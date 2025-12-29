#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session
import datetime
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import SessionLocal, engine
from database.models import HistoricalDelivery, Base

# Create tables if not exist
Base.metadata.create_all(bind=engine)

def ingest():
    csv_path = 'c:/Users/Admin/Desktop/Smart_shield/backend/data/rides'
    print(f"Reading data from {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Total rows found: {len(df)}")
    
    # Filter completed rides for success
    df['success'] = df['ride_status'] == 'completed'
    
    # Parse date
    df['date_parsed'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    # Use current date for any invalid dates
    df.loc[df['date_parsed'].isna(), 'date_parsed'] = datetime.datetime.now()
    
    # Generate coordinates mapping for unique locations
    print("Generating location mappings...")
    unique_locs = pd.concat([df['source'], df['destination']]).unique()
    
    # Bangalore bounds
    min_lat, max_lat = 12.85, 13.10
    min_lng, max_lng = 77.50, 77.75
    
    random.seed(42) # For consistency
    loc_mapping = {}
    for loc in unique_locs:
        loc_mapping[loc] = (
            random.uniform(min_lat, max_lat),
            random.uniform(min_lng, max_lng)
        )
        
    db = SessionLocal()
    try:
        # Clear existing historical data to avoid duplicates if required
        # db.query(HistoricalDelivery).delete()
        # db.commit()
        
        deliveries = []
        count = 0
        for i, row in df.iterrows():
            source_coords = loc_mapping.get(row['source'])
            dest_coords = loc_mapping.get(row['destination'])
            
            # Use the minute part of 'time' as a hint or just cycle hours
            # row['time'] is MM:SS.f
            try:
                minute = int(row['time'].split(':')[0])
            except:
                minute = random.randint(0, 59)
                
            # Distribute hours based on minutes or just index
            hour = (i % 24)
            
            delivery = HistoricalDelivery(
                delivery_id=str(row['ride_id']),
                origin_lat=source_coords[0],
                origin_lng=source_coords[1],
                destination_lat=dest_coords[0],
                destination_lng=dest_coords[1],
                delivery_time_minutes=float(row['duration']) if not pd.isna(row['duration']) else 0.0,
                distance_km=float(row['distance']) if not pd.isna(row['distance']) else 0.0,
                success=bool(row['success']),
                time_of_day=hour,
                day_of_week=row['date_parsed'].dayofweek if hasattr(row['date_parsed'], 'dayofweek') else 0,
                completed_at=row['date_parsed'] if isinstance(row['date_parsed'], datetime.datetime) else datetime.datetime.now(),
                weather={"condition": "clear"},
                traffic={"level": "medium"}
            )
            deliveries.append(delivery)
            
            # Batch insert every 2000 rows
            if len(deliveries) >= 2000:
                db.bulk_save_objects(deliveries)
                db.commit()
                count += len(deliveries)
                print(f"✓ Ingested {count} rows...")
                deliveries = []
        
        if deliveries:
            db.bulk_save_objects(deliveries)
            db.commit()
            count += len(deliveries)
            
        print(f"✅ Ingestion complete! Total rows: {count}")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest()
