import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from pathlib import Path

class DeliveryTimePredictor:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.model_dir = os.path.join(Path(__file__).parent.parent, "models")
        self.model_path = os.path.join(self.model_dir, "time_predictor_xgb.pkl")
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Train XGBoost model to predict delivery time
        """
        self.feature_columns = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 7,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'random_state': 42
        }
        
        self.model = xgb.XGBRegressor(**params)
        
        # Train
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Time Predictor Training Complete. MAE: {mae:.2f} min, R²: {r2:.4f}")
        
        # Save model
        self.save_model()
        
        return {
            'mae': float(mae),
            'r2': float(r2),
            'feature_importance': self.get_feature_importance()
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict delivery time for new routes"""
        if self.model is None:
            self.load_model()
        
        # Ensure feature columns match
        X = X[self.feature_columns]
        
        return self.model.predict(X)
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if self.model is None:
            return {}
        
        importance = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, [float(i) for i in importance]))
        
        # Sort by importance
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def save_model(self):
        """Save trained model to disk"""
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, self.model_path)
        print(f"✅ Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        if not os.path.exists(self.model_path):
            print(f"⚠️ Model file not found: {self.model_path}. Returning dummy model.")
            return False
            
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        return True
