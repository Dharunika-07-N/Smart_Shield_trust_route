import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from database.database import SessionLocal, engine, Base
from database.models import User, Customer, Delivery
from datetime import datetime

def seed_driver_deliveries():
    db = SessionLocal()
    try:
        # Find the driver
        driver = db.query(User).filter(User.username == "driver@smartshield.com").first()
        if not driver:
            print("Driver not found. Please run seed_demo_users.py first.")
            return

        # Find or create a customer
        customer = db.query(Customer).first()
        if not customer:
            customer = Customer(
                name="Suresh Kumar",
                phone="9876543210",
                email="suresh@example.com",
                addresses=['24, Lotus Apts, Velachery, Chennai']
            )
            db.add(customer)
            db.flush()

        # Create some deliveries for the driver
        deliveries = [
            {
                "order_id": "ORD-7742-XJ",
                "status": "assigned",
                "pickup_location": {"address": "City Mall, Chennai", "lat": 13.0827, "lng": 80.2707},
                "dropoff_location": {"address": "24, Lotus Apts, Velachery, Chennai", "lat": 12.9716, "lng": 80.2452}
            },
            {
                "order_id": "ORD-8821-KM",
                "status": "pending",
                "pickup_location": {"address": "Pizza Hut, Adyar", "lat": 13.0063, "lng": 80.2574},
                "dropoff_location": {"address": "Apollo Hospital, Greams Road", "lat": 13.0607, "lng": 80.2512}
            }
        ]

        for d in deliveries:
            existing = db.query(Delivery).filter(Delivery.order_id == d["order_id"]).first()
            if existing:
                existing.assigned_rider_id = driver.id
                existing.status = d["status"]
                print(f"Updated delivery {d['order_id']}")
            else:
                new_delivery = Delivery(
                    order_id=d["order_id"],
                    customer_id=customer.id,
                    pickup_location=d["pickup_location"],
                    dropoff_location=d["dropoff_location"],
                    status=d["status"],
                    assigned_rider_id=driver.id,
                    safety_score=85.0,
                    estimated_distance=5.2,
                    estimated_duration=20.0
                )
                db.add(new_delivery)
                print(f"Created delivery {d['order_id']}")
        
        db.commit()
        print("✅ Seeded deliveries for driver@smartshield.com")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_driver_deliveries()
