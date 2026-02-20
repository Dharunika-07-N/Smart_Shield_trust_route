import os
import csv
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import SessionLocal, engine, Base
from database.models import CrimeData
from api.services.crime_data import CrimeDataService

def import_crime_csv():
    print("Starting Crime Data Import...")
    db = SessionLocal()
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Use the CrimeDataService logic to parse the CSVs
    service = CrimeDataService()
    
    # Clear existing data
    db.query(CrimeData).delete()
    
    imported_count = 0
    for district, data in service.crime_data.items():
        coords = data.get('coordinates', (0, 0))
        
        # Calculate a simplified risk score for the DB
        risk_score = (
            data.get('murders', 0) * 5 +
            data.get('sexual_harassment', 0) * 10 +
            data.get('road_accidents', 0) * 1 +
            data.get('theft', 0) * 0.5
        ) / 100.0
        risk_score = min(100.0, risk_score)
        
        crime_entry = CrimeData(
            district=district,
            location={"lat": coords[0], "lng": coords[1]},
            murder_count=data.get('murders', 0),
            sexual_harassment_count=data.get('sexual_harassment', 0),
            road_accident_count=data.get('road_accidents', 0),
            theft_count=data.get('theft', 0),
            crime_risk_score=risk_score,
            year=2022,
            radius_km=15.0 # District level coverage
        )
        db.add(crime_entry)
        imported_count += 1
    
    db.commit()
    db.close()
    print(f"✅ Successfully imported {imported_count} district crime records into the database.")

if __name__ == "__main__":
    import_crime_csv()
