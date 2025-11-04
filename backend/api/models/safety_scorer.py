"""AI Safety Scoring Model."""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings
from api.schemas.delivery import Coordinate
from loguru import logger


class SafetyScorer:
    """AI-powered safety scoring for routes."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.weights = settings.SAFETY_WEIGHTS
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the safety scoring model."""
        model_path = settings.SAFETY_MODEL_PATH
        model_dir = Path(model_path).parent
        
        # Create directory if it doesn't exist
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing model
        if Path(model_path).exists():
            try:
                self.model = joblib.load(model_path)
                logger.info("Loaded existing safety scoring model")
            except Exception as e:
                logger.warning(f"Could not load model: {e}, creating new model")
                self._train_initial_model()
        else:
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial model with synthetic data."""
        # Generate synthetic training data based on heuristics
        n_samples = 1000
        np.random.seed(42)
        
        # Feature: [crime_rate, lighting_score, patrol_density, traffic_density, hour_of_day]
        X = np.random.rand(n_samples, 5)
        # Normalize features to realistic ranges
        X[:, 0] = X[:, 0] * 10  # crime incidents (0-10)
        X[:, 1] = X[:, 1] * 100  # lighting score (0-100)
        X[:, 2] = X[:, 2] * 100  # patrol density (0-100)
        X[:, 3] = X[:, 3] * 100  # traffic density (0-100)
        X[:, 4] = X[:, 4] * 24  # hour (0-24)
        
        # Target: safety score (0-100)
        # Lower crime, higher lighting, higher patrol = higher safety
        y = (
            50 - X[:, 0] * 2.5 +  # crime impact
            X[:, 1] * 0.15 +  # lighting contribution
            X[:, 2] * 0.15 +  # patrol contribution
            (50 - X[:, 3]) * 0.1 +  # lower traffic is safer
            np.sin(X[:, 4] * np.pi / 12) * 10  # time of day effect
        )
        y = np.clip(y, 0, 100)
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_scaled, y)
        
        # Save model
        try:
            joblib.dump(self.model, settings.SAFETY_MODEL_PATH)
            logger.info("Trained and saved new safety scoring model")
        except Exception as e:
            logger.warning(f"Could not save model: {e}")
    
    def _get_location_features(
        self,
        coord: Coordinate,
        time_of_day: str = "day"
    ) -> np.ndarray:
        """Extract features for a location."""
        # Simulate real-world feature extraction
        # In production, this would fetch from external APIs (SafeGraph, etc.)
        
        # Mock features - replace with actual API calls
        np.random.seed(int(coord.latitude * 1000 + coord.longitude))
        
        # Crime rate (low for demo, higher in some areas)
        crime_rate = np.random.rand() * 3
        
        # Lighting score (varies by location)
        lighting_score = 60 + np.random.rand() * 30
        
        # Patrol density (varies by area)
        patrol_density = 40 + np.random.rand() * 40
        
        # Traffic density
        traffic_density = 30 + np.random.rand() * 50
        
        # Time of day adjustment
        hour_map = {"day": 12, "evening": 18, "night": 22}
        hour = hour_map.get(time_of_day, 12)
        
        return np.array([
            crime_rate,
            lighting_score,
            patrol_density,
            traffic_density,
            hour
        ])
    
    def score_location(
        self,
        coord: Coordinate,
        time_of_day: str = "day",
        rider_info: Optional[Dict] = None
    ) -> Tuple[float, List[Dict]]:
        """Score a single location for safety.
        
        Returns:
            Tuple of (overall_score, factors_list)
        """
        features = self._get_location_features(coord, time_of_day)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get model prediction
        base_score = self.model.predict(features_scaled)[0]
        
        # Apply gender-specific adjustments if needed
        if rider_info and rider_info.get("gender") == "female":
            # Women riders prefer higher lighting and patrol presence
            if features[1] < 50:  # Low lighting
                base_score -= 10
            if features[2] < 50:  # Low patrol
                base_score -= 10
        
        base_score = np.clip(base_score, 0, 100)
        
        # Create factors breakdown
        factors = [
            {
                "factor": "crime",
                "score": max(0, 100 - features[0] * 10),
                "weight": self.weights["crime"],
                "description": f"Crime rate: {features[0]:.1f}"
            },
            {
                "factor": "lighting",
                "score": features[1],
                "weight": self.weights["lighting"],
                "description": f"Lighting conditions: {features[1]:.1f}/100"
            },
            {
                "factor": "patrol_presence",
                "score": features[2],
                "weight": self.weights["patrol_presence"],
                "description": f"Patrol density: {features[2]:.1f}/100"
            },
            {
                "factor": "traffic",
                "score": max(0, 100 - features[3]),
                "weight": self.weights["traffic"],
                "description": f"Traffic conditions: {features[3]:.1f}/100"
            }
        ]
        
        return base_score, factors
    
    def score_route(
        self,
        coordinates: List[Coordinate],
        time_of_day: str = "day",
        rider_info: Optional[Dict] = None
    ) -> Dict:
        """Score an entire route for safety.
        
        Returns:
            Dictionary with route safety metrics
        """
        segment_scores = []
        total_score = 0
        
        for coord in coordinates:
            score, factors = self.score_location(coord, time_of_day, rider_info)
            segment_scores.append({
                "coordinates": coord,
                "overall_score": score,
                "factors": factors
            })
            total_score += score
        
        avg_score = total_score / len(coordinates) if coordinates else 0
        
        # Risk level classification
        if avg_score >= 75:
            risk_level = "low"
        elif avg_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "route_safety_score": avg_score,
            "average_score": avg_score,
            "segment_scores": segment_scores,
            "risk_level": risk_level,
            "improvement_suggestions": self._get_improvement_suggestions(avg_score)
        }
    
    def _get_improvement_suggestions(self, score: float) -> List[str]:
        """Get suggestions for improving route safety."""
        suggestions = []
        
        if score < 50:
            suggestions.append("Consider daytime deliveries for better safety")
            suggestions.append("Choose routes with better lighting")
            suggestions.append("Prefer areas with frequent patrol presence")
        elif score < 75:
            suggestions.append("Route is moderately safe")
            suggestions.append("Consider real-time safety updates")
        
        return suggestions
    
    def retrain_with_feedback(self, feedback_data: List[Dict]):
        """Retrain model with new feedback data."""
        # This would process user feedback and retrain the model
        # For now, just log the intent
        logger.info(f"Retraining model with {len(feedback_data)} feedback samples")
        # In production, would aggregate feedback by location and update model

