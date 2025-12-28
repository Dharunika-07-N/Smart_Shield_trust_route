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
                # Fallback score
                return np.array([75.0] * len(X))
        
        try:
            X_scaled = self.scaler.transform(X)
            # Get probability of safe class (index 1)
            safety_proba = self.model.predict_proba(X_scaled)[:, 1]
            # Convert to 0-100 scale
            return safety_proba * 100
        except Exception as e:
            print(f"❌ Error in safety prediction: {e}")
            return np.array([70.0] * len(X))
    
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
