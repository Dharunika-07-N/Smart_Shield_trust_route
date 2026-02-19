"""
simulate_fleet.py
-----------------
Simulates multiple active drivers in the Chennai area for demonstration.
Creates demo drivers and periodically updates their locations in the database.

Run from backend directory:
    python simulate_fleet.py
"""

import sys
import os
import time
import random
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.database import SessionLocal, Base, engine
from database.models import User, DeliveryStatus, RiderProfile
from api.services.security import get_password_hash
from loguru import logger

# Simulation Configuration
CENTER_LAT = 13.0827  # Chennai Center
CENTER_LNG = 80.2707
RADIUS = 0.05  # Dispersion radius
NUM_DRIVERS = 8
UPDATE_INTERVAL = 10  # Seconds between location updates

# Demo Drivers Data
DRIVERS = [
    {"name": "Rajesh Kumar", "email": "rajesh@fleet.com", "v_type": "bike"},
    {"name": "Ananya Seth", "email": "ananya@fleet.com", "v_type": "scooter"},
    {"name": "Vikram Singh", "email": "vikram@fleet.com", "v_type": "bike"},
    {"name": "Siddharth Rao", "email": "sid@fleet.com", "v_type": "delivery_van"},
    {"name": "Meera Iyer", "email": "meera@fleet.com", "v_type": "bike"},
    {"name": "Prakash G", "email": "prakash@fleet.com", "v_type": "bike"},
    {"name": "Deepa Devi", "email": "deepa@fleet.com", "v_type": "scooter"},
    {"name": "Arun Prasad", "email": "arun@fleet.com", "v_type": "bike"},
]

def setup_sim_drivers(db: Session):
    """Ensure demo drivers exist in the database."""
    logger.info("Setting up simulation drivers...")
    driver_ids = []
    
    for d_info in DRIVERS:
        user = db.query(User).filter(User.username == d_info["email"]).first()
        if not user:
            user = User(
                username=d_info["email"],
                email=d_info["email"],
                hashed_password=get_password_hash("fleet@123"),
                role="rider", # Using 'rider' as it's the primary field role in the app
                full_name=d_info["name"],
                status="active"
            )
            db.add(user)
            db.flush()
            
            # Add profile
            profile = RiderProfile(
                user_id=user.id,
                vehicle_type=d_info["v_type"],
                license_number=f"TN-{random.randint(10,99)}-{uuid.uuid4().hex[:6].upper()}"
            )
            db.add(profile)
            db.commit()
            logger.info(f"Created driver: {d_info['name']}")
        
        driver_ids.append(user.id)
    
    return driver_ids

def run_simulation():
    """Main simulation loop."""
    logger.info("Starting Fleet Simulation...")
    db = SessionLocal()
    
    try:
        driver_ids = setup_sim_drivers(db)
        
        # Initialize positions
        positions = {}
        for d_id in driver_ids:
            positions[d_id] = {
                "lat": CENTER_LAT + (random.random() - 0.5) * RADIUS,
                "lng": CENTER_LNG + (random.random() - 0.5) * RADIUS
            }

        logger.info(f"Simulation running for {len(driver_ids)} drivers. Press Ctrl+C to stop.")
        
        iteration = 0
        while True:
            iteration += 1
            logger.info(f"Update cycle #{iteration}...")
            
            for d_id in driver_ids:
                # Slowly move the driver
                pos = positions[d_id]
                pos["lat"] += (random.random() - 0.5) * 0.002
                pos["lng"] += (random.random() - 0.5) * 0.002
                
                # Insert location update
                status_update = DeliveryStatus(
                    delivery_id="simulation",
                    rider_id=d_id,
                    current_location={
                        "latitude": pos["lat"],
                        "longitude": pos["lng"]
                    },
                    status="available",
                    speed_kmh=random.uniform(15, 45),
                    heading=random.uniform(0, 360),
                    battery_level=random.randint(60, 100),
                    timestamp=datetime.utcnow()
                )
                db.add(status_update)
            
            db.commit()
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user.")
    except Exception as e:
        logger.error(f"Simulation error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
