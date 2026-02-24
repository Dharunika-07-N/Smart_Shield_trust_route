
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(os.path.abspath('backend'))

from ml.safety_classifier_enhanced import EnhancedSafetyClassifier
from ml.time_predictor_enhanced import EnhancedTimePredictor
from ml.rl_agent_enhanced import EnhancedSARSAAgent

def seed_ai_training():
    print("🧠 Starting AI Training Data Seeding...")
    db_path = 'backend/smartshield.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create missing tables if needed (Drop first to ensure schema matching)
    cursor.execute("DROP TABLE IF EXISTS route_segments")
    cursor.execute("DROP TABLE IF EXISTS delivery_outcomes")
    cursor.execute("DROP TABLE IF EXISTS training_history")

    cursor.execute("""
    CREATE TABLE route_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id TEXT,
        segment_order INTEGER,
        crime_rate REAL,
        lighting REAL,
        patrol_frequency REAL,
        traffic_density REAL,
        police_proximity REAL,
        hospital_proximity REAL,
        timestamp TEXT,
        safety_score REAL,
        safety_class INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE delivery_outcomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_id TEXT,
        start_latitude REAL,
        start_longitude REAL,
        end_latitude REAL,
        end_longitude REAL,
        timestamp TEXT,
        route_choice TEXT,
        actual_time REAL,
        estimated_time REAL,
        safety_score REAL,
        success INTEGER,
        actual_distance REAL,
        estimated_distance REAL,
        traffic_level REAL,
        weather TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE training_history (
        timestamp TEXT, 
        models_trained TEXT, 
        metrics TEXT, 
        errors TEXT, 
        version TEXT
    )
    """)

    # 2. Generate Synthetic Safety Data (route_segments)
    print("🛡️ Generating Safety Training Data...")
    safety_data = []
    for i in range(500):
        crime = np.random.beta(2, 5) # Skewed towards low crime
        lighting = np.random.beta(5, 2)
        patrol = np.random.beta(3, 3)
        traffic = np.random.uniform(0, 1)
        police = np.random.uniform(0, 1)
        hospital = np.random.uniform(0, 1)
        
        # Calculate a pseudo-safety score
        score = (1-crime) * 0.4 + lighting * 0.2 + patrol * 0.2 + (1-traffic) * 0.1 + police * 0.1
        s_class = 0
        if score > 0.8: s_class = 4
        elif score > 0.6: s_class = 3
        elif score > 0.4: s_class = 2
        elif score > 0.2: s_class = 1
        
        safety_data.append((
            f"R-{i}", i % 10, crime, lighting, patrol, traffic, police, hospital,
            (datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
            score * 100, s_class
        ))
    
    cursor.executemany("""
    INSERT INTO route_segments 
    (route_id, segment_order, crime_rate, lighting, patrol_frequency, traffic_density, police_proximity, hospital_proximity, timestamp, safety_score, safety_class)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, safety_data)

    # 3. Generate Synthetic RL Data (delivery_outcomes)
    print("🤖 Generating RL Training Data...")
    rl_data = []
    actions = ['fastest', 'safest', 'balanced', 'shortest']
    for i in range(300):
        est_time = np.random.uniform(15, 45)
        # Outcome based on action
        action = np.random.choice(actions)
        success = 1 if np.random.random() > 0.05 else 0
        
        actual_time = est_time
        if action == 'fastest': actual_time *= np.random.uniform(0.8, 1.1)
        elif action == 'safest': actual_time *= np.random.uniform(1.0, 1.3)
        else: actual_time *= np.random.uniform(0.9, 1.2)

        rl_data.append((
            f"DEL-{i}", 11.0168, 76.9558, 11.0333, 76.9825,
            (datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
            action, actual_time, est_time, np.random.uniform(60, 95), success,
            5.2, 5.0, np.random.uniform(0, 1), 'clear'
        ))

    cursor.executemany("""
    INSERT INTO delivery_outcomes 
    (delivery_id, start_latitude, start_longitude, end_latitude, end_longitude, timestamp, route_choice, actual_time, estimated_time, safety_score, success, actual_distance, estimated_distance, traffic_level, weather)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rl_data)

    conn.commit()
    print(f"✅ Database seeded with {len(safety_data)} safety rows and {len(rl_data)} RL rows.")

    # 4. Trigger Training for Models
    print("\n🚀 Training Models (this might take a few seconds)...")
    
    # Safety
    try:
        print("Training Safety Classifier...")
        sc = EnhancedSafetyClassifier()
        df_safety = pd.read_sql_query("SELECT * FROM route_segments", conn)
        X, y = sc.prepare_data(df_safety)
        sc_metrics = sc.train(X, y, tune_hyperparameters=False)
        sc.save_model(version="demo_v1")
        print(f"   Success! F1: {sc_metrics['f1_weighted']:.2f}")
    except Exception as e:
        print(f"   Safety training failed: {e}")
        sc_metrics = {}

    # RL
    try:
        print("Training RL Agent...")
        rl = EnhancedSARSAAgent()
        df_rl = pd.read_sql_query("SELECT * FROM delivery_outcomes", conn)
        rl_metrics = rl.train_from_history(df_rl)
        rl.save_model(version="demo_v1")
        print(f"   Success! Avg Reward: {rl_metrics.get('avg_episode_reward', 0):.2f}")
    except Exception as e:
        print(f"   RL training failed: {e}")
        rl_metrics = {}

    # Time Predictor (using existing deliveries table if possible)
    try:
        print("Training Time Predictor...")
        tp = EnhancedTimePredictor()
        df_time = pd.read_sql_query("SELECT * FROM deliveries WHERE actual_duration_seconds IS NOT NULL LIMIT 100", conn)
        # Need to map columns if they differ from what EnhancedTimePredictor expects
        # EnhancedTimePredictor expects: delivery_id, route_distance, traffic_level, timestamp, actual_time, ...
        # Based on training.py query: actual_time, estimatd_time, route_distance...
        
        # For demo, let's just create a minimal DF if deliveries is empty or missing columns
        if df_time.empty:
             df_time = pd.DataFrame({
                 'delivery_id': [f"D-{i}" for i in range(100)],
                 'route_distance': np.random.uniform(1, 15, 100),
                 'traffic_level': np.random.uniform(0, 1, 100),
                 'timestamp': [datetime.now().isoformat() for _ in range(100)],
                 'actual_time': np.random.uniform(10, 60, 100),
                 'estimated_time': np.random.uniform(10, 60, 100),
                 'weather_condition': ['clear']*100,
                 'num_stops': [2]*100,
                 'vehicle_type': ['motorcycle']*100,
                 'success': [1]*100
             })
        
        X, y, feats = tp.prepare_data(df_time, 'actual_time')
        tp_metrics = tp.train(X, y, tune_hyperparameters=False)
        tp.save_model(version="demo_v1")
        print(f"   Success! R2 Score: {tp_metrics.get('r2', 0):.2f}")
    except Exception as e:
        print(f"   Time training failed: {e}")
        tp_metrics = {}

    # 5. Log to training_history
    cursor.execute("""
    INSERT INTO training_history 
    (timestamp, models_trained, metrics, errors, version)
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        "safety,time,rl",
        str({"safety": sc_metrics, "time": tp_metrics, "rl": rl_metrics}),
        "",
        "demo_v1"
    ))
    conn.commit()
    conn.close()
    print("\n✨ All done! Admin dashboard should now show AI training details.")

if __name__ == "__main__":
    seed_ai_training()
