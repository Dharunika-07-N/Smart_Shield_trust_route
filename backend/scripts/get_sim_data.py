
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))
from database.models import User, Delivery

DATABASE_URL = "sqlite:///./smartshield.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_sim_data():
    db = SessionLocal()
    try:
        # Get 10 UNIQUE riders that have at least one delivery
        # Then get one delivery ID for each
        from sqlalchemy import func
        results = db.query(Delivery.assigned_rider_id, func.min(Delivery.id), User.email)\
            .join(User, Delivery.assigned_rider_id == User.id)\
            .group_by(Delivery.assigned_rider_id)\
            .limit(10).all()
        for rider_id, delivery_id, email in results:
            print(f"{delivery_id}|{email}")
    finally:
        db.close()

if __name__ == "__main__":
    get_sim_data()
