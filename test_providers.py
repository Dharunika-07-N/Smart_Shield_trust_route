
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger

async def test_all_providers():
    maps = MapsService()
    origin = {"lat": 11.0168, "lng": 76.9558} # Coimbatore
    destination = {"lat": 11.0168 + 0.02, "lng": 76.9558 + 0.02}
    
    # 1. Test Google Maps directly
    if maps.gmaps:
        try:
            logger.info("Testing Google Maps API directly...")
            res = maps.gmaps.directions(
                origin=(origin['lat'], origin['lng']),
                destination=(destination['lat'], destination['lng']),
                mode="driving"
            )
            if res:
                logger.success(f"Google Maps Direct SUCCESS: Found {len(res)} routes")
            else:
                logger.warning("Google Maps Direct: No routes found")
        except Exception as e:
            logger.error(f"Google Maps Direct FAILED: {e}")
    else:
        logger.warning("Google Maps Client not initialized")

    # 2. Test GraphHopper directly
    if maps.graphhopper:
        try:
            logger.info("Testing GraphHopper API directly...")
            res = maps.graphhopper.get_directions(
                (origin['lat'], origin['lng']),
                (destination['lat'], destination['lng'])
            )
            if res:
                logger.success("GraphHopper Direct SUCCESS")
            else:
                logger.warning("GraphHopper Direct: No routes found")
        except Exception as e:
            logger.error(f"GraphHopper Direct FAILED: {e}")
    else:
        logger.warning("GraphHopper Client not initialized")

    # 3. Test OSRM directly
    if maps.osrm:
        try:
            logger.info("Testing OSRM API directly...")
            res = await maps.osrm.get_directions(origin, destination)
            if res:
                logger.success(f"OSRM Direct SUCCESS: Found {len(res)} routes")
            else:
                logger.warning("OSRM Direct: No routes found")
        except Exception as e:
            logger.error(f"OSRM Direct FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_providers())
