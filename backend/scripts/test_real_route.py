
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from api.services.maps import MapsService
from api.services.safety import SafetyService
from api.schemas.delivery import Coordinate
from loguru import logger

async def get_test_route():
    maps = MapsService()
    safety = SafetyService()
    
    # A to B: Gandhipuram to Peelamedu, Coimbatore
    origin = {"lat": 11.0183, "lng": 76.9682}
    destination = {"lat": 11.0253, "lng": 77.0125}
    
    print(f"\n--- Calculating Real A-to-B Route ---")
    print(f"Origin: Gandhipuram ({origin['lat']}, {origin['lng']})")
    print(f"Destination: Peelamedu ({destination['lat']}, {destination['lng']})")
    
    # 1. Get real directions (Mock if no API key, but same structure)
    try:
        routes = await maps.get_directions(origin, destination)
    except Exception as e:
        print(f"[ERR] Directions failed: {e}")
        return
    
    if not routes:
        print("[FAIL] Could not calculate route.")
        return
        
    route = routes[0]
    print(f"\n[MAPS] Route Summary: {route.get('summary', 'Main Road')}")
    print(f"[MAPS] Distance: {route['legs'][0]['distance']['text']}")
    print(f"[MAPS] Duration: {route['legs'][0]['duration']['text']}")
    
    # 2. Get Safety Scoring for the route
    coords = route.get('route_coordinates', [])
    if not coords:
        print("[FAIL] No coordinates found in route.")
        return
        
    print(f"\n[SAFETY] Analyzing {len(coords)} track points for hazards...")
    
    # In a real run, we'd use safety_scorer.score_route
    try:
        from api.models.safety_scorer import SafetyScorer
        scorer = SafetyScorer()
        safety_data = scorer.score_route(coords, time_of_day="night")
        
        print("\n--- SAFETY ANALYSIS (NIGHT MODE) ---")
        print(f"Safety Score: {safety_data['route_safety_score']}/100")
        print(f"Average Reliability: {safety_data['average_score']:.2f}")
        
        print("\nSafety Suggestions:")
        for sugg in safety_data.get('improvement_suggestions', []):
            print(f"  - {sugg}")
            
    except Exception as e:
        print(f"[ERR] Safety analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(get_test_route())
