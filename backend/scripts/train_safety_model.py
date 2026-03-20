
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.safety_classifier_enhanced import EnhancedSafetyClassifier
from loguru import logger

def train():
    db_path = "smartshield.db"
    if not os.path.exists(db_path):
        db_path = Path(__file__).parent.parent / "smartshield.db"
        if not db_path.exists():
            logger.error(f"Database not found.")
            return

    # Use SQLAlchemy to read the feedback tables
    engine = create_engine(f"sqlite:///{db_path}")
    
    logger.info("Fetching User Feedback for training...")
    try:
        sf_df = pd.read_sql("SELECT * FROM safety_feedback", engine)
        
        # Mapping ratings 1-5 to classes 0-4
        if not sf_df.empty:
            sf_df['safety_class'] = (sf_df['rating'] - 1).clip(0, 4)
            # Need to extract lat/lng from JSON location
            import json
            sf_df['lat'] = sf_df['location'].apply(lambda x: json.loads(x)['lat'] if isinstance(x, str) else x.get('lat'))
            sf_df['lng'] = sf_df['location'].apply(lambda x: json.loads(x)['lng'] if isinstance(x, str) else x.get('lng'))
    except Exception as e:
        logger.error(f"DB Read failed: {e}")
        sf_df = pd.DataFrame()

    if sf_df.empty:
        logger.warning("No feedback data found in DB. Falling back to hazard-based synthetic data.")
        
        # Warm start logic: generate 1000 samples based on hazards
        synthetic_rows = []
        for _ in range(1000):
            visibility = np.random.beta(5, 2)
            lighting = np.random.beta(5, 2)
            patrol = np.random.beta(3, 3)
            traffic = np.random.uniform(0, 1)
            police = np.random.uniform(0, 1)
            hospital = np.random.uniform(0, 1)
            
            # Higher visibility/lighting = safer
            score = visibility * 0.3 + lighting * 0.3 + patrol * 0.2 + (1-traffic) * 0.1 + police * 0.1
            s_class = int(np.round(score * 4))
            s_class = max(0, min(4, s_class))
            
            synthetic_rows.append({
                'visibility_score': visibility,
                'lighting': lighting,
                'patrol_frequency': patrol,
                'hospital_proximity': hospital,
                'police_proximity': police,
                'traffic_density': traffic,
                'time_of_day': 3 if np.random.rand() > 0.7 else 1,
                'safety_class': s_class,
                'timestamp': datetime.now().isoformat()
            })
        training_df = pd.DataFrame(synthetic_rows)
    else:
        # Use real feedback
        training_df = sf_df[['safety_class', 'lat', 'lng']]
        training_df['timestamp'] = sf_df['date_submitted']
        
        # Synthetic hazards for existing feedback entries
        training_df['visibility_score'] = 0.8
        training_df['lighting'] = 0.7
        training_df['patrol_frequency'] = 0.5
        training_df['police_proximity'] = 0.5
        training_df['hospital_proximity'] = 0.5
        training_df['traffic_density'] = 0.3

    # Initialize Classifier
    classifier = EnhancedSafetyClassifier()
    
    logger.info(f"Training on {len(training_df)} samples...")
    X, y = classifier.prepare_data(training_df, target_column='safety_class')
    
    metrics = classifier.train(X, y, tune_hyperparameters=False)
    logger.info(f"Training Complete! Test F1: {metrics.get('f1_weighted', 0):.2f}")
    
    model_file = classifier.save_model(version="hazard_v1")
    logger.info(f"Enhanced Safety Model saved to {model_file}")

if __name__ == "__main__":
    train()
