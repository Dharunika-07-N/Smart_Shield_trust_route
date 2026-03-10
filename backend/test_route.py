
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
root = Path(r"c:\Users\Sackthika\OneDrive\Desktop\Smart Shield Trust Route\backend")
sys.path.append(str(root))

from api.models.route_optimizer import RouteOptimizer
from api.schemas.delivery import Coordinate, DeliveryStop
from datetime import datetime

async def test():
    optimizer = RouteOptimizer()
    start = Coordinate(latitude=11.0319, longitude=77.0358)
    stop = DeliveryStop(
        stop_id="DEST_1",
        address="Destination",
        coordinates=Coordinate(latitude=11.0238, longitude=77.0227)
    )
    
    try:
        print("Starting optimization...")
        result = await optimizer._optimize_single_leg_alternatives(
            starting_point=start,
            stop=stop,
            optimize_for=["time", "distance"],
            rider_info={"gender": "neutral", "prefers_safe_routes": True},
            departure_time=datetime.now()
        )
        print("Success!")
        print(f"Route ID: {result['route_id']}")
        print(f"Alternatives: {len(result.get('alternatives', []))}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
