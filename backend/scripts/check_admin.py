
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))
from database.models import User
from api.services.security import verify_password, get_password_hash

DATABASE_URL = "sqlite:///./smartshield.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin@smartshield.com").first()
        if user:
            print(f"User found: {user.username}, Role: {user.role}, Status: {user.status}")
            is_valid = verify_password("Admin@123", user.hashed_password)
            print(f"Password 'Admin@123' valid: {is_valid}")
            
            # If invalid, reset it
            if not is_valid:
                user.hashed_password = get_password_hash("Admin@123")
                user.status = "active"
                db.commit()
                print("Reset password to 'Admin@123'")
        else:
            print("Admin user NOT found")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()
