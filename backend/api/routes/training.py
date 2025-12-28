from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict

from database.database import get_db
from database.models import HistoricalDelivery
from ml.time_predictor import DeliveryTimePredictor
from ml.safety_classifier import SafetyClassifier
from loguru import logger

router = APIRouter()

@router.post("/training/retrain")
async def retrain_models(db: Session = Depends(get_db)):
    """Trigger retraining of ML models based on historical data."""
    try:
        # Fetch historical data
        history = db.query(HistoricalDelivery).all()
        if len(history) < 10:
            return {"status": "skipped", "reason": "Insufficient data for retraining (need at least 10 samples)"}
        
        # Prepare data (simplified feature extraction for the retraining endpoint)
        data_list = []
        for h in history:
            data_list.append({
                'hour': h.time_of_day,
                'day_of_week': h.day_of_week,
                'segment_distance': h.distance_km,
                'total_distance': h.distance_km,
                'crime_score': 50.0, # This should ideally be extracted from CrimeData for the history locations
                'traffic_level': 0.5 if h.traffic.get('level') == 'medium' else 0.8,
                'delivery_time': h.delivery_time_minutes,
                'safe': 1 if h.success else 0
            })
        
        df = pd.DataFrame(data_list)
        X = df.drop(['delivery_time', 'safe'], axis=1)
        
        # Retrain Time Predictor
        time_predictor = DeliveryTimePredictor()
        time_res = time_predictor.train(X, df['delivery_time'])
        
        # Retrain Safety Classifier
        safety_classifier = SafetyClassifier()
        safety_res = safety_classifier.train(X, df['safe'])
        
        return {
            "status": "success",
            "time_model": time_res,
            "safety_model": safety_res
        }
    except Exception as e:
        logger.error(f"Error during retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))
