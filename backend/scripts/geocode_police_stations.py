import csv
import json
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger

def geocode_stations():
    """Geocode police stations from CSV file."""
    maps_service = MapsService()
    
    input_file = Path(__file__).parent.parent / "data" / "police_stations_raw.csv"
    output_file = Path(__file__).parent.parent / "data" / "police_stations.json"
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return
    
    stations = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_name = row['Name']
            search_query = f"{station_name}, Coimbatore, Tamil Nadu, India"
            
            logger.info(f"Geocoding: {search_query}")
            
            # Use MapsService to geocode
            coord = maps_service.geocode(search_query)
            
            if coord:
                station_data = {
                    "name": station_name,
                    "phone": row['Phone'],
                    "type": row['Type'],
                    "latitude": coord.latitude,
                    "longitude": coord.longitude,
                    "address": search_query # or the formatted address if we had it
                }
                stations.append(station_data)
                logger.success(f"Found: {coord.latitude}, {coord.longitude}")
            else:
                logger.warning(f"Could not geocode: {station_name}")
                # Fallback or manual entry could go here
                
            # Rate limiting to be nice to API
            time.sleep(0.5)
            
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=2)
        
    logger.info(f"Saved {len(stations)} geocoded stations to {output_file}")

if __name__ == "__main__":
    geocode_stations()
