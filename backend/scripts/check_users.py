import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import SessionLocal
from database.models import User

def check_users():
    db = SessionLocal()
    try:
        count = db.query(User).count()
        print(f"Total users in database: {count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
