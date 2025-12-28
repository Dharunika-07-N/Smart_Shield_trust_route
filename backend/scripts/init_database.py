import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Base
from database.database import engine
from sqlalchemy import text

def init_database():
    """Initialize database with PostGIS extension and all tables"""
    
    # Enable PostGIS
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
        print("✅ PostGIS extension enabled")
    except Exception as e:
        print(f"⚠️ Could not enable PostGIS (might be using SQLite or missing permissions): {e}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully!")
    print(f"✅ Created/Verified {len(Base.metadata.tables)} tables")

if __name__ == "__main__":
    init_database()
