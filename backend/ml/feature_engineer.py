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
        self._crimes_cache = None
    
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
                try:
                    delivery_time = datetime.fromisoformat(delivery_time_str.replace('Z', '+00:00'))
                except ValueError:
                    delivery_time = datetime.utcnow()
            else:
                delivery_time = datetime.utcnow()
                
            feature_vector['hour'] = delivery_time.hour
            feature_vector['day_of_week'] = delivery_time.weekday()
            feature_vector['is_weekend'] = int(delivery_time.weekday() >= 5)
            feature_vector['is_peak_hour'] = int(delivery_time.hour in [8, 9, 17, 18, 19])
            feature_vector['is_night'] = int(delivery_time.hour < 6 or delivery_time.hour > 20)
            
            # === DISTANCE FEATURES ===
            dist_meters = segment.get('distance', 0)
            feature_vector['segment_distance'] = dist_meters
            feature_vector['distance_km'] = dist_meters / 1000.0
            
            total_dist = route_data.get('total_distance', 0)
            feature_vector['total_distance'] = total_dist
            feature_vector['segment_ratio'] = dist_meters / total_dist if total_dist > 0 else 0
            
            # Additional features required by TimePredictor
            feature_vector['num_turns'] = len(segment.get('instructions', []))
            feature_vector['num_traffic_lights'] = max(1, int(dist_meters / 1000)) # Approximation
            
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
    
    def _get_db(self):
        if self.db:
            return self.db
        from database.database import SessionLocal
        return SessionLocal()

    def _get_safety_scores(self, start_lat, start_lng, end_lat, end_lng):
        """Get safety scores from crime data"""
        midpoint_lat = (start_lat + end_lat) / 2
        midpoint_lng = (start_lng + end_lng) / 2
        
        # Cache crime data to avoid repeated DB hits
        if self._crimes_cache is None:
            db = self._get_db()
            try:
                self._crimes_cache = db.query(CrimeData).all()
                # Extract essential data to avoid keeping DB objects if possible
                self._crimes_cache = [
                    {
                        'lat': c.location.get('latitude') if c.location else 0,
                        'lng': c.location.get('longitude') if c.location else 0,
                        'risk': c.crime_risk_score or 50.0,
                        'murder': c.murder_count or 0,
                        'harassment': c.sexual_harassment_count or 0,
                        'accident': c.road_accident_count or 0
                    }
                    for c in self._crimes_cache
                ]
            except Exception as e:
                print(f"Error fetching crimes: {e}")
                self._crimes_cache = []
            finally:
                if not self.db:
                    db.close()
        
        nearby_crimes = []
        for crime in self._crimes_cache:
            # Simple Euclidean distance approximation (0.1 degree ~ 11km)
            dist = ((crime['lat'] - midpoint_lat)**2 + (crime['lng'] - midpoint_lng)**2)**0.5
            if dist < 0.1:
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
            weight = 1.0 / (1.0 + dist * 100) # Stronger distance weighting
            total_crime_score += crime['risk'] * weight
            murder_risk += crime['murder'] * weight
            harassment_risk += crime['harassment'] * weight
            accident_risk += crime['accident'] * weight
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
            traffic_level = 2 # High
        elif hour in [10, 11, 12, 13, 14, 15, 16] and day_of_week < 5:
            traffic_level = 1 # Medium
        else:
            traffic_level = 0 # Low
        
        return {
            'traffic_level': traffic_level,
            'expected_delay': traffic_level * (segment.get('distance', 0) / 1000.0) * 2  # 2 min per km delay
        }
    
    def _get_weather_features(self, lat, lng):
        """Extract weather-related features"""
        return {
            'temperature': 30.0,
            'precipitation': 0.0,
            'wind_speed': 10.0,
            'visibility': 10.0,
            'weather_hazard_score': 0.1,
            'weather_hazard': 0.1 # Alias for some model versions
        }
    
    def _get_historical_features(self, segment):
        """Extract historical performance features"""
        start_lat = segment.get('start_lat', 0)
        start_lng = segment.get('start_lng', 0)
        
        # We should also cache historical deliveries or optimize this query
        db = self._get_db()
        try:
            # Query with small range to use index if available
            nearby_deliveries = db.query(HistoricalDelivery).filter(
                HistoricalDelivery.origin_lat.between(start_lat - 0.05, start_lat + 0.05),
                HistoricalDelivery.origin_lng.between(start_lng - 0.05, start_lng + 0.05)
            ).limit(20).all() # Reduce limit for speed
            
            if not nearby_deliveries:
                return {
                    'avg_delivery_time': (segment.get('distance', 0) / 1000.0) * 3,  # 3 min per km
                    'success_rate': 0.95,
                    'avg_fuel_consumption': (segment.get('distance', 0) / 1000.0) * 0.05
                }
            
            avg_time = np.mean([d.delivery_time_minutes for d in nearby_deliveries])
            success_rate = np.mean([d.success for d in nearby_deliveries])
            avg_fuel = np.mean([d.fuel_consumed for d in nearby_deliveries if d.fuel_consumed is not None]) or 0.1
            
            return {
                'avg_delivery_time': float(avg_time),
                'success_rate': float(success_rate),
                'avg_fuel_consumption': float(avg_fuel)
            }
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {
                'avg_delivery_time': (segment.get('distance', 0) / 1000.0) * 3,
                'success_rate': 0.95,
                'avg_fuel_consumption': 0.1
            }
        finally:
            if not self.db:
                db.close()
