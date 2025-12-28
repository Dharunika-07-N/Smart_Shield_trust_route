import sys
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import SessionLocal, init_db
from services.crime_data_loader import CrimeDataLoader
from services.historical_data_generator import HistoricalDataGenerator
from ml.feature_engineer import FeatureEngineer
from ml.time_predictor import DeliveryTimePredictor
from ml.safety_classifier import SafetyClassifier

async def renovate():
    print("🚀 Starting Smart Shield Trust Route Renovation...")
    
    # 1. Initialize Database
    print("\n--- Phase 1: Database Initialization ---")
    await init_db()
    
    db = SessionLocal()
    try:
        # 2. Load Crime Data
        print("\n--- Phase 2: Data Integration ---")
        loader = CrimeDataLoader(db)
        loader.load_tamil_nadu_crime_data()
        
        # 3. Generate Historical Data
        generator = HistoricalDataGenerator(db)
        generator.generate_training_data(num_samples=2000)
        
        # 4. Train Models
        print("\n--- Phase 3: ML Model Training ---")
        from database.models import HistoricalDelivery
        history = db.query(HistoricalDelivery).all()
        
        if not history:
            print("❌ No historical data found for training.")
            return

        # Prepare simple training data from generated history
        data_list = []
        for h in history:
            data_list.append({
                'hour': h.time_of_day,
                'day_of_week': h.day_of_week,
                'segment_distance': h.distance_km,
                'total_distance': h.distance_km, # simplified
                'crime_score': 50.0, # dummy for training setup
                'traffic_level': 0.5 if h.traffic.get('level') == 'medium' else 0.8,
                'delivery_time': h.delivery_time_minutes,
                'safe': 1 if h.success else 0
            })
        
        df = pd.DataFrame(data_list)
        X = df.drop(['delivery_time', 'safe'], axis=1)
        
        # Train Time Predictor
        time_predictor = DeliveryTimePredictor()
        time_predictor.train(X, df['delivery_time'])
        
        # Train Safety Classifier
        safety_classifier = SafetyClassifier()
        safety_classifier.train(X, df['safe'])
        
        print("\n✅ Renovation Phase Complete!")
        print("💡 The backend is now equipped with ML models and Tamil Nadu crime data.")
        
    except Exception as e:
        print(f"❌ Renovation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(renovate())
