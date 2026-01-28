
import os
import sys
from pathlib import Path

# Add the current directory to sys.path
sys.path.append(str(Path(__file__).parent))

from database.database import engine, Base, init_db
import asyncio

def reset_db():
    db_file = Path("smartshield.db")
    if db_file.exists():
        print(f"Deleting existing database: {db_file}")
        os.remove(db_file)
    
    print("Initializing new database...")
    # This will call create_all through init_db (sync part)
    from database.models import User # Ensure models are loaded
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully!")

if __name__ == "__main__":
    reset_db()
