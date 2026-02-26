
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger

async def test_routing():
    maps = MapsService()
    origin = {"lat": 11.0168, "lng": 76.9558} # Coimbatore
    destination = {"lat": 11.0168 + 0.05, "lng": 76.9558 + 0.05}
    
    logger.info("Testing Google Maps...")
    if maps.gmaps:
        try:
            directions = maps.get_directions(origin, destination, provider="google")
            if directions:
                logger.success(f"Google Maps returned {len(directions)} routes")
                logger.info(f"First route provider: {directions[0].get('provider')}")
            else:
                logger.error("Google Maps returned no directions")
        except Exception as e:
            logger.error(f"Google Maps failed: {e}")
    else:
        logger.warning("Google Maps not initialized")

    logger.info("Testing GraphHopper...")
    if maps.graphhopper:
        try:
            directions = maps.get_directions(origin, destination, provider="graphhopper")
            if directions:
                logger.success(f"GraphHopper returned {len(directions)} routes")
                logger.info(f"First route provider: {directions[0].get('provider')}")
        except Exception as e:
            logger.error(f"GraphHopper failed: {e}")

    logger.info("Testing OSRM...")
    if maps.osrm:
        try:
            directions = await maps.osrm.get_directions(origin, destination)
            if directions:
                logger.success(f"OSRM returned {len(directions)} routes")
        except Exception as e:
            logger.error(f"OSRM failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_routing())
