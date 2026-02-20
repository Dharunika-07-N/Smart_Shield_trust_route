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
from database.models import SafeZone, CrimeData, User

def populate_mvp_data():
    db = SessionLocal()
    try:
        print("🚀 Starting MVP Data Population...")

        # 1. Clear existing MVP-specific data to avoid duplicates (optional, but good for re-running)
        # db.query(SafeZone).delete()
        # db.query(CrimeData).filter(CrimeData.radius_km < 5.0).delete() # Remove previous hotspots

        # 2. Add Police Stations from JSON
        police_stations_path = Path(__file__).parent.parent / "data" / "police_stations.json"
        if police_stations_path.exists():
            with open(police_stations_path, 'r') as f:
                stations = json.load(f)
                count = 0
                for s in stations:
                    # Check if already exists
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
                print(f"✅ Added {count} Police Stations as Safe Zones.")

        # 3. Add Synthetic Safe Zones (Shops & Well-lit areas)
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
                "name": "7-Eleven Convenience Store",
                "type": "shop_24hr",
                "lat": 11.0210, "lng": 76.9650,
                "address": "Gandhipuram, Coimbatore",
                "is_24hr": True,
                "score": 80.0
            },
            {
                "name": "Well-Lit Main Road Segment - Avinashi Road",
                "type": "well_lit_area",
                "lat": 11.0250, "lng": 77.0000,
                "address": "Avinashi Road, Coimbatore",
                "is_24hr": True,
                "score": 90.0
            },
            {
                "name": "TIDEL Park CCTV Zone",
                "type": "well_lit_area",
                "lat": 11.0285, "lng": 77.0265,
                "address": "Vilankurichi Road, Coimbatore",
                "is_24hr": True,
                "score": 98.0
            },
            {
                "name": "Brookefields Mall Security Hub",
                "type": "well_lit_area",
                "lat": 11.0085, "lng": 76.9600,
                "address": "Krishnaswamy Rd, Coimbatore",
                "is_24hr": False,
                "score": 88.0
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
        print(f"✅ Added {len(additional_safe_zones)} high-traffic Safe Zones.")

        # 4. Generate Synthetic Crime Hotspots (MVP Zones)
        # We define high-risk spots to test the rerouting logic
        crime_hotspots = [
            {
                "district": "Coimbatore City",
                "name": "Zone 1: Town Hall High-Risk Area",
                "lat": 10.9950, "lng": 76.9610,
                "murders": 2, "harassment": 15, "accidents": 25, "thefts": 40,
                "risk_score": 85.0, "radius": 0.8
            },
            {
                "district": "Coimbatore City",
                "name": "Zone 2: Gandhipuram Night-Risk Area",
                "lat": 11.0180, "lng": 76.9680,
                "murders": 0, "harassment": 8, "accidents": 30, "thefts": 20,
                "risk_score": 65.0, "radius": 1.2
            },
            {
                "district": "Coimbatore City",
                "name": "Zone 3: Ukkadam Bypass High-Accident Zone",
                "lat": 10.9850, "lng": 76.8550,
                "murders": 1, "harassment": 5, "accidents": 45, "thefts": 10,
                "risk_score": 75.0, "radius": 1.5
            }
        ]

        for ch in crime_hotspots:
            # We add these as specific location-based crime records
            crime = CrimeData(
                district=ch['district'],
                location={"lat": ch['lat'], "lng": ch['lng']},
                murder_count=ch['murders'],
                sexual_harassment_count=ch['harassment'],
                road_accident_count=ch['accidents'],
                theft_count=ch['thefts'],
                crime_risk_score=ch['risk_score'],
                year=2024,
                radius_km=ch['radius']
            )
            db.add(crime)
        print(f"✅ Generated {len(crime_hotspots)} synthetic Crime Hotspots for demo.")

        db.commit()
        print("🏁 MVP Population Complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during population: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_mvp_data()
