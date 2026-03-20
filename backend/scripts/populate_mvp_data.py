
import os
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import SessionLocal, engine, Base
from database.models import SafeZone, User, CrowdsourcedAlert

def populate_mvp_data():
    # Ensure all tables exist in the DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[RUN] Starting MVP Data Population...")

        # 1. Add Police Stations from JSON
        police_stations_path = Path(__file__).parent.parent / "data" / "police_stations.json"
        if police_stations_path.exists():
            with open(police_stations_path, 'r') as f:
                stations = json.load(f)
                count = 0
                for s in stations:
                    exists = db.query(SafeZone).filter(SafeZone.name == s['name']).first()
                    if not exists:
                        zone = SafeZone(
                            id=str(uuid.uuid4()),
                            zone_type="police_station",
                            name=s['name'],
                            location={"lat": s['latitude'], "lng": s['longitude']},
                            address=s.get('address', ''),
                            phone=s.get('phone', ''),
                            is_24hr=True,
                            safety_score=95.0
                        )
                        db.add(zone)
                        count += 1
                print(f"[OK] Added {count} Police Stations as Safe Zones.")

        # 2. Add Synthetic Safe Zones (Shops & Well-lit areas)
        additional_safe_zones = [
            {
                "name": "Apollo Pharmacy 24/7 - RS Puram",
                "type": "shop_24hr",
                "lat": 11.0125, "lng": 76.9535,
                "address": "DB Road, RS Puram, Coimbatore",
                "is_24hr": True,
                "score": 85.0
            },
            {
                "name": "Well-Lit Main Road Segment - Avinashi Road",
                "type": "well_lit_area",
                "lat": 11.0250, "lng": 77.0000,
                "address": "Avinashi Road, Coimbatore",
                "is_24hr": True,
                "score": 90.0
            }
        ]

        for sz in additional_safe_zones:
            exists = db.query(SafeZone).filter(SafeZone.name == sz['name']).first()
            if not exists:
                zone = SafeZone(
                    id=str(uuid.uuid4()),
                    zone_type=sz['type'],
                    name=sz['name'],
                    location={"lat": sz['lat'], "lng": sz['lng']},
                    address=sz['address'],
                    is_24hr=sz['is_24hr'],
                    safety_score=sz['score']
                )
                db.add(zone)
        print(f"[OK] Added {len(additional_safe_zones)} high-traffic Safe Zones.")

        # 3. Generate Synthetic Hazard Alerts (Low Visibility / Traffic)
        hazard_zones = [
            {
                "type": "road_obstruction",
                "lat": 10.9950, "lng": 76.9610,
                "desc": "Ongoing construction, low visibility at night"
            },
            {
                "type": "poor_lighting",
                "lat": 11.0180, "lng": 76.9680,
                "desc": "Street lights non-functional in this stretch"
            }
        ]

        for hz in hazard_zones:
            alert = CrowdsourcedAlert(
                rider_id="system_init",
                service_type="Admin",
                location={"lat": hz['lat'], "lng": hz['lng']},
                is_faster=False,
                has_traffic_issues=True,
                created_at=datetime.utcnow()
            )
            db.add(alert)
        print(f"[OK] Generated {len(hazard_zones)} synthetic Hazard Zones for demo.")

        db.commit()
        print("[DONE] MVP Population Complete!")

    except Exception as e:
        db.rollback()
        print(f"[ERR] Error during population: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_mvp_data()

