import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.time_predictor_enhanced import EnhancedTimePredictor
from loguru import logger

def train():
    rides_path = "data/rides"
    if not os.path.exists(rides_path):
        logger.error(f"Rides data not found at {rides_path}")
        return

    logger.info("Loading real ride history for training...")
    # Read the data - it's a CSV despite lacking .csv extension
    try:
        df = pd.read_csv(rides_path)
    except Exception as e:
        logger.error(f"Failed to read rides file: {e}")
        return

    # Basic cleaning to match EnhancedTimePredictor expectations
    logger.info(f"Loaded {len(df)} rows. Mapping headers...")
    
    # Mapping your CSV columns to what the model expects:
    # CSV: distance -> route_distance
    # CSV: duration -> actual_time (Target)
    if 'distance' in df.columns:
        df['route_distance'] = df['distance']
    if 'duration' in df.columns:
        df['actual_time'] = df['duration']
    
    # Fill in some defaults for missing features in this specific CSV
    df['traffic_level'] = 0.5 # Neutral fallback
    df['weather_condition'] = 'clear'
    
    # Initialize Predictor
    predictor = EnhancedTimePredictor()
    
    logger.info("Preparing data for XGBoost...")
    X, y, features = predictor.prepare_data(df, target_column='actual_time')
    
    if X is None or len(X) == 0:
        logger.error("No valid data points found for training.")
        return

    logger.info(f"Starting training on {len(X)} samples with {len(features)} features...")
    metrics = predictor.train(X, y, tune_hyperparameters=False)
    
    logger.info(f"Training Complete! Test MAE: {metrics['test']['mae']:.2f} mins")
    
    model_file = predictor.save_model(version="real_data_v1")
    logger.info(f"Model saved to {model_file}")

if __name__ == "__main__":
    train()
