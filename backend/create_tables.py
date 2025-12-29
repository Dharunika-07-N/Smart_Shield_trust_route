import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from database.database import engine, Base
from database.models import *

print("Attempting to create all tables...")
Base.metadata.create_all(bind=engine)
print("Tables creation/verification complete.")
