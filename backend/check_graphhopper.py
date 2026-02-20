import os
import requests
import json
from dotenv import load_dotenv

def check_graphhopper_status():
    load_dotenv()
    api_key = os.getenv("GRAPHHOPPER_API_KEY")
    
    print("\n--- GraphHopper API Diagnostic ---")
    if not api_key or api_key == "your_graphhopper_key_here":
        print("❌ Error: GRAPHHOPPER_API_KEY is not set in .env")
        return

    print(f"✓ API Key found: {api_key[:5]}...{api_key[-5:]}")
    
    # Check 1: Routing API
    print("\n✓ Check 1: Testing Routing API")
    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": ["13.0827,80.2707", "13.0475,80.2090"], # Chennai points
        "vehicle": "car",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("  ✅ Routing API works!")
            data = response.json()
            path = data['paths'][0]
            print(f"  → Distance: {path['distance']/1000:.2f} km")
            print(f"  → Time: {path['time']/60000:.2f} mins")
        else:
            print(f"  ❌ Routing API failed (Status: {response.status_code})")
            print(f"  → Error: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Request failed: {e}")

    # Check 2: Geocoding API
    print("\n✓ Check 2: Testing Geocoding API")
    url = "https://graphhopper.com/api/1/geocode"
    params = {
        "q": "Chennai Central",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("  ✅ Geocoding API works!")
        else:
            print(f"  ❌ Geocoding API failed")
    except Exception:
        print("  ❌ Geocoding API failed")

    print("\n--- Diagnostic Complete ---\n")

if __name__ == "__main__":
    check_graphhopper_status()
