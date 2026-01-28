import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from database.database import SessionLocal
from database.models import User
from api.services.security import verify_password

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "dharunika").first()
        if user:
            print(f"User found: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Status: {user.status}")
            print(f"Is Active: {user.is_active}")
            print(f"Hashed Password: {user.hashed_password}")
            
            pwd = "password123"
            is_valid = verify_password(pwd, user.hashed_password)
            print(f"Password 'password123' valid: {is_valid}")
        else:
            print("User 'dharunika' not found.")
            
        user_by_email = db.query(User).filter(User.email == "dharunika0708@gmail.com").first()
        if user_by_email:
             print(f"User found by email: {user_by_email.username}")
        else:
             print("User not found by email 'dharunika0708@gmail.com'.")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
