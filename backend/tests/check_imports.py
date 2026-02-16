import sys
import os
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

try:
    from api.main import app
    print("SUCCESS: api.main.app imported")
    from database.database import Base, get_db
    print("SUCCESS: database.database imported")
    from api.services.safety import SafetyService
    print("SUCCESS: api.services.safety imported")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED: {e}")
