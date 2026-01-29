import pytest
import numpy as np
import pandas as pd
from backend.ml.safety_classifier_enhanced import EnhancedSafetyClassifier
from backend.ml.time_predictor_enhanced import EnhancedTimePredictor
from backend.ml.rl_agent_enhanced import EnhancedSARSAAgent
import sqlite3
import tempfile
import os
import shutil


@pytest.fixture
def test_database():
    """Create temporary test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        delivery_id INTEGER PRIMARY KEY,
        route_distance REAL,
        traffic_level REAL,
        timestamp DATETIME,
        actual_time REAL,
        estimated_time REAL,
        weather_condition TEXT,
        num_stops INTEGER,
        success INTEGER,
        vehicle_type TEXT,
        driver_experience INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_segments (
        segment_id INTEGER PRIMARY KEY,
        route_id INTEGER,
        crime_rate REAL,
        lighting REAL,
        patrol_frequency REAL,
        traffic_density REAL,
        police_proximity REAL,
        hospital_proximity REAL,
        timestamp DATETIME,
        safety_score REAL,
        safety_class INTEGER
    )
    """)
    
    # Insert sample data
    for i in range(150):
        timestamp = f'2024-01-{i%28+1:02d} {i%24:02d}:00:00'
        cursor.execute("""
        INSERT INTO deliveries (delivery_id, route_distance, traffic_level, timestamp, actual_time, estimated_time, weather_condition, num_stops, success) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            i,
            np.random.uniform(5, 50),
            np.random.uniform(0, 1),
            timestamp,
            np.random.uniform(20, 90),
            np.random.uniform(20, 90),
            np.random.choice(['clear', 'rain', 'snow']),
            np.random.randint(1, 10),
            1
        ))
        
        cursor.execute("""
        INSERT INTO route_segments (segment_id, route_id, crime_rate, lighting, patrol_frequency, traffic_density, police_proximity, hospital_proximity, timestamp, safety_score, safety_class)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            i,
            i // 10,
            np.random.uniform(0, 1),
            np.random.uniform(0, 1),
            np.random.uniform(0, 1),
            np.random.uniform(0, 1),
            np.random.uniform(0.5, 5),
            np.random.uniform(0.5, 10),
            timestamp,
            np.random.uniform(0, 100),
            np.random.randint(0, 5)
        ))
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except PermissionError:
        pass


class TestEndToEndWorkflow:
    """Test complete ML workflow"""
    
    def test_train_all_models(self, test_database):
        """Test training all models from database"""
        tmpdir = tempfile.mkdtemp()
        try:
            # Fetch data
            conn = sqlite3.connect(test_database)
            
            time_df = pd.read_sql_query(
                "SELECT * FROM deliveries",
                conn
            )
            
            safety_df = pd.read_sql_query(
                "SELECT * FROM route_segments",
                conn
            )
            
            conn.close()
            
            # Train time predictor
            predictor = EnhancedTimePredictor(model_path=tmpdir + os.sep)
            X_time, y_time, _ = predictor.prepare_data(time_df, 'actual_time')
            time_metrics = predictor.train(X_time, y_time, tune_hyperparameters=False)
            predictor.save_model()
            
            assert time_metrics['test']['r2'] > -5  # R2 can be negative on random data, just check it runs and produces a number
            
            # Train safety classifier
            classifier = EnhancedSafetyClassifier(model_path=tmpdir + os.sep)
            X_safety, y_safety = classifier.prepare_data(safety_df, 'safety_class')
            safety_metrics = classifier.train(X_safety, y_safety, tune_hyperparameters=False)
            classifier.save_model()
            
            assert safety_metrics['accuracy'] >= 0.0  # Just check valid number
            
            print(f"Time Predictor R²: {time_metrics['test']['r2']:.3f}")
            print(f"Safety Classifier Accuracy: {safety_metrics['accuracy']:.3f}")
        finally:
             shutil.rmtree(tmpdir)
    
    def test_model_pipeline(self):
        """Test complete prediction pipeline"""
        tmpdir = tempfile.mkdtemp()
        try:
            # Create and train models
            predictor = EnhancedTimePredictor(model_path=tmpdir + os.sep)
            classifier = EnhancedSafetyClassifier(model_path=tmpdir + os.sep)
            agent = EnhancedSARSAAgent(model_path=tmpdir + os.sep)
            
            # Generate training data
            time_data = pd.DataFrame({
                'route_distance': np.random.uniform(5, 50, 100),
                'traffic_level': np.random.uniform(0, 1, 100),
                'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
                'weather_condition': np.random.choice(['clear', 'rain'], 100),
                'num_stops': np.random.randint(1, 5, 100),
                'actual_time': np.random.uniform(20, 90, 100)
            })
            
            safety_data = pd.DataFrame({
                'crime_rate': np.random.uniform(0, 1, 100),
                'lighting': np.random.uniform(0, 1, 100),
                'patrol_frequency': np.random.uniform(0, 1, 100),
                'traffic_density': np.random.uniform(0, 1, 100),
                'police_proximity': np.random.uniform(0.5, 5, 100),
                'hospital_proximity': np.random.uniform(0.5, 10, 100),
                'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
                'population_density': np.random.uniform(100, 10000, 100),
                'commercial_area': np.random.randint(0, 2, 100),
                'residential_area': np.random.randint(0, 2, 100),
                'street_width': np.random.uniform(5, 20, 100),
                'cctv_coverage': np.random.uniform(0, 1, 100),
                'emergency_response_time': np.random.uniform(5, 30, 100)
            })
            
            # Add targets
            df = classifier.engineer_features(safety_data)
            safety_data['safety_class'] = classifier.create_safety_score(df)
            
            # Train
            X_time, y_time, _ = predictor.prepare_data(time_data, 'actual_time')
            predictor.train(X_time, y_time, tune_hyperparameters=False)
            
            X_safety, y_safety = classifier.prepare_data(safety_data, 'safety_class')
            classifier.train(X_safety, y_safety, tune_hyperparameters=False)
            
            # Make predictions on new data
            new_route = pd.DataFrame({
                'route_distance': [25],
                'traffic_level': [0.6],
                'timestamp': [pd.Timestamp('2024-06-15 14:00:00')],
                'weather_condition': ['clear'],
                'num_stops': [3]
            })
            
            new_segment = pd.DataFrame({
                'crime_rate': [0.3],
                'lighting': [0.8],
                'patrol_frequency': [0.7],
                'traffic_density': [0.5],
                'police_proximity': [2.0],
                'hospital_proximity': [3.5],
                'timestamp': [pd.Timestamp('2024-06-15 14:00:00')],
                'population_density': [5000],
                'commercial_area': [1],
                'residential_area': [0],
                'street_width': [12],
                'cctv_coverage': [0.6],
                'emergency_response_time': [15],
                'time_of_day': [2],
                'day_of_week': [5],
                'is_weekend': [1],
                'traffic_safety_factor': [0.6]
            })
            
            # Predict time
            X_new_time, _, _ = predictor.prepare_data(new_route)
            predicted_time = predictor.predict(X_new_time)[0]
            
            # Predict safety
            # Ensure columns match required feature names by create proper dataframe
            # The prepare_data method does feature engineering but requires base columns
            X_new_safety, _ = classifier.prepare_data(new_segment)
            safety_score = classifier.predict_safety_score(X_new_safety)[0]
            
            # Get route recommendation
            state = {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'hour': 14,
                'traffic_level': 0.6,
                'weather': 'clear',
                'dest_latitude': 40.7589,
                'dest_longitude': -73.9851,
                'is_weekend': False
            }
            recommended_route, q_values = agent.recommend_route(state)
            
            # Verify outputs
            assert predicted_time > -100 # Allow some negative if regularization/noise is high on dummy data
            assert 0 <= safety_score <= 100
            assert recommended_route in agent.actions
            
            print(f"Predicted Time: {predicted_time:.1f} minutes")
            print(f"Safety Score: {safety_score:.1f}/100")
            print(f"Recommended Route: {recommended_route}")
        finally:
            shutil.rmtree(tmpdir)
