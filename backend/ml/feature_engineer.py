import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import cast, func
from geoalchemy2.functions import ST_Distance
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import CrimeData, HistoricalDelivery

class FeatureEngineer:
    def __init__(self, db: Session):
        self.db = db
    
    def extract_features(self, route_data: Dict) -> pd.DataFrame:
        """
        Extract comprehensive features for ML models
        """
        features = []
        
        for segment in route_data.get('segments', []):
            feature_vector = {}
            
            # === TEMPORAL FEATURES ===
            delivery_time_str = route_data.get('delivery_time')
            if delivery_time_str:
                delivery_time = datetime.fromisoformat(delivery_time_str.replace('Z', '+00:00'))
            else:
                delivery_time = datetime.utcnow()
                
            feature_vector['hour'] = delivery_time.hour
            feature_vector['day_of_week'] = delivery_time.weekday()
            feature_vector['is_weekend'] = int(delivery_time.weekday() >= 5)
            feature_vector['is_peak_hour'] = int(delivery_time.hour in [8, 9, 17, 18, 19])
            feature_vector['is_night'] = int(delivery_time.hour < 6 or delivery_time.hour > 20)
            
            # === DISTANCE FEATURES ===
            feature_vector['segment_distance'] = segment.get('distance', 0)
            total_dist = route_data.get('total_distance', 0)
            feature_vector['total_distance'] = total_dist
            feature_vector['segment_ratio'] = segment.get('distance', 0) / total_dist if total_dist > 0 else 0
            
            # === SAFETY FEATURES ===
            safety_scores = self._get_safety_scores(
                segment.get('start_lat', 0), 
                segment.get('start_lng', 0),
                segment.get('end_lat', 0),
                segment.get('end_lng', 0)
            )
            feature_vector.update(safety_scores)
            
            # === TRAFFIC FEATURES ===
            traffic_features = self._get_traffic_features(segment, delivery_time)
            feature_vector.update(traffic_features)
            
            # === WEATHER FEATURES ===
            weather_features = self._get_weather_features(
                segment.get('start_lat', 0), 
                segment.get('start_lng', 0)
            )
            feature_vector.update(weather_features)
            
            # === HISTORICAL FEATURES ===
            hist_features = self._get_historical_features(segment)
            feature_vector.update(hist_features)
            
            features.append(feature_vector)
        
        return pd.DataFrame(features)
    
    def _get_safety_scores(self, start_lat, start_lng, end_lat, end_lng):
        """Get safety scores from crime data"""
        midpoint_lat = (start_lat + end_lat) / 2
        midpoint_lng = (start_lng + end_lng) / 2
        
        # Simple distance check for SQLite-friendly query
        # Fetch all for now and calculate distance in Python (fine for few districts)
        all_crimes = self.db.query(CrimeData).all()
        
        nearby_crimes = []
        for crime in all_crimes:
            loc = crime.location
            if not loc: continue
            
            # Simple Euclidean distance approximation
            dist = ((loc['latitude'] - midpoint_lat)**2 + (loc['longitude'] - midpoint_lng)**2)**0.5
            if dist < 0.1: # Roughly 10km
                nearby_crimes.append((crime, dist))
        
        if not nearby_crimes:
            return {
                'crime_score': 50.0,
                'murder_risk': 0.0,
                'sexual_harassment_risk': 0.0,
                'accident_risk': 0.0
            }
        
        # Weighted average
        total_crime_score = 0
        murder_risk = 0
        harassment_risk = 0
        accident_risk = 0
        total_weight = 0
        
        for crime, dist in nearby_crimes:
            weight = 1.0 / (1.0 + dist * 10)
            total_crime_score += crime.crime_risk_score * weight
            murder_risk += crime.murder_count * weight
            harassment_risk += crime.sexual_harassment_count * weight
            accident_risk += crime.road_accident_count * weight
            total_weight += weight
        
        return {
            'crime_score': total_crime_score / total_weight if total_weight > 0 else 50.0,
            'murder_risk': murder_risk / total_weight if total_weight > 0 else 0.0,
            'sexual_harassment_risk': harassment_risk / total_weight if total_weight > 0 else 0.0,
            'accident_risk': accident_risk / total_weight if total_weight > 0 else 0.0
        }
    
    def _get_traffic_features(self, segment, delivery_time):
        """Extract traffic-related features"""
        hour = delivery_time.hour
        day_of_week = delivery_time.weekday()
        
        # Peak hour traffic
        if hour in [8, 9, 17, 18, 19] and day_of_week < 5:
            traffic_level = 0.8
        elif hour in [10, 11, 12, 13, 14, 15, 16] and day_of_week < 5:
            traffic_level = 0.5
        else:
            traffic_level = 0.2
        
        return {
            'traffic_level': traffic_level,
            'expected_delay': traffic_level * segment.get('distance', 0) * 2  # 2 min per km delay
        }
    
    def _get_weather_features(self, lat, lng):
        """Extract weather-related features"""
        return {
            'temperature': 30.0,
            'precipitation': 0.0,
            'wind_speed': 10.0,
            'visibility': 10.0,
            'weather_hazard_score': 0.1
        }
    
    def _get_historical_features(self, segment):
        """Extract historical performance features"""
        start_lat = segment.get('start_lat', 0)
        start_lng = segment.get('start_lng', 0)
        
        nearby_deliveries = self.db.query(HistoricalDelivery).filter(
            HistoricalDelivery.origin_lat.between(start_lat - 0.1, start_lat + 0.1),
            HistoricalDelivery.origin_lng.between(start_lng - 0.1, start_lng + 0.1)
        ).limit(50).all()
        
        if not nearby_deliveries:
            return {
                'avg_delivery_time': segment.get('distance', 0) * 3,  # 3 min per km
                'success_rate': 0.95,
                'avg_fuel_consumption': segment.get('distance', 0) * 0.05
            }
        
        avg_time = np.mean([d.delivery_time_minutes for d in nearby_deliveries])
        success_rate = np.mean([d.success for d in nearby_deliveries])
        avg_fuel = np.mean([d.fuel_consumed for d in nearby_deliveries if d.fuel_consumed])
        
        return {
            'avg_delivery_time': float(avg_time),
            'success_rate': float(success_rate),
            'avg_fuel_consumption': float(avg_fuel)
        }
