import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from database.database import SessionLocal
from database.models import User, RiderProfile
from api.services.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user exists
        username = "dharunika"
        email = "dharunika0708@gmail.com"
        
        # Delete existing if any to reset
        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            print(f"User {username} already exists. Updating password...")
            existing.hashed_password = get_password_hash("password123")
            existing.status = "active"
            db.commit()
            print("Password updated to: password123")
            return

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash("password123"),
            full_name="Dharunika",
            phone="1234567890",
            role="rider",
            status="active",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        rider_profile = RiderProfile(
            user_id=user.id,
            vehicle_type="scooter",
            gender="female",
            preferences={"prefers_safe_routes": True}
        )
        db.add(rider_profile)
        db.commit()

        print("Test user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print("Password: password123")
        print("Role: rider")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
