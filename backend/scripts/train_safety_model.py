"""
Smart Shield - ML Model Training Script
Trains the safety scoring model on real crime and feedback data
"""

import sys
import os
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import User, Delivery, SafetyFeedback, CrimeData, SafeZone

def collect_training_data(db: Session):
    """Collect and prepare training data from database"""
    print("\n📊 Collecting training data from database...")
    
    # Get all completed deliveries with safety scores
    deliveries = db.query(Delivery).filter(
        Delivery.status == 'completed',
        Delivery.safety_score.isnot(None)
    ).all()
    
    print(f"  Found {len(deliveries)} completed deliveries with safety scores")
    
    if len(deliveries) < 20:
        print("  ⚠️  Not enough data for training. Need at least 20 completed deliveries.")
        print("  💡 Run seed_database.py first to generate training data.")
        return None
    
    # Get feedback data
    feedback_records = db.query(SafetyFeedback).all()
    print(f"  Found {len(feedback_records)} feedback records")
    
    # Get crime data
    crime_records = db.query(CrimeData).all()
    print(f"  Found {len(crime_records)} crime records")
    
    # Get safe zones
    safe_zones = db.query(SafeZone).all()
    print(f"  Found {len(safe_zones)} safe zones")
    
    # Prepare training data
    training_data = []
    
    for delivery in deliveries:
        # Calculate features
        features = calculate_safety_features(
            delivery, 
            crime_records, 
            safe_zones, 
            feedback_records
        )
        
        if features:
            features['safety_score'] = delivery.safety_score
            training_data.append(features)
    
    if not training_data:
        print("  ❌ Could not generate training features")
        return None
    
    df = pd.DataFrame(training_data)
    print(f"\n✅ Generated {len(df)} training samples with {len(df.columns)-1} features")
    print(f"\nFeatures: {', '.join(df.columns[:-1])}")
    
    return df

def calculate_safety_features(delivery, crime_records, safe_zones, feedback_records):
    """Calculate safety features for a delivery location"""
    
    # Helper function to calculate distance
    def haversine_distance(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    loc = delivery.dropoff_location
    lat, lon = loc['lat'], loc['lng']
    
    # 1. Crime density (crimes within 5km)
    nearby_crimes = [
        c for c in crime_records 
        if haversine_distance(lat, lon, c.location['latitude'], c.location['longitude']) < 5
    ]
    crime_density = len(nearby_crimes)
    
    # 2. Crime severity score (using risk score from DB)
    crime_severity = sum(c.crime_risk_score or 0 for c in nearby_crimes) / max(len(nearby_crimes), 1)
    
    # 3. Distance to nearest safe zone
    if safe_zones:
        distances_to_safe_zones = [
            haversine_distance(lat, lon, sz.location['latitude'], sz.location['longitude'])
            for sz in safe_zones
        ]
        distance_to_safe_zone = min(distances_to_safe_zones)
    else:
        distance_to_safe_zone = 10  # Default 10km
    
    # 4. Number of safe zones nearby (within 2km)
    safe_zones_nearby = sum(
        1 for sz in safe_zones 
        if haversine_distance(lat, lon, sz.location['latitude'], sz.location['longitude']) < 2
    )
    
    # 5. Historical feedback for area
    # 5. Historical feedback for area (Simplified for now as feedback lacks location in this version)
    nearby_feedback = [] # Placeholder
    
    if nearby_feedback:
        avg_feedback_rating = sum(f.rating for f in nearby_feedback) / len(nearby_feedback)
        pct_felt_safe = 80 # Default
        pct_adequate_lighting = 80 # Default
    else:
        avg_feedback_rating = 3.5  # Neutral default
        pct_felt_safe = 50
        pct_adequate_lighting = 50
    
    # 6. Time of day factor
    if delivery.delivered_at:
        hour = delivery.delivered_at.hour
        is_night = 1 if (hour >= 20 or hour <= 6) else 0
        is_peak_crime_time = 1 if (hour >= 22 or hour <= 4) else 0
    else:
        is_night = 0
        is_peak_crime_time = 0
    
    # 7. Area type estimation (urban vs suburban vs rural)
    # Higher crime density = more urban
    area_urbanization = min(crime_density / 10, 1)  # Normalize to 0-1
    
    return {
        'crime_density': crime_density,
        'crime_severity': crime_severity,
        'distance_to_safe_zone_km': distance_to_safe_zone,
        'safe_zones_nearby': safe_zones_nearby,
        'avg_feedback_rating': avg_feedback_rating,
        'pct_felt_safe': pct_felt_safe,
        'pct_adequate_lighting': pct_adequate_lighting,
        'is_night': is_night,
        'is_peak_crime_time': is_peak_crime_time,
        'area_urbanization': area_urbanization,
        'delivery_distance_km': delivery.estimated_distance or 10,
        'delivery_duration_min': delivery.estimated_duration or 30,
    }

def train_model(df):
    """Train Random Forest model"""
    print("\n🤖 Training Random Forest model...")
    
    # Separate features and target
    X = df.drop('safety_score', axis=1)
    y = df['safety_score']
    
    print(f"\n  Features shape: {X.shape}")
    print(f"  Target shape: {y.shape}")
    print(f"  Target range: {y.min():.1f} - {y.max():.1f}")
    print(f"  Target mean: {y.mean():.1f}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # Train model
    print("\n  🔄 Training model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("  ✓ Model trained!")
    
    # Evaluate on training set
    y_train_pred = model.predict(X_train)
    train_mse = mean_squared_error(y_train, y_train_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    
    print("\n  📈 Training Performance:")
    print(f"    MSE: {train_mse:.2f}")
    print(f"    MAE: {train_mae:.2f}")
    print(f"    R² Score: {train_r2:.4f}")
    
    # Evaluate on test set
    y_test_pred = model.predict(X_test)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    
    print("\n  📊 Test Performance:")
    print(f"    MSE: {test_mse:.2f}")
    print(f"    MAE: {test_mae:.2f}")
    print(f"    R² Score: {test_r2:.4f}")
    
    # Cross-validation
    print("\n  🔄 Running 5-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    print(f"    CV R² Scores: {cv_scores}")
    print(f"    Mean CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    print("\n  🎯 Feature Importance:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(5).iterrows():
        print(f"    {row['feature']:.<35} {row['importance']:.4f}")
    
    return model, X.columns.tolist(), {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_mae': test_mae,
        'cv_mean_r2': cv_scores.mean(),
        'cv_std_r2': cv_scores.std()
    }

def save_model(model, feature_names, metrics):
    """Save trained model to disk"""
    print("\n💾 Saving model...")
    
    models_dir = backend_path / 'api' / 'models' / 'saved_models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = models_dir / 'safety_scorer_rf.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  ✓ Model saved to: {model_path}")
    
    # Save feature names
    features_path = models_dir / 'safety_scorer_features.pkl'
    with open(features_path, 'wb') as f:
        pickle.dump(feature_names, f)
    print(f"  ✓ Features saved to: {features_path}")
    
    # Save metrics
    metrics_path = models_dir / 'safety_scorer_metrics.pkl'
    with open(metrics_path, 'wb') as f:
        pickle.dump(metrics, f)
    print(f"  ✓ Metrics saved to: {metrics_path}")
    
    return model_path

def test_model_inference(model, feature_names):
    """Test model with sample data"""
    print("\n🧪 Testing model inference...")
    
    # Create sample data (safe area during day)
    sample_safe = pd.DataFrame([{
        'crime_density': 2,
        'crime_severity': 1.2,
        'distance_to_safe_zone_km': 0.5,
        'safe_zones_nearby': 3,
        'avg_feedback_rating': 4.5,
        'pct_felt_safe': 90,
        'pct_adequate_lighting': 85,
        'is_night': 0,
        'is_peak_crime_time': 0,
        'area_urbanization': 0.7,
        'delivery_distance_km': 5,
        'delivery_duration_min': 20,
    }])[feature_names]
    
    # Create sample data (unsafe area at night)
    sample_unsafe = pd.DataFrame([{
        'crime_density': 15,
        'crime_severity': 2.8,
        'distance_to_safe_zone_km': 5,
        'safe_zones_nearby': 0,
        'avg_feedback_rating': 2.5,
        'pct_felt_safe': 30,
        'pct_adequate_lighting': 20,
        'is_night': 1,
        'is_peak_crime_time': 1,
        'area_urbanization': 0.9,
        'delivery_distance_km': 15,
        'delivery_duration_min': 45,
    }])[feature_names]
    
    safe_score = model.predict(sample_safe)[0]
    unsafe_score = model.predict(sample_unsafe)[0]
    
    print(f"\n  Safe area (day): {safe_score:.1f}/100")
    print(f"  Unsafe area (night): {unsafe_score:.1f}/100")
    print(f"  Difference: {safe_score - unsafe_score:.1f} points")
    
    if safe_score > unsafe_score:
        print("\n  ✅ Model correctly identifies safer vs. unsafe routes!")
    else:
        print("\n  ⚠️  Model may need more training data or feature engineering")

def main():
    """Main training function"""
    print("\n" + "="*60)
    print("🤖 SMART SHIELD ML MODEL TRAINING")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Collect training data
        df = collect_training_data(db)
        
        if df is None or len(df) < 20:
            print("\n❌ Not enough training data. Please run seed_database.py first.")
            return
        
        # Train model
        model, feature_names, metrics = train_model(df)
        
        # Save model
        model_path = save_model(model, feature_names, metrics)
        
        # Test inference
        test_model_inference(model, feature_names)
        
        # Summary
        print("\n" + "="*60)
        print("✅ MODEL TRAINING COMPLETED")
        print("="*60)
        print(f"\n  Model Performance:")
        print(f"    Test R² Score: {metrics['test_r2']:.4f}")
        print(f"    Test MAE: {metrics['test_mae']:.2f} points")
        print(f"    CV Mean R²: {metrics['cv_mean_r2']:.4f}")
        
        if metrics['test_r2'] > 0.7:
            print("\n  🎉 Excellent! Model has good predictive power.")
        elif metrics['test_r2'] > 0.5:
            print("\n  👍 Good! Model can make useful predictions.")
        else:
            print("\n  ⚠️  Model needs improvement. Consider more data or features.")
        
        print(f"\n  Model saved to: {model_path}")
        print("\n  💡 Next Steps:")
        print("    1. Test the API: python scripts/test_ml_integration.py")
        print("    2. Run the backend: uvicorn api.main:app --reload")
        print("    3. Test route optimization with ML: POST /api/v1/delivery/optimize")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
