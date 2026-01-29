from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import pandas as pd
import sqlite3
from datetime import datetime
import logging
import os
from pathlib import Path

# Fix relative imports by using absolute imports assuming 'backend' is root or in path
from ml.safety_classifier_enhanced import EnhancedSafetyClassifier
from ml.time_predictor_enhanced import EnhancedTimePredictor
from ml.rl_agent_enhanced import EnhancedSARSAAgent
from database.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class RetrainingRequest(BaseModel):
    model_name: Optional[str] = None  # "safety", "time", "rl", or None for all
    tune_hyperparameters: bool = False
    min_samples: int = 100
    version: Optional[str] = None


class RetrainingResponse(BaseModel):
    status: str
    message: str
    models_trained: List[str]
    metrics: Dict
    timestamp: str


def fetch_training_data(db_path: str = None) -> Dict[str, pd.DataFrame]:
    """Fetch training data from database"""
    if db_path is None:
         # Assuming database is in backend/smartshield.db or backend/database/smartshield.db based on project structure
         # Let's check typical location
         db_path = os.path.join(Path(__file__).parent.parent.parent, "smartshield.db")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Check if tables exist first to avoid crashing on new DB
        cursor = conn.cursor()
        
        # Safety data
        try:
            safety_query = """
            SELECT 
                crime_rate,
                lighting,
                patrol_frequency,
                traffic_density,
                police_proximity,
                hospital_proximity,
                timestamp,
                safety_score,
                safety_class
            FROM route_segments
            WHERE safety_score IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10000
            """
            safety_df = pd.read_sql_query(safety_query, conn)
        except Exception:
            safety_df = pd.DataFrame() # Return empty if table doesn't exist
        
        # Time prediction data
        try:
            time_query = """
            SELECT 
                delivery_id,
                route_distance,
                traffic_level,
                timestamp,
                actual_time,
                estimated_time,
                weather_condition,
                num_stops,
                vehicle_type,
                success
            FROM deliveries
            WHERE actual_time IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10000
            """
            time_df = pd.read_sql_query(time_query, conn)
        except Exception:
            time_df = pd.DataFrame()

        # RL training data
        try:
            rl_query = """
            SELECT 
                delivery_id,
                start_latitude,
                start_longitude,
                end_latitude,
                end_longitude,
                timestamp,
                route_choice,
                actual_time,
                estimated_time,
                safety_score,
                success,
                actual_distance,
                estimated_distance,
                traffic_level,
                weather
            FROM delivery_outcomes
            ORDER BY timestamp DESC
            LIMIT 10000
            """
            rl_df = pd.read_sql_query(rl_query, conn)
        except Exception:
            rl_df = pd.DataFrame()
        
        return {
            'safety': safety_df,
            'time': time_df,
            'rl': rl_df
        }
    
    finally:
        conn.close()


def retrain_models_background(
    model_name: Optional[str],
    tune_hyperparameters: bool,
    min_samples: int,
    version: Optional[str]
):
    """Background task for retraining"""
    try:
        logger.info(f"Starting retraining for: {model_name or 'all models'}")
        
        # Fetch data
        data = fetch_training_data()
        
        results = {
            'models_trained': [],
            'metrics': {},
            'errors': []
        }
        
        # Train Safety Classifier
        if model_name in [None, 'safety']:
            safety_df = data['safety']
            
            if len(safety_df) < min_samples:
                # If insufficient real data, try training with synthetic data for initialization if needed
                # But typically we prefer logging warning
                results['errors'].append(
                    f"Safety: Insufficient data ({len(safety_df)} < {min_samples})"
                )
            else:
                try:
                    logger.info("Training Safety Classifier...")
                    classifier = EnhancedSafetyClassifier()
                    
                    X, y = classifier.prepare_data(safety_df, 'safety_class')
                    
                    metrics = classifier.train(
                        X, y, 
                        tune_hyperparameters=tune_hyperparameters
                    )
                    
                    classifier.save_model(version=version)
                    
                    results['models_trained'].append('safety')
                    results['metrics']['safety'] = metrics
                    
                    logger.info("Safety Classifier trained successfully")
                    
                except Exception as e:
                    logger.error(f"Safety Classifier training failed: {e}")
                    results['errors'].append(f"Safety: {str(e)}")
        
        # Train Time Predictor
        if model_name in [None, 'time']:
            time_df = data['time']
            
            if len(time_df) < min_samples:
                results['errors'].append(
                    f"Time: Insufficient data ({len(time_df)} < {min_samples})"
                )
            else:
                try:
                    logger.info("Training Time Predictor...")
                    predictor = EnhancedTimePredictor()
                    
                    X, y, features = predictor.prepare_data(time_df, 'actual_time')
                    
                    metrics = predictor.train(
                        X, y,
                        tune_hyperparameters=tune_hyperparameters
                    )
                    
                    predictor.save_model(version=version)
                    
                    results['models_trained'].append('time')
                    results['metrics']['time'] = metrics
                    
                    logger.info("Time Predictor trained successfully")
                    
                except Exception as e:
                    logger.error(f"Time Predictor training failed: {e}")
                    results['errors'].append(f"Time: {str(e)}")
        
        # Train RL Agent
        if model_name in [None, 'rl']:
            rl_df = data['rl']
            
            if len(rl_df) < min_samples:
                results['errors'].append(
                    f"RL: Insufficient data ({len(rl_df)} < {min_samples})"
                )
            else:
                try:
                    logger.info("Training RL Agent...")
                    agent = EnhancedSARSAAgent()
                    
                    metrics = agent.train_from_history(rl_df)
                    
                    agent.save_model(version=version)
                    
                    results['models_trained'].append('rl')
                    results['metrics']['rl'] = metrics
                    
                    logger.info("RL Agent trained successfully")
                    
                except Exception as e:
                    logger.error(f"RL Agent training failed: {e}")
                    results['errors'].append(f"RL: {str(e)}")
        
        logger.info(f"Retraining complete. Trained: {results['models_trained']}")
        
        # Store results in database
        db_path = os.path.join(Path(__file__).parent.parent.parent, "smartshield.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure training_history table exists (simple check)
        cursor.execute("CREATE TABLE IF NOT EXISTS training_history (timestamp TEXT, models_trained TEXT, metrics TEXT, errors TEXT, version TEXT)")
        
        cursor.execute("""
        INSERT INTO training_history 
        (timestamp, models_trained, metrics, errors, version)
        VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            ','.join(results['models_trained']),
            str(results['metrics']),
            ','.join(results['errors']),
            version or 'auto'
        ))
        
        conn.commit()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        # Don't re-raise in background task usually, just log
        return None


@router.post("/training/retrain", response_model=RetrainingResponse)
async def retrain_models(
    request: RetrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger model retraining
    
    - **model_name**: Specific model to train ("safety", "time", "rl") or None for all
    - **tune_hyperparameters**: Whether to perform hyperparameter tuning
    - **min_samples**: Minimum samples required for training
    - **version**: Optional version tag for saved models
    """
    # Add to background tasks
    background_tasks.add_task(
        retrain_models_background,
        request.model_name,
        request.tune_hyperparameters,
        request.min_samples,
        request.version
    )
    
    return RetrainingResponse(
        status="started",
        message="Model retraining started in background",
        models_trained=[],
        metrics={},
        timestamp=datetime.now().isoformat()
    )


@router.get("/training/status")
async def get_training_status():
    """Get latest training status"""
    db_path = os.path.join(Path(__file__).parent.parent.parent, "smartshield.db")
    conn = sqlite3.connect(db_path)
    
    try:
        query = """
        SELECT timestamp, models_trained, metrics, errors, version
        FROM training_history
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            row = cursor.fetchone()
            
            if not row:
                return {"status": "No training history found"}
            
            return {
                "timestamp": row[0],
                "models_trained": row[1].split(',') if row[1] else [],
                "metrics": eval(row[2]) if row[2] else {},
                "errors": row[3].split(',') if row[3] else [],
                "version": row[4]
            }
        except sqlite3.OperationalError:
             return {"status": "No training history found (table missing)"}
        
    finally:
        conn.close()


@router.get("/training/history")
async def get_training_history(limit: int = 10):
    """Get training history"""
    db_path = os.path.join(Path(__file__).parent.parent.parent, "smartshield.db")
    conn = sqlite3.connect(db_path)
    
    try:
        try:
            df = pd.read_sql_query(
                f"SELECT * FROM training_history ORDER BY timestamp DESC LIMIT {limit}",
                conn
            )
            return df.to_dict('records')
        except Exception:
             return []
        
    finally:
        conn.close()


@router.get("/training/model-info/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        if model_name == 'safety':
            classifier = EnhancedSafetyClassifier()
            if not classifier.load_model():
                 raise HTTPException(status_code=404, detail="Safety model not trained yet")
            
            # Helper to safely serialize numpy/pandas types
            def safe_serialize(obj):
                 if hasattr(obj, 'to_dict'):
                      return obj.to_dict('records')
                 return obj

            return {
                "model": "Safety Classifier",
                "type": "Random Forest",
                "features": classifier.feature_names,
                "classes": classifier.safety_classes,
                "feature_importance": safe_serialize(classifier.get_feature_importance()),
                "training_history": classifier.training_history[-5:] if classifier.training_history else []
            }
            
        elif model_name == 'time':
            predictor = EnhancedTimePredictor()
            if not predictor.load_model():
                 raise HTTPException(status_code=404, detail="Time predictor not trained yet")
            
            def safe_serialize(obj):
                 if hasattr(obj, 'to_dict'):
                      return obj.to_dict('records')
                 return obj

            return {
                "model": "Time Predictor",
                "type": "XGBoost Regressor",
                "features": predictor.feature_names,
                "feature_importance": safe_serialize(predictor.feature_importance_),
                "training_history": predictor.training_history[-5:] if predictor.training_history else []
            }
            
        elif model_name == 'rl':
            agent = EnhancedSARSAAgent()
            if not agent.load_model():
               raise HTTPException(status_code=404, detail="RL Agent not trained yet")
            
            return {
                "model": "SARSA RL Agent",
                "type": "Reinforcement Learning",
                "actions": agent.actions,
                "reward_weights": agent.reward_weights,
                "performance": agent.get_performance_summary(),
                "training_history": agent.training_history[-5:] if agent.training_history else []
            }
            
        else:
            raise HTTPException(status_code=404, detail="Model not found")
            
    except HTTPException:
         raise
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
