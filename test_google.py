
import googlemaps
from loguru import logger
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))
from config.config import settings

def test_google_maps():
    key = settings.GOOGLE_MAPS_API_KEY
    if not key or key.startswith('YOUR_'):
        logger.error("No valid Google Maps key found in .env")
        return

    try:
        gmaps = googlemaps.Client(key=key)
        # Simple geocode test
        res = gmaps.geocode("Coimbatore, Tamil Nadu")
        if res:
            logger.success("Google Maps API Key is WORKING")
            logger.info(f"Geocode result: {res[0]['geometry']['location']}")
        else:
            logger.warning("Google Maps API Key returned no results for test query")
    except Exception as e:
        logger.error(f"Google Maps API Key FAILED: {e}")

if __name__ == "__main__":
    test_google_maps()
