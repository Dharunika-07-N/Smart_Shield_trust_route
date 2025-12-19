import sys
import os
from pathlib import Path
import traceback

results_file = "debug_results.txt"

def log(msg):
    with open(results_file, "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

if os.path.exists(results_file):
    os.remove(results_file)

log(f"Python version: {sys.version}")

packages = [
    "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
    "sklearn", "joblib", "loguru", "googlemaps", "networkx"
]

for pkg in packages:
    try:
        __import__(pkg)
        log(f"OK: {pkg} imported")
    except ImportError as e:
        log(f"FAIL: {pkg} import failed: {e}")

# Test local imports
sys.path.append(str(Path.cwd()))
log(f"Checking local imports from {Path.cwd()}")

try:
    import api.main
    log("OK: api.main imported")
except Exception as e:
    log("FAIL: api.main import failed")
    with open(results_file, "a") as f:
        traceback.print_exc(file=f)
