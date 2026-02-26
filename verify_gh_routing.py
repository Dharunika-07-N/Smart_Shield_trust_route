
import requests
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))
from config.config import settings

def verify_gh():
    api_key = settings.GRAPHHOPPER_API_KEY
    if not api_key or api_key.startswith('YOUR_'):
        print("No valid GraphHopper key")
        return

    origin = (11.0168, 76.9558)
    destination = (11.0668, 77.0058)
    
    url = f"https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{origin[0]},{origin[1]}", f"{destination[0]},{destination[1]}"],
        "vehicle": "car",
        "key": api_key,
        "type": "json"
    }
    
    print(f"Requesting: {url} with points {params['point']}")
    res = requests.get(url, params=params)
    print(f"Status: {res.status_code}")
    data = res.json()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    verify_gh()
