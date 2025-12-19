import sys
from pathlib import Path

print("Python version:", sys.version)
print("Path:", sys.path)

try:
    import fastapi
    print("OK: fastapi imported")
except ImportError as e:
    print("FAIL: fastapi import failed:", e)

try:
    import uvicorn
    print("OK: uvicorn imported")
except ImportError as e:
    print("FAIL: uvicorn import failed:", e)

try:
    import sqlalchemy
    print("OK: sqlalchemy imported")
except ImportError as e:
    print("FAIL: sqlalchemy import failed:", e)

try:
    import pydantic
    print("OK: pydantic imported")
except ImportError as e:
    print("FAIL: pydantic import failed:", e)

try:
    import sklearn
    print("OK: sklearn imported")
except ImportError as e:
    print("FAIL: sklearn import failed:", e)

try:
    import joblib
    print("OK: joblib imported")
except ImportError as e:
    print("FAIL: joblib import failed:", e)

try:
    import loguru
    print("OK: loguru imported")
except ImportError as e:
    print("FAIL: loguru import failed:", e)

try:
    import googlemaps
    print("OK: googlemaps imported")
except ImportError as e:
    print("FAIL: googlemaps import failed:", e)

try:
    import networkx
    print("OK: networkx imported")
except ImportError as e:
    print("FAIL: networkx import failed:", e)

# Test local imports
sys.path.append(str(Path.cwd()))
print("Checking local imports from", Path.cwd())

try:
    import api.main
    print("OK: api.main imported")
except Exception as e:
    print("FAIL: api.main import failed:")
    import traceback
    traceback.print_exc()
