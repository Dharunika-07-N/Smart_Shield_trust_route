"""Seed the database with real-world feedback data for the safety model."""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.database import SessionLocal
from database.models import SafetyFeedback, Route
from loguru import logger
import random
import uuid
from datetime import datetime, timedelta

def seed_feedback():
    """Seed feedback entries based on Tamil Nadu coordinates."""
    db = SessionLocal()
    try:
        # Major Tamil Nadu hubs for seeding
        hubs = [
            {"name": "Chennai Central", "lat": 13.0827, "lng": 80.2707},
            {"name": "Coimbatore Gandhipuram", "lat": 11.0168, "lng": 76.9558},
            {"name": "Madurai Meenakshi", "lat": 9.9252, "lng": 78.1198},
            {"name": "Trichy Junction", "lat": 10.7905, "lng": 78.7047},
            {"name": "Salem Bus Stand", "lat": 11.6643, "lng": 78.1460},
        ]
        
        feedback_types = ["general", "lighting", "security", "traffic"]
        incident_types = [None, "low_lighting", "catcalling", "heavy_traffic", "unpaved_road"]
        
        count = 0
        for hub in hubs:
            # Create 10-15 feedback points around each hub
            for _ in range(random.randint(10, 15)):
                lat = hub["lat"] + random.uniform(-0.05, 0.05)
                lng = hub["lng"] + random.uniform(-0.05, 0.05)
                
                # Biased rating: hub centers are generally safer but might have traffic
                dist_factor = abs(lat - hub["lat"]) + abs(lng - hub["lng"])
                base_rating = 5 if dist_factor < 0.02 else 3
                rating = max(1, min(5, base_rating + random.randint(-1, 1)))
                
                fb = SafetyFeedback(
                    id=str(uuid.uuid4()),
                    route_id=f"ROUTE_SEED_{random.randint(100, 999)}",
                    rider_id=f"RIDER_{random.randint(1, 50)}",
                    feedback_type=random.choice(feedback_types),
                    rating=rating,
                    location={"latitude": lat, "longitude": lng},
                    comments=f"Automated seed feedback for {hub['name']} area.",
                    incident_type=random.choice(incident_types) if rating < 3 else None,
                    time_of_day=random.choice(["day", "evening", "night"]),
                    date_submitted=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.add(fb)
                count += 1
        
        db.commit()
        logger.info(f"Successfully seeded {count} safety feedback records.")
        return True
    except Exception as e:
        logger.error(f"Error seeding feedback: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    seed_feedback()
