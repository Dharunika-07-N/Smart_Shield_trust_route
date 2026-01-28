import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

import random
import json
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session

from database.database import engine, SessionLocal, Base
from database.models import User, RiderProfile, Customer, Delivery, SafetyFeedback, CrimeData, SafeZone
from api.services.security import get_password_hash

fake = Faker()

# Tamil Nadu coordinates
MAJOR_CITIES = [
    {'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707},
    {'name': 'Coimbatore', 'lat': 11.0168, 'lon': 76.9558},
    {'name': 'Madurai', 'lat': 9.9252, 'lon': 78.1198},
    {'name': 'Trichy', 'lat': 10.7905, 'lon': 78.7047},
    {'name': 'Salem', 'lat': 11.6643, 'lon': 78.1460},
]

def generate_random_location(near_city=None, radius_km=10):
    city = random.choice(MAJOR_CITIES) if not near_city or near_city == 'random' else near_city
    lat_offset = random.uniform(-radius_km/111, radius_km/111)
    lon_offset = random.uniform(-radius_km/111, radius_km/111)
    return {
        'lat': city['lat'] + lat_offset,
        'lon': city['lon'] + lon_offset,
        'city': city['name']
    }

def seed_users(db: Session, count=50):
    print(f"🧑 Creating {count} users...")
    users = []
    roles = ['rider', 'driver', 'dispatcher', 'admin']
    for i in range(count):
        role = random.choices(roles, weights=[0.4, 0.4, 0.15, 0.05])[0]
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            hashed_password=get_password_hash("password123"), # Standard password for demo
            full_name=fake.name(),
            phone=fake.phone_number()[:15],
            role=role,
            is_active=True,
            status="active"
        )
        db.add(user)
        users.append(user)
    db.commit()
    for u in users: db.refresh(u)
    return users

def seed_riders(db: Session, users):
    print("🏍️ Creating rider profiles...")
    riders = []
    rider_users = [u for u in users if u.role == 'rider']
    for user in rider_users:
        rider = RiderProfile(
            user_id=user.id,
            vehicle_type=random.choice(['bike', 'scooter', 'bicycle']),
            license_number=fake.bothify('TN##?#######'),
            gender=random.choice(['male', 'female', 'other']),
            preferences={'prefers_safe_routes': True}
        )
        db.add(rider)
        riders.append(rider)
    db.commit()
    for r in riders: db.refresh(r)
    return riders

def seed_customers(db: Session, count=50):
    print("👥 Creating customers...")
    customers = []
    for i in range(count):
        customer = Customer(
            name=fake.name(),
            phone=fake.phone_number()[:15],
            email=fake.email(),
            addresses=json.dumps([fake.address()]),
            preferences=json.dumps({"test": True})
        )
        db.add(customer)
        customers.append(customer)
    db.commit()
    for c in customers: db.refresh(c)
    return customers

def seed_deliveries(db: Session, riders, customers, count=200):
    print(f"📦 Creating {count} deliveries...")
    for i in range(count):
        rider = random.choice(riders)
        customer = random.choice(customers)
        pickup_loc = generate_random_location('random')
        dropoff_loc = generate_random_location('random')
        
        delivery = Delivery(
            order_id=f"ORD{random.randint(100000, 999999)}",
            customer_id=customer.id,
            pickup_location={"address": fake.address(), "lat": pickup_loc['lat'], "lng": pickup_loc['lon']},
            dropoff_location={"address": fake.address(), "lat": dropoff_loc['lat'], "lng": dropoff_loc['lon']},
            status=random.choice(['completed', 'in_progress', 'pending']),
            assigned_rider_id=rider.user_id,
            safety_score=random.uniform(60, 95),
            estimated_distance=random.uniform(2, 15),
            estimated_duration=random.uniform(10, 45),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.add(delivery)
    db.commit()

def seed_crime_data(db: Session):
    print("🚨 Seeding crime data...")
    for city in MAJOR_CITIES:
        for _ in range(20):
            loc = generate_random_location(city)
            crime = CrimeData(
                district=city['name'],
                location={"latitude": loc['lat'], "longitude": loc['lon']},
                murder_count=random.randint(0, 5),
                sexual_harassment_count=random.randint(0, 10),
                road_accident_count=random.randint(0, 20),
                theft_count=random.randint(0, 30),
                crime_risk_score=random.uniform(0, 100),
                year=2022
            )
            db.add(crime)
    db.commit()

def seed_safe_zones(db: Session):
    print("🛡️ Seeding safe zones...")
    for city in MAJOR_CITIES:
        for i in range(5):
            loc = generate_random_location(city)
            zone = SafeZone(
                name=f"{city['name']} Safe Zone {i}",
                location={"latitude": loc['lat'], "longitude": loc['lon']},
                zone_type=random.choice(['police_station', 'hospital'])
            )
            db.add(zone)
    db.commit()

def main():
    print("🚀 Starting simplified seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users = seed_users(db)
        riders = seed_riders(db, users)
        customers = seed_customers(db)
        seed_deliveries(db, riders, customers)
        seed_crime_data(db)
        seed_safe_zones(db)
        print("✅ Seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
