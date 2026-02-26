
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))
from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger

async def test_vrp():
    maps = MapsService()
    if not maps.graphhopper:
        print("GraphHopper not initialized")
        return

    start = Coordinate(latitude=11.0168, longitude=76.9558)
    stops = [
        Coordinate(latitude=11.0268, longitude=76.9658),
        Coordinate(latitude=11.0368, longitude=76.9758)
    ]
    
    vehicles = [{
        "vehicle_id": "v1",
        "start_address": {"location_id": "start", "lat": start.latitude, "lon": start.longitude}
    }]
    
    services = []
    for i, stop in enumerate(stops):
        services.append({
            "id": f"stop_{i}",
            "address": {"location_id": f"stop_{i}", "lat": stop.latitude, "lon": stop.longitude}
        })
        
    print("Testing GraphHopper VRP...")
    result = maps.graphhopper.solve_vrp(vehicles, services)
    if result:
        print("VRP Success!")
        print(f"Status: {result.get('status')}")
        if 'solution' in result:
            print(f"Distance: {result['solution']['distance']}")
            print(f"Time: {result['solution']['time']}")
    else:
        print("VRP Failed or returned no result")

if __name__ == "__main__":
    asyncio.run(test_vrp())
