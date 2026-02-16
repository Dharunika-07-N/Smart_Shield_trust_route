import sqlite3
import os

def update_database_schema():
    db_path = os.path.join("backend", "smartshield.db")
    if not os.path.exists(db_path):
         print(f"Database not found at {db_path}. Creating new one...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Updating database schema...")
    
    # 1. Route Segments - Add new columns if missing
    # We can't easily ADD COLUMN IF NOT EXISTS in SQLite in one go for multiple columns efficiently in older versions, 
    # but we can try catch. Or just create table if not exists with full schema first? 
    # If table exists, we append columns.
    
    # New features for route_segments
    new_segment_cols = [
        ("population_density", "REAL"),
        ("commercial_area", "INTEGER DEFAULT 0"),
        ("residential_area", "INTEGER DEFAULT 0"),
        ("street_width", "REAL"),
        ("cctv_coverage", "REAL"),
        ("emergency_response_time", "REAL"),
        ("timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("hour", "INTEGER"),
        ("day_of_week", "INTEGER"),
        ("is_weekend", "INTEGER"),
        ("safety_class", "INTEGER")
    ]
    
    # Ensure table exists first with basics if not
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_segments (
        segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER NOT NULL,
        start_lat REAL NOT NULL,
        start_lon REAL NOT NULL,
        end_lat REAL NOT NULL,
        end_lon REAL NOT NULL,
        crime_rate REAL,
        lighting REAL,
        patrol_frequency REAL,
        traffic_density REAL,
        police_proximity REAL,
        hospital_proximity REAL,
        safety_score REAL
    );
    """)
    
    for col_name, col_type in new_segment_cols:
        try:
            cursor.execute(f"ALTER TABLE route_segments ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to route_segments")
        except sqlite3.OperationalError:
            # Column likely exists
            pass

    # 2. Deliveries - Add new columns
    new_delivery_cols = [
        ("route_distance", "REAL"),
        ("estimated_distance", "REAL"),
        ("actual_distance", "REAL"),
        ("traffic_level", "REAL"),
        ("timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("hour", "INTEGER"),
        ("day_of_week", "INTEGER"),
        ("is_weekend", "INTEGER"),
        ("is_holiday", "INTEGER"),
        ("weather_condition", "TEXT"),
        ("temperature", "REAL"),
        ("precipitation", "REAL"),
        ("num_stops", "INTEGER DEFAULT 1"),
        ("route_complexity", "REAL"),
        ("vehicle_type", "TEXT"),
        ("driver_id", "INTEGER"),
        ("driver_experience", "INTEGER"),
        ("estimated_time", "REAL"),
        ("actual_time", "REAL"),
        ("success", "INTEGER DEFAULT 1"),
        ("delay_reason", "TEXT")
    ]
    
    # Ensure deliveries table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT, 
        status TEXT
    );
    """)
    
    for col_name, col_type in new_delivery_cols:
        try:
            cursor.execute(f"ALTER TABLE deliveries ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to deliveries")
        except sqlite3.OperationalError:
            pass

    # 3. Delivery Outcomes (For RL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivery_outcomes (
        outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_id INTEGER NOT NULL,
        start_latitude REAL,
        start_longitude REAL,
        end_latitude REAL,
        end_longitude REAL,
        timestamp DATETIME,
        traffic_level REAL,
        weather TEXT,
        route_choice TEXT,
        actual_time REAL,
        estimated_time REAL,
        safety_score REAL,
        success INTEGER,
        actual_distance REAL,
        estimated_distance REAL,
        time_reward REAL,
        safety_reward REAL,
        success_reward REAL,
        distance_reward REAL,
        total_reward REAL
    );
    """)
    print("Ensured delivery_outcomes table exists")

    # 4. Training History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_history (
        training_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        models_trained TEXT,
        metrics TEXT,
        errors TEXT,
        version TEXT,
        duration_seconds REAL
    );
    """)
    print("Ensured training_history table exists")

    # 5. Model Versions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_versions (
        version_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        version TEXT NOT NULL,
        file_path TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        metrics TEXT,
        is_active INTEGER DEFAULT 0,
        UNIQUE(model_name, version)
    );
    """)
    print("Ensured model_versions table exists")
    
    # 6. Model Performance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        num_predictions INTEGER,
        mae REAL,
        rmse REAL,
        accuracy REAL,
        feature_drift_score REAL,
        prediction_drift_score REAL,
        needs_retraining INTEGER DEFAULT 0
    );
    """)
    print("Ensured model_performance table exists")

    # 7. Safety Feedback - Ensure columns for Phase 2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safety_feedback (
        id TEXT PRIMARY KEY,
        route_id TEXT NOT NULL,
        rider_id TEXT,
        feedback_type TEXT NOT NULL,
        rating INTEGER NOT NULL,
        location JSON,
        comments TEXT,
        incident_type TEXT,
        time_of_day TEXT DEFAULT 'day',
        date_submitted DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT 0
    );
    """)
    
    # Try adding columns if they might be missing in an existing table
    for col, col_type in [("processed", "BOOLEAN DEFAULT 0"), ("time_of_day", "TEXT DEFAULT 'day'")]:
        try:
            cursor.execute(f"ALTER TABLE safety_feedback ADD COLUMN {col} {col_type}")
            print(f"Added column {col} to safety_feedback")
        except sqlite3.OperationalError:
            pass

    conn.commit()

    conn.commit()
    conn.close()
    print("Database schema update complete.")

if __name__ == "__main__":
    update_database_schema()
