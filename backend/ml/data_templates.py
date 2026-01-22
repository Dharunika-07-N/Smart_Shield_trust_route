"""
Sample data templates for training ML models in Smart Shield
"""

# 1. HISTORICAL DELIVERY DATA (for Time Predictor)
historical_deliveries_template = """
route_id,origin_lat,origin_lng,dest_lat,dest_lng,actual_time_minutes,distance_km,traffic_level,weather_condition,hour,day_of_week,rider_id,vehicle_type,num_turns,num_traffic_lights,road_type,success
R001,11.0168,76.9558,11.0200,76.9600,18.5,3.2,medium,clear,14,2,RID001,motorcycle,8,3,arterial,1
R002,11.0180,76.9570,11.0250,76.9650,22.3,4.1,high,rain,18,4,RID002,motorcycle,12,5,residential,1
R003,11.0150,76.9540,11.0300,76.9700,15.2,2.8,low,clear,10,1,RID003,scooter,5,2,highway,1
R004,11.0200,76.9600,11.0400,76.9800,35.7,7.5,medium,cloudy,8,0,RID001,motorcycle,18,8,mixed,1
R005,11.0220,76.9620,11.0180,76.9580,8.3,1.5,low,clear,15,3,RID004,bicycle,3,1,residential,1
"""

# 2. RIDER PERFORMANCE DATA (for RL Agent)
rider_performance_template = """
rider_id,experience_months,total_deliveries,avg_delivery_time_minutes,success_rate,safety_violations,avg_rating,preferred_vehicle,avg_speed_kmh
RID001,24,1250,22.5,0.98,0,4.8,motorcycle,32.5
RID002,18,890,25.3,0.95,1,4.6,motorcycle,28.7
RID003,36,2100,20.1,0.99,0,4.9,scooter,25.3
RID004,12,450,28.7,0.92,2,4.3,bicycle,18.2
RID005,30,1800,21.8,0.97,0,4.7,motorcycle,30.1
"""

# 3. TRAFFIC PATTERNS (for Traffic Prediction)
traffic_patterns_template = """
location_id,latitude,longitude,hour,day_of_week,avg_speed_kmh,congestion_level,sample_size
LOC001,11.0180,76.9570,8,0,15.2,high,150
LOC001,11.0180,76.9570,8,1,18.5,medium,145
LOC001,11.0180,76.9570,14,0,28.3,low,120
LOC001,11.0180,76.9570,18,0,12.8,high,180
LOC002,11.0200,76.9600,8,0,22.1,medium,95
LOC002,11.0200,76.9600,14,0,35.7,low,88
"""

# 4. WEATHER HISTORY (for Weather Impact Model)
weather_history_template = """
timestamp,latitude,longitude,temperature_c,precipitation_mm,wind_speed_kmh,visibility_km,condition,impact_on_delivery
2024-01-15T08:00:00,11.0180,76.9570,28.5,0.0,12.3,10.0,clear,none
2024-01-15T14:00:00,11.0180,76.9570,32.1,0.0,15.7,10.0,clear,none
2024-01-15T18:00:00,11.0180,76.9570,29.3,2.5,18.2,8.5,light_rain,minor
2024-01-16T08:00:00,11.0180,76.9570,27.8,8.3,22.5,5.2,heavy_rain,major
2024-01-16T14:00:00,11.0180,76.9570,30.5,0.0,10.1,10.0,cloudy,none
"""

# 5. CROWDSOURCED FEEDBACK (for Route Quality)
crowdsourced_feedback_template = """
feedback_id,route_id,rider_id,timestamp,location_lat,location_lng,is_faster,has_traffic,has_safety_issue,rating,comment
FB001,R001,RID001,2024-01-15T14:35:00,11.0185,76.9575,1,0,0,5,Great route
FB002,R002,RID002,2024-01-15T18:25:00,11.0220,76.9630,0,1,0,3,Heavy traffic
FB003,R003,RID003,2024-01-16T10:15:00,11.0175,76.9560,1,0,0,5,Fast and safe
FB004,R004,RID001,2024-01-16T08:45:00,11.0250,76.9680,0,1,0,3,Morning rush hour
"""

# 6. DELIVERY EPISODES (for Reinforcement Learning)
rl_episodes_template = """
episode_id,rider_id,start_lat,start_lng,end_lat,end_lng,state_sequence,action_sequence,reward_sequence,total_reward,success
EP001,RID001,11.0168,76.9558,11.0200,76.9600,"[s1,s2,s3]","[a1,a2,a3]","[r1,r2,r3]",85.5,1
EP002,RID002,11.0180,76.9570,11.0250,76.9650,"[s1,s2,s3,s4]","[a1,a2,a3,a4]","[r1,r2,r3,r4]",72.3,1
"""

# 7. ROAD NETWORK DATA (for A* Algorithm - Optional)
road_network_template = """
edge_id,start_lat,start_lng,end_lat,end_lng,road_type,speed_limit_kmh,length_m,num_lanes,has_traffic_light
E001,11.0168,76.9558,11.0170,76.9560,arterial,50,250,4,1
E002,11.0170,76.9560,11.0175,76.9565,arterial,50,550,4,0
E003,11.0175,76.9565,11.0180,76.9570,residential,30,450,2,1
E004,11.0180,76.9570,11.0185,76.9575,highway,80,1200,6,0
"""


def save_templates_to_csv(output_dir="backend/data/ml_training"):
    """Save all templates to CSV files"""
    import os
    from pathlib import Path
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    templates = {
        'historical_deliveries.csv': historical_deliveries_template,
        'rider_performance.csv': rider_performance_template,
        'traffic_patterns.csv': traffic_patterns_template,
        'weather_history.csv': weather_history_template,
        'crowdsourced_feedback.csv': crowdsourced_feedback_template,
        'rl_episodes.csv': rl_episodes_template,
        'road_network.csv': road_network_template
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content.strip())
        print(f"Created: {filepath}")


if __name__ == "__main__":
    save_templates_to_csv()
    print("\n✅ All sample data templates created!")
    print("\n📝 Next steps:")
    print("1. Fill these CSV files with real data from your operations")
    print("2. Minimum recommended samples:")
    print("   - Historical deliveries: 1,000+ records (10,000+ ideal)")
    print("   - Rider performance: 10+ riders (100+ ideal)")
    print("   - Traffic patterns: 100+ location-hour combinations")
    print("   - Crowdsourced feedback: Continuous collection")
    print("3. Run training scripts to build ML models")
    print("4. A* algorithm works immediately with simplified safety scoring")
    print("\n⚠️  Note: Crime, lighting, and patrol data removed - using simplified safety scoring")
