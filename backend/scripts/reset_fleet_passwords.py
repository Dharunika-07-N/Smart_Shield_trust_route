
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))
from database.models import User, Delivery
from api.services.security import get_password_hash

DATABASE_URL = "sqlite:///./smartshield.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_passwords():
    db = SessionLocal()
    try:
        # Get 10 riders that have deliveries
        riders_with_deliveries = db.query(User).join(Delivery, User.id == Delivery.assigned_rider_id).limit(100).all()
        count = 0
        p_hash = get_password_hash("Rider@123")
        
        sim_data = []
        seen_riders = set()
        
        for user in riders_with_deliveries:
            # FORCE update
            user.hashed_password = p_hash
            user.status = "active"
            user.role = "rider"
            
            if user.id not in seen_riders and len(sim_data) < 10:
                # Find one active delivery for this rider
                delivery = db.query(Delivery).filter(Delivery.assigned_rider_id == user.id).first()
                if delivery:
                    sim_data.append((delivery.id, user.username)) # Use USERNAME specifically
                    seen_riders.add(user.id)
                    count += 1
            
        db.commit()
        print(f"Reset and activated {count} riders")
        
        for d_id, username in sim_data:
            print(f"DATA:{d_id}|{username}")
            
    finally:
        db.close()

if __name__ == "__main__":
    reset_passwords()
