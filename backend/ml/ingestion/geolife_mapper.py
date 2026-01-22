"""
Mapper for Microsoft GeoLife GPS Trajectory Dataset to Smart Shield format.
Dataset: https://www.microsoft.com/en-us/download/details.aspx?id=52367
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from pathlib import Path

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def process_plt_file(file_path, user_id):
    """Extract trips from a single .plt file."""
    try:
        # Skip header (6 lines)
        df = pd.read_csv(file_path, skiprows=6, header=None, 
                         names=['lat', 'lng', 'zero', 'alt', 'date_days', 'date_str', 'time_str'])
        
        if len(df) < 2:
            return []
        
        # Combine date and time
        df['timestamp'] = pd.to_datetime(df['date_str'] + ' ' + df['time_str'])
        
        trips = []
        current_trip_points = []
        
        # Split into trips based on time gaps (> 10 minutes)
        for i in range(len(df)):
            if not current_trip_points:
                current_trip_points.append(df.iloc[i])
                continue
            
            time_gap = (df.iloc[i]['timestamp'] - current_trip_points[-1]['timestamp']).total_seconds() / 60
            
            if time_gap > 10: # New trip
                if len(current_trip_points) > 5: # Valid trip has at least 5 points
                    trips.append(create_trip_summary(current_trip_points, user_id))
                current_trip_points = [df.iloc[i]]
            else:
                current_trip_points.append(df.iloc[i])
        
        if len(current_trip_points) > 5:
            trips.append(create_trip_summary(current_trip_points, user_id))
            
        return trips
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def create_trip_summary(points, user_id):
    """Convert points list to a trip dictionary."""
    start = points[0]
    end = points[-1]
    
    duration = (end['timestamp'] - start['timestamp']).total_seconds() / 60
    
    # Calculate cumulative distance
    total_dist = 0
    for i in range(len(points) - 1):
        total_dist += haversine(points[i]['lat'], points[i]['lng'], 
                                points[i+1]['lat'], points[i+1]['lng'])
    
    return {
        'route_id': f"GEO_{user_id}_{start['timestamp'].strftime('%Y%H%M%S')}",
        'origin_lat': start['lat'],
        'origin_lng': start['lng'],
        'dest_lat': end['lat'],
        'dest_lng': end['lng'],
        'actual_time_minutes': duration,
        'distance_km': total_dist,
        'traffic_level': 'low', # Default
        'weather_condition': 'clear',
        'hour': start['timestamp'].hour,
        'day_of_week': start['timestamp'].weekday(),
        'rider_id': f"USER_{user_id}",
        'vehicle_type': 'mixed', # Often walking/cycling in GeoLife
        'success': 1
    }

def map_geolife_data(raw_data_dir, output_path, max_users=10):
    """Crawl GeoLife directory and process files."""
    print(f"Starting GeoLife mapping from {raw_data_dir}...")
    all_trips = []
    
    data_dir = Path(raw_data_dir) / "Data"
    if not data_dir.exists():
        print(f"Error: {data_dir} not found. Check structure.")
        return
    
    user_folders = sorted([f for f in os.listdir(data_dir) if f.isdigit()])
    processed_users = 0
    
    for user_id in user_folders:
        if processed_users >= max_users:
            break
            
        print(f"Processing user {user_id}...")
        traj_dir = data_dir / user_id / "Trajectory"
        if not traj_dir.exists():
            continue
            
        for plt_file in traj_dir.glob("*.plt"):
            trips = process_plt_file(plt_file, user_id)
            all_trips.extend(trips)
            
        processed_users += 1
    
    if not all_trips:
        print("No trips found!")
        return
        
    df = pd.DataFrame(all_trips)
    # Filter weird data (too short, negative time, etc)
    df = df[(df['distance_km'] > 0.1) & (df['actual_time_minutes'] > 1)]
    
    print(f"Saving {len(df)} trips to {output_path}...")
    df.to_csv(output_path, index=False)
    print("GeoLife mapping complete!")

if __name__ == "__main__":
    # Base directory for raw data
    raw_dir = r"c:\Users\Admin\Desktop\Smart_shield\backend\data\raw\Geolife Trajectories 1.3"
    output = r"c:\Users\Admin\Desktop\Smart_shield\backend\data\ml_training\historical_deliveries.csv"
    
    map_geolife_data(raw_dir, output, max_users=20) # Process first 20 users for a good sample
