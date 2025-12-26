import sys
from pathlib import Path

# Add the parent directory to sys.path to import from database and api
sys.path.append(str(Path(__file__).parent.parent))

from database.database import SessionLocal, engine, Base
from database.models import Rider
import uuid

def seed_rider():
    db = SessionLocal()
    try:
        # Check if test rider already exists
        test_rider_id = "test-rider-001"
        existing = db.query(Rider).filter(Rider.id == test_rider_id).first()
        
        if existing:
            print(f"Test rider already exists: {test_rider_id}. Updating email...")
            existing.email = "dharunika0708@gmail.com"
            existing.emergency_contacts = [
                {
                    "name": "Emergency Contact",
                    "phone": "9876543210",
                    "email": "dharunika0708@gmail.com",
                    "relationship": "Contact"
                }
            ]
            db.commit()
            return test_rider_id
            
        # Create a new test rider
        new_rider = Rider(
            id=test_rider_id,
            name="Test Rider",
            email="dharunika0708@gmail.com",
            phone="1234567890",
            gender="female",
            emergency_contacts=[
                {
                    "name": "Emergency Contact",
                    "phone": "9876543210",
                    "email": "dharunika0708@gmail.com",
                    "relationship": "Contact"
                }
            ]
        )
        
        db.add(new_rider)
        db.commit()
        print(f"Successfully created test rider with ID: {test_rider_id}")
        return test_rider_id
    except Exception as e:
        print(f"Error seeding rider: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rider()
