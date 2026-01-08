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
from api.services.crime_data import CrimeDataService
from loguru import logger
import json
from geopy.distance import distance



class SafetyScorer:
    """AI-powered safety scoring for routes."""
    
    def __init__(self, crime_service: Optional[CrimeDataService] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.weights = settings.SAFETY_WEIGHTS
        self.crime_service = crime_service or CrimeDataService()
        self.police_stations = self._load_police_stations()
        self.hospitals = self._load_hospitals()
        self._initialize_model()

    def _load_police_stations(self) -> List[Dict]:
        """Load police stations from JSON file."""
        try:
            # Try absolute path first, then relative to this file
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "police_stations.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading police stations: {e}")
        return []

    def _load_hospitals(self) -> List[Dict]:
        """Load hospitals from JSON file."""
        try:
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "hospitals.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading hospitals: {e}")
        return []

    
    def _initialize_model(self):
        """Initialize or load the safety scoring model."""
        model_path = settings.SAFETY_MODEL_PATH
        model_dir = Path(model_path).parent
        
        # Create directory if it doesn't exist
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing model
        if Path(model_path).exists() and Path(settings.SAFETY_SCALER_PATH).exists():
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(settings.SAFETY_SCALER_PATH)
                
                # Check for feature mismatch (we now have 7 features)
                if hasattr(self.model, "n_features_in_") and self.model.n_features_in_ != 7:
                    raise ValueError(f"Model expects {self.model.n_features_in_} features, but we need 7")
                    
                logger.info("Loaded existing safety scoring model and scaler")
            except Exception as e:
                logger.warning(f"Could not load model or scaler: {e}, creating new ones")
                self._train_initial_model()
        else:
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial model with synthetic data."""
        # Generate synthetic training data based on heuristics
        n_samples = 1000
        np.random.seed(42)
        
        # Feature: [crime_rate, lighting_score, patrol_density, traffic_density, hour_of_day, police_proximity, hospital_proximity]
        X = np.random.rand(n_samples, 7)
        # Normalize features to realistic ranges
        X[:, 0] = X[:, 0] * 10  # crime incidents (0-10)
        X[:, 1] = X[:, 1] * 100  # lighting score (0-100)
        X[:, 2] = X[:, 2] * 100  # patrol density (0-100)
        X[:, 3] = X[:, 3] * 100  # traffic density (0-100)
        X[:, 4] = X[:, 4] * 24  # hour (0-24)
        X[:, 5] = X[:, 5] * 100 # police proximity score (0-100)
        X[:, 6] = X[:, 6] * 100 # hospital proximity score (0-100)
        
        # Target: safety score (0-100)
        # Lower crime, higher lighting, higher patrol, closer police/hospital = higher safety
        y = (
            50 - X[:, 0] * 2.5 +  # crime impact
            X[:, 1] * 0.15 +  # lighting contribution
            X[:, 2] * 0.15 +  # patrol contribution
            (50 - X[:, 3]) * 0.1 +  # lower traffic is safer
            np.sin(X[:, 4] * np.pi / 12) * 10 + # time of day effect
            X[:, 5] * 0.15 + # police proximity contribution
            X[:, 6] * 0.10 # hospital proximity contribution
        )
        y = np.clip(y, 0, 100)
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_scaled, y)
        
        # Save model and scaler
        try:
            joblib.dump(self.model, settings.SAFETY_MODEL_PATH)
            joblib.dump(self.scaler, settings.SAFETY_SCALER_PATH)
            logger.info("Trained and saved new safety scoring model and scaler")
        except Exception as e:
            logger.warning(f"Could not save model or scaler: {e}")
    
    def _get_location_features(
        self,
        coord: Coordinate,
        time_of_day: str = "day",
        weather_data: Optional[Dict] = None
    ) -> np.ndarray:
        """Extract features for a location using real crime data."""
        # Get real crime data from Tamil Nadu crime dataset
        crime_score = self.crime_service.get_crime_score(coord)
        crime_data = self.crime_service.get_crime_data_for_location(coord)
        
        # Convert crime score to crime rate (0-10 scale)
        crime_rate = crime_score / 10.0
        
        # Lighting score (varies by location and time)
        hour_map = {"day": 12, "evening": 18, "night": 22}
        hour = hour_map.get(time_of_day, 12)
        
        # Adjust lighting based on time of day
        if hour < 6 or hour > 20:
            lighting_score = 30 + np.random.rand() * 20  # Low at night
        elif hour < 8 or hour > 18:
            lighting_score = 50 + np.random.rand() * 30  # Medium at dawn/dusk
        else:
            lighting_score = 70 + np.random.rand() * 30  # High during day
        
        # Patrol density (higher in high-crime areas)
        if crime_score > 50:
            patrol_density = 60 + np.random.rand() * 30  # More patrols in high-crime areas
        else:
            patrol_density = 40 + np.random.rand() * 40
        
        # Traffic density (mock for now, could use real traffic data)
        traffic_density = 30 + np.random.rand() * 50
        
        # Weather hazard impact (if provided)
        weather_hazard = 0
        if weather_data:
            weather_hazard = weather_data.get("hazard_score", 0) / 10.0  # Scale to 0-10
            
        # Police Proximity
        police_proximity = self._calculate_police_proximity(coord)

        # Hospital Proximity
        hospital_proximity = self._calculate_hospital_proximity(coord)
        
        # Increase importance of hospitals at night
        if hour < 6 or hour > 20:
            hospital_proximity *= 1.2
            hospital_proximity = min(100.0, hospital_proximity)
        
        return np.array([
            crime_rate,
            lighting_score,
            patrol_density,
            traffic_density,
            hour,
            police_proximity,  # Feature 5 (0-100)
            hospital_proximity, # Feature 6 (0-100)
            weather_hazard    # Extra feature, not in main model X
        ])

    def _calculate_hospital_proximity(self, coord: Coordinate) -> float:
        """Calculate proximity score to nearest 24/7 hospital (0-100)."""
        if not self.hospitals:
            return 50.0 # Default if no data
            
        min_dist_km = float('inf')
        
        for hospital in self.hospitals:
            try:
                dist = distance(
                    (coord.latitude, coord.longitude),
                    (hospital['latitude'], hospital['longitude'])
                ).km
                if dist < min_dist_km:
                    min_dist_km = dist
            except Exception:
                continue
                
        # Proximity score: 100 if < 500m, decays to 0 at 10km
        if min_dist_km == float('inf'):
            return 0.0
            
        score = 100 * np.exp(-0.4 * min_dist_km) # Slightly slower decay than police
        return min(100.0, max(0.0, score))

    def _calculate_police_proximity(self, coord: Coordinate) -> float:
        """Calculate proximity score to nearest police station (0-100)."""
        if not self.police_stations:
            return 50.0 # Default if no data
            
        min_dist_km = float('inf')
        
        for station in self.police_stations:
            try:
                dist = distance(
                    (coord.latitude, coord.longitude),
                    (station['latitude'], station['longitude'])
                ).km
                if dist < min_dist_km:
                    min_dist_km = dist
            except Exception:
                continue
                
        # Proximity score: 100 if < 500m, decays to 0 at 10km
        # Logic: score = 100 * exp(-0.5 * dist_km)
        # 1km -> 60, 2km -> 36, 5km -> 8
        if min_dist_km == float('inf'):
            return 0.0
            
        score = 100 * np.exp(-0.5 * min_dist_km)
        return min(100.0, max(0.0, score))
    
    def score_location(
        self,
        coord: Coordinate,
        time_of_day: str = "day",
        rider_info: Optional[Dict] = None,
        weather_data: Optional[Dict] = None
    ) -> Tuple[float, List[Dict]]:
        """Score a single location for safety.
        
        Returns:
            Tuple of (overall_score, factors_list)
        """
        features = self._get_location_features(coord, time_of_day, weather_data)
        # Expected model features: 7
        if features.shape[0] >= 7:
            # Taking first 7 features for the model
             features_for_model = features[:7].reshape(1, -1)
        else:
             # Fallback
             features_for_model = np.zeros((1, 7))
             features_for_model[0, :min(len(features), 7)] = features[:7]
        
        features_scaled = self.scaler.transform(features_for_model)
        
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
        
        # Get crime data for detailed description
        crime_data = self.crime_service.get_crime_data_for_location(coord)
        crime_score = self.crime_service.get_crime_score(coord)
        
        # Create factors breakdown
        factors = [
            {
                "factor": "crime_overall",
                "score": max(0, 100 - crime_score),
                "weight": self.weights["crime"],
                "description": f"Overall Crime Risk: {crime_data.get('district', 'Unknown')}"
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
            },
            {
                "factor": "police_proximity",
                "score": features[5],
                "weight": 0.15,
                "description": "Proximity to Police Station"
            },
            {
                "factor": "hospital_proximity",
                "score": features[6],
                "weight": 0.15,
                "description": "Proximity to 24/7 Medical Services"
            }
        ]
        
        # Add specific high-risk warnings based on raw counts
        if crime_data.get('theft', 0) > 100:
             factors.append({
                "factor": "theft_risk",
                "score": 40, # Low safety score specifically for theft
                "weight": 0.1,
                "description": "High Theft Zone"
            })
            
        if crime_data.get('sexual_harassment', 0) > 20:
             factors.append({
                "factor": "harassment_risk",
                "score": 20, # Very low safety score
                "weight": 0.2,
                "description": "High Harassment Risk Area"
            })
        
        # Add weather factor if available
        if weather_data:
            weather_hazard = weather_data.get("hazard_score", 0)
            factors.append({
                "factor": "weather",
                "score": max(0, 100 - weather_hazard),
                "weight": 0.15,  # Additional weight for weather
                "description": f"Weather hazard: {', '.join(weather_data.get('hazard_conditions', []))}"
            })
            # Adjust base score based on weather
            base_score -= weather_hazard * 0.2
        
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

