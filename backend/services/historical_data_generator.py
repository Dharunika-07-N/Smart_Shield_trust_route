import random
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import HistoricalDelivery

class HistoricalDataGenerator:
    """
    Generate synthetic historical delivery data for training
    Based on realistic patterns for Tamil Nadu delivery services
    """
    
    def __init__(self, db):
        self.db = db
        
        # Key delivery hubs in Tamil Nadu
        self.hubs = {
            "Chennai Central": (13.0827, 80.2707),
            "Coimbatore Junction": (11.0168, 76.9558),
            "Madurai Town": (9.9252, 78.1198),
            "Tiruppur Market": (11.1085, 77.3411),
            "Salem City": (11.6643, 78.1460),
        }
        
        # Common delivery destinations (offset from hubs)
        self.delivery_patterns = [
            (0.05, 0.05),  # 5-6 km radius
            (0.10, 0.10),  # 10-12 km radius
            (0.15, 0.15),  # 15-18 km radius
        ]
    
    def generate_training_data(self, num_samples=1000):
        """Generate historical delivery data"""
        
        records = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_samples):
            # Random hub
            hub_name = random.choice(list(self.hubs.keys()))
            origin_lat, origin_lng = self.hubs[hub_name]
            
            # Random destination (within delivery radius)
            lat_offset, lng_offset = random.choice(self.delivery_patterns)
            dest_lat = origin_lat + random.uniform(-lat_offset, lat_offset)
            dest_lng = origin_lng + random.uniform(-lng_offset, lng_offset)
            
            # Calculate distance (Haversine)
            distance_km = self._haversine_distance(
                origin_lat, origin_lng, dest_lat, dest_lng
            )
            
            # Simulate delivery time based on distance + traffic + time of day
            hour = random.randint(6, 22)
            day_of_week = random.randint(0, 6)
            
            base_time = distance_km * 3  # 3 min per km base
            traffic_factor = 1.5 if hour in [8, 9, 17, 18, 19] else 1.0
            delivery_time = base_time * traffic_factor + random.uniform(-5, 10)
            
            # Ensure delivery time is positive
            delivery_time = max(delivery_time, 2.0)
            
            # Success rate (higher for experienced routes)
            success = random.random() > 0.05  # 95% success rate
            
            # Weather simulation
            weather_condition = random.choices(
                ["clear", "cloudy", "rain", "heavy_rain"],
                weights=[0.6, 0.2, 0.15, 0.05]
            )[0]
            
            weather = {
                "condition": weather_condition,
                "temperature": random.randint(25, 38),
                "wind_speed": random.randint(5, 25),
                "visibility": 10 if weather_condition == "clear" else 5
            }
            
            # Traffic simulation
            traffic = {
                "level": "high" if hour in [8, 9, 17, 18, 19] else "medium",
                "congestion_score": random.uniform(0.3, 0.9)
            }
            
            record = HistoricalDelivery(
                delivery_id=f"DEL-{i:06d}-{random.getrandbits(16)}",
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                destination_lat=dest_lat,
                destination_lng=dest_lng,
                delivery_time_minutes=delivery_time,
                distance_km=distance_km,
                fuel_consumed=distance_km * 0.05,  # 0.05L per km
                success=success,
                weather=weather,
                traffic=traffic,
                time_of_day=hour,
                day_of_week=day_of_week,
                completed_at=start_date + timedelta(
                    days=random.randint(0, 365),
                    hours=hour
                )
            )
            
            records.append(record)
        
        # Bulk insert
        try:
            self.db.bulk_save_objects(records)
            self.db.commit()
            print(f"✅ Generated {num_samples} historical delivery records")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error generating training data: {e}")
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
