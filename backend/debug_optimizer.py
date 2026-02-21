import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api.models.route_optimizer import RouteOptimizer
from api.services.maps import MapsService
from api.schemas.delivery import Coordinate, DeliveryStop
from datetime import datetime

async def test_optimizer():
    print("\n=== Testing MapsService get_directions directly ===")
    ms = MapsService()
    origin = Coordinate(latitude=13.0827, longitude=80.2707)
    dest = Coordinate(latitude=13.0400, longitude=80.2400)
    
    directions = ms.get_directions(origin, dest)
    print(f"Directions type: {type(directions)}")
    if isinstance(directions, list):
        print(f"  List length: {len(directions)}")
        for i, d in enumerate(directions):
            rc = d.get('route_coordinates')
            op = d.get('overview_polyline', {}).get('points', '')
            print(f"  Route {i}: route_coordinates={len(rc) if rc else None} pts, polyline_len={len(op)}, summary={d.get('summary','?')[:40]}")
    elif isinstance(directions, dict):
        rc = directions.get('route_coordinates')
        op = directions.get('overview_polyline', {}).get('points', '')
        print(f"  Dict: route_coordinates={len(rc) if rc else None} pts, polyline_len={len(op)}")

    print("\n=== Testing Full Optimizer ===")
    optimizer = RouteOptimizer()
    
    start = Coordinate(latitude=13.0827, longitude=80.2707)
    stops = [
        DeliveryStop(stop_id="stop1", coordinates=Coordinate(latitude=13.0400, longitude=80.2400), address="T. Nagar"),
        DeliveryStop(stop_id="stop2", coordinates=Coordinate(latitude=12.9800, longitude=80.2200), address="Guindy"),
    ]
    
    try:
        result = await optimizer.optimize_route(start, stops, optimize_for=["time", "safety"])
        print("Optimization OK")
        for i, seg in enumerate(result['segments']):
            rc = seg.get('route_coordinates')
            instr = seg.get('instructions')
            print(f"  Seg {i}: polyline_pts={len(rc) if rc else 0}, instructions={len(instr) if instr else 0}, dist={seg['distance_meters']:.0f}m")
    except Exception as e:
        import traceback
        print(f"FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_optimizer())
