import requests
import json
import time
from datetime import datetime

def run_demo():
    print("🚀 Initializing Smart Shield AI Demo Run...")
    
    # Endpoint
    url = "http://localhost:8000/api/v1/delivery/optimize"
    
    # Payload: Chennai Central to Guindy National Park
    payload = {
        "starting_point": {"latitude": 13.0827, "longitude": 80.2707},
        "stops": [
            {
                "stop_id": "GUINDY_001",
                "address": "Guindy National Park",
                "coordinates": {"latitude": 13.0067, "longitude": 80.2206},
                "priority": "high"
            }
        ],
        "optimize_for": ["safety"],
        "rider_info": {"gender": "female", "rider_id": "rider_123"},
        "vehicle_type": "motorcycle",
        "departure_time": datetime.now().isoformat()
    }
    
    print(f"📍 Route: Chennai Central -> Guindy")
    print(f"🧠 Asking AI to optimize for SAFETY...")
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            raw_data = response.json()
            data = raw_data.get('data', {})
            
            print("\n--- 📊 AI PREDICTION RESULTS ---")
            print(f"✅ Route ID: {data.get('route_id', 'N/A')}")
            print(f"⏱️ XGBoost Predicted Duration: {data.get('total_duration_seconds', 0) / 60:.1f} minutes")
            print(f"🛡️ Random Forest Safety Score: {data.get('average_safety_score', 0):.1f}/100")
            
            # Check for RL Recommendation
            if data.get("rl_recommended_id"):
                 print(f"🤖 RL Agent Recommendation: Route ID {data['rl_recommended_id']}")
            
            print("\n--- 🛣️ SEGMENT BREAKDOWN ---")
            for i, segment in enumerate(data.get('segments', [])):
                print(f"Segment {i+1}: {segment['distance_meters']/1000:.2f} km")
                print(f"  - AI Safety Level: {segment.get('safety_score', 'N/A')}")
                if segment.get('weather'):
                    print(f"  - Weather: {segment['weather'].get('condition', 'Clear')}")
            
            print("\n✅ Demo Complete. The system successfully cross-referenced Safety Metrics + ML Models.")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Tip: Make sure the backend server (uvicorn) is running on port 8000.")

if __name__ == "__main__":
    run_demo()
