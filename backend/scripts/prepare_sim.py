
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))
from database.models import User, RiderProfile, Delivery
from api.services.security import get_password_hash

# Resolve absolute path to smartshield.db
BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/smartshield.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def prepare_sim_riders():
    db = SessionLocal()
    try:
        # Find 10 riders
        riders = db.query(User).filter(User.role == 'rider').limit(10).all()
        p_hash = get_password_hash("Rider@123")
        
        sim_data = []
        for rider in riders:
            rider.hashed_password = p_hash
            rider.status = "active"
            
            # Ensure rider has an assigned delivery or create a dummy one if needed
            delivery = db.query(Delivery).filter(Delivery.assigned_rider_id == rider.id).first()
            if not delivery:
                # Create a minimal delivery for simulation
                delivery = Delivery(
                    order_id=f"SIM-{rider.username[:5]}",
                    status="assigned",
                    assigned_rider_id=rider.id,
                    pickup_location={"lat": 13.0827, "lng": 80.2707, "address": "Chennai Central"},
                    dropoff_location={"lat": 13.0067, "lng": 80.2206, "address": "Guindy"}
                )
                db.add(delivery)
                db.flush()
            
            sim_data.append({"username": rider.username, "delivery_id": delivery.id})
            
        db.commit()
        print("PASSWORDS_RESET_SUCCESS")
        for data in sim_data:
            print(f"RIDER_DATA:{data['username']}|{data['delivery_id']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    prepare_sim_riders()
