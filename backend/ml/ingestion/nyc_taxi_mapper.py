"""
Mapper for NYC Taxi / TLC Dataset to Smart Shield Historical Deliveries format
Dataset: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
"""
import pandas as pd
import numpy as np
from datetime import datetime

def map_nyc_taxi_data(input_path, output_path):
    print(f"Reading NYC Taxi data from {input_path}...")
    # Load dataset (supports CSV or Parquet)
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)
    
    print("Mapping columns...")
    # Smart Shield format:
    # route_id,origin_lat,origin_lng,dest_lat,dest_lng,actual_time_minutes,distance_km,traffic_level,weather_condition,hour,day_of_week,rider_id,vehicle_type,success
    
    mapped_df = pd.DataFrame()
    
    # Generate Route IDs
    mapped_df['route_id'] = [f"NYC_{i}" for i in range(len(df))]
    
    # Lat/Lng mapping
    mapped_df['origin_lat'] = df['pickup_latitude'] if 'pickup_latitude' in df.columns else df['PULocationID'] # Simplified for zones
    mapped_df['origin_lng'] = df['pickup_longitude'] if 'pickup_longitude' in df.columns else 0
    mapped_df['dest_lat'] = df['dropoff_latitude'] if 'dropoff_latitude' in df.columns else df['DOLocationID']
    mapped_df['dest_lng'] = df['dropoff_longitude'] if 'dropoff_longitude' in df.columns else 0
    
    # Time calculations
    pickup_time = pd.to_datetime(df['tpep_pickup_datetime'])
    dropoff_time = pd.to_datetime(df['tpep_dropoff_datetime'])
    mapped_df['actual_time_minutes'] = (dropoff_time - pickup_time).dt.total_seconds() / 60
    
    # Distance (Already in miles in NYC data, converting to KM)
    mapped_df['distance_km'] = df['trip_distance'] * 1.60934
    
    # Temporal features
    mapped_df['hour'] = pickup_time.dt.hour
    mapped_df['day_of_week'] = pickup_time.dt.dayofweek
    
    # Defaults for delivery specific data
    mapped_df['traffic_level'] = 'medium' # Default, can be refined by speed
    mapped_df['weather_condition'] = 'clear'
    mapped_df['rider_id'] = df['VendorID'].astype(str) if 'VendorID' in df.columns else 'Unknown'
    mapped_df['vehicle_type'] = 'car'
    mapped_df['success'] = 1
    
    # Filter out invalid records (e.g. 0 distance or negative time)
    mapped_df = mapped_df[(mapped_df['distance_km'] > 0) & (mapped_df['actual_time_minutes'] > 0)]
    
    print(f"Saving {len(mapped_df)} mapped records to {output_path}...")
    mapped_df.to_csv(output_path, index=False)
    print("Mapping complete!")

if __name__ == "__main__":
    # Example usage:
    # map_nyc_taxi_data('yellow_tripdata_2023-01.csv', 'backend/data/ml_training/historical_deliveries.csv')
    pass
