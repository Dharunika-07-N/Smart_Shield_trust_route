
import pandas as pd
import csv
import sys
import os
import time
from pathlib import Path
import re

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from api.services.maps import MapsService
from database.database import SessionLocal
from database.models import SafeZone
from config.config import settings

def process_police_stations():
    csv_path = 'backend/data/police_stations_coimbatore.csv.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    print(f"Reading {csv_path}...")
    
    # Initialize Maps Service for geocoding
    maps_service = MapsService()
    db = SessionLocal()
    
    try:
        # Read the CSV with custom quote handling
        # Format: ID, "Name, Address, Phone", District
        rows_added = 0
        
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            
            for row in reader:
                if len(row) < 3:
                    continue
                
                id_val, details, district = row[0], row[1], row[2]
                
                # We mainly care about Coimbatore district or the cities mentioned by user
                target_cities = ['Coimbatore', 'Tiruppur', 'Pollachi', 'Udumalpet', 'Dharapuram']
                is_target = district.strip() == 'Coimbatore' or any(city in details for city in target_cities)
                
                if not is_target:
                    continue
                
                # Split details into Name and Phone
                # Example: "Perumanallur Police Station, Perumanallur PS, Coimbatore - 641601. PH: 0421-2350070"
                name_part = details.split('. PH:')[0].strip()
                phone_part = details.split('. PH:')[1].strip() if '. PH:' in details else "N/A"
                
                # Clean name for better geocoding (e.g., remove "B1" prefix or PS details)
                clean_name = name_part.split(',')[0].strip()
                # Remove common prefixes like "B1  ", "B2  " etc.
                clean_name = re.sub(r'^[A-Z][0-9]+\s+', '', clean_name)
                
                query_address = f"{clean_name}, {district}, Tamil Nadu, India"
                print(f"Geocoding: {query_address}...")
                
                # MapsService.geocode is sync (def)
                coords = maps_service.geocode(query_address)
                
                if coords:
                    lat, lng = coords.latitude, coords.longitude
                    
                    # Create SafeZone entry
                    safe_zone = SafeZone(
                        zone_type='police_station',
                        name=name_part,
                        address=details,
                        phone=phone_part,
                        location={"lat": lat, "lng": lng},
                        is_24hr=True,
                        safety_score=95.0
                    )
                    
                    db.add(safe_zone)
                    rows_added += 1
                    print(f"Added {name_part} @ {lat}, {lng}")
                    
                    if rows_added % 10 == 0:
                        db.commit()
                        print(f"Progress: {rows_added} stations saved...")
                else:
                    print(f"Warning: Could not geocode {name_part}")
                
                # Sleep 1s to respect PositionStack/OSRM free tier limits
                time.sleep(1)
        
        db.commit()
        print(f"Successfully added {rows_added} police stations to the database!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    process_police_stations()
