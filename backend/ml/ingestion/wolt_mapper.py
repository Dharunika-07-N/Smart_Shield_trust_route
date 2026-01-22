"""
Mapper for Wolt / Food Delivery Datasets to Smart Shield format.
Dataset: https://www.kaggle.com/datasets/muhammadwajeeharif/wolt-delivery-dataset
"""
import pandas as pd
import numpy as np
from datetime import datetime

def map_wolt_data(input_path, output_path):
    print(f"Reading Wolt data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print("Mapping columns...")
    # Expected columns in Wolt/Food datasets usually include:
    # pickup_lat, pickup_lon, delivery_lat, delivery_lon, time_taken, etc.
    
    # This is a generic template that matches the common Kaggle food delivery schema
    mapped_df = pd.DataFrame()
    
    # Map coordinates
    if 'pickup_lat' in df.columns:
        mapped_df['origin_lat'] = df['pickup_lat']
        mapped_df['origin_lng'] = df['pickup_lon']
        mapped_df['dest_lat'] = df['delivery_lat']
        mapped_df['dest_lng'] = df['delivery_lon']
    elif 'Restaurant_latitude' in df.columns:
        mapped_df['origin_lat'] = df['Restaurant_latitude']
        mapped_df['origin_lng'] = df['Restaurant_longitude']
        mapped_df['dest_lat'] = df['Delivery_location_latitude']
        mapped_df['dest_lng'] = df['Delivery_location_longitude']
    
    # Map Time (usually in minutes or seconds)
    if 'Time_taken(min)' in df.columns:
        mapped_df['actual_time_minutes'] = df['Time_taken(min)']
    elif 'duration' in df.columns:
        mapped_df['actual_time_minutes'] = df['duration'] / 60 # if seconds
        
    # Map Hour/Day
    if 'Order_Time' in df.columns:
        # Some datasets have "15:45:00", others have full timestamps
        try:
            order_time = pd.to_datetime(df['Order_Time'])
            mapped_df['hour'] = order_time.dt.hour
            mapped_df['day_of_week'] = 0 # Default to Monday if not specified
        except:
            mapped_df['hour'] = 12 # Default
            mapped_df['day_of_week'] = 0
            
    # Default values
    mapped_df['route_id'] = [f"WOLT_{i}" for i in range(len(df))]
    mapped_df['distance_km'] = df['distance'] if 'distance' in df.columns else 0
    mapped_df['traffic_level'] = df['Road_traffic_density'].str.lower() if 'Road_traffic_density' in df.columns else 'medium'
    mapped_df['weather_condition'] = df['Weatherconditions'].str.replace('conditions', '').str.lower() if 'Weatherconditions' in df.columns else 'clear'
    mapped_df['rider_id'] = df['Delivery_person_ID'] if 'Delivery_person_ID' in df.columns else 'Unknown'
    mapped_df['vehicle_type'] = df['Type_of_vehicle'] if 'Type_of_vehicle' in df.columns else 'motorcycle'
    mapped_df['success'] = 1
    
    # Basic distance calculation if missing
    if (mapped_df['distance_km'] == 0).all():
        from math import radians, cos, sin, asin, sqrt
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            r = 6371 
            return c * r
        
        mapped_df['distance_km'] = mapped_df.apply(
            lambda x: haversine(x.origin_lng, x.origin_lat, x.dest_lng, x.dest_lat), axis=1)

    print(f"Saving {len(mapped_df)} mapped records to {output_path}...")
    # Append or overwrite? For now overwrite to start fresh
    mapped_df.to_csv(output_path, index=False)
    print("Wolt mapping complete!")

if __name__ == "__main__":
    # Example usage:
    # map_wolt_data('backend/data/raw/wolt.csv', 'backend/data/ml_training/historical_deliveries.csv')
    pass
