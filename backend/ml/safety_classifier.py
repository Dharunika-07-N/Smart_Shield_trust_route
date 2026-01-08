from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path

class SafetyClassifier:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_dir = os.path.join(Path(__file__).parent.parent, "models")
        self.model_path = os.path.join(self.model_dir, "safety_classifier_rf.pkl")
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Train Random Forest classifier for safety prediction
        y should be binary: 1 = safe, 0 = unsafe
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        
        self.model.fit(X_scaled, y)
        
        # Evaluate
        accuracy = self.model.score(X_scaled, y)
        print(f"✅ Safety Classifier Training Complete. Accuracy: {accuracy:.4f}")
        
        self.save_model()
        
        return {'accuracy': float(accuracy)}
    
    def predict_safety_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict safety probability (0-1)
        Returns probability of route being safe
        """
        if self.model is None:
            if not self.load_model():
                # Train with synthetic data if no model exists
                print("⚠️ No trained model found, creating initial model with synthetic data...")
                self._train_synthetic_model()
        
        try:
            # Ensure scaler is fitted
            if not hasattr(self.scaler, 'mean_'):
                print("⚠️ Scaler not fitted, refitting...")
                self.scaler.fit(X)
            
            X_scaled = self.scaler.transform(X)
            # Get probability of safe class (index 1)
            safety_proba = self.model.predict_proba(X_scaled)[:, 1]
            # Convert to 0-100 scale
            return safety_proba * 100
        except Exception as e:
            print(f"❌ Error in safety prediction: {e}")
            # Return fallback scores
            return np.array([70.0] * len(X))
    
    def _train_synthetic_model(self):
        """Train model with synthetic data if no real data available"""
        print("🔧 Training SafetyClassifier with synthetic data...")
        
        # Generate synthetic training data
        n_samples = 500
        np.random.seed(42)
        
        # Features: [crime_rate, lighting, patrol, traffic, hour, police_proximity, hospital_proximity]
        X = pd.DataFrame({
            'crime_rate': np.random.rand(n_samples) * 10,
            'lighting': np.random.rand(n_samples) * 100,
            'patrol': np.random.rand(n_samples) * 100,
            'traffic': np.random.rand(n_samples) * 100,
            'hour': np.random.randint(0, 24, n_samples),
            'police_proximity': np.random.rand(n_samples) * 100,
            'hospital_proximity': np.random.rand(n_samples) * 100
        })
        
        # Target: 1 = safe, 0 = unsafe
        # Safe if: low crime, high lighting, high patrol, close to police/hospital
        y = ((X['crime_rate'] < 5) & 
             ((X['lighting'] > 50) | (X['hospital_proximity'] > 60)) & 
             (X['patrol'] > 40) & 
             ((X['police_proximity'] > 30) | (X['hospital_proximity'] > 40))).astype(int)
        
        self.train(X, y)
    
    def save_model(self):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, self.model_path)
        print(f"✅ Safety model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model"""
        if not os.path.exists(self.model_path):
            return False
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        return True
