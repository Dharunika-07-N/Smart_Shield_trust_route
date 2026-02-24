
import sqlite3
import json
from datetime import datetime, timedelta
import random
import uuid

def go_live():
    print("📡 Activating Live Dispatch Data...")
    db_path = 'backend/smartshield.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Get some rider IDs
    cursor.execute("SELECT id, full_name FROM users WHERE role IN ('rider', 'driver')")
    riders = cursor.fetchall()
    if not riders:
        print("❌ No riders found in database. Run seed_demo_users.py first.")
        return

    now = datetime.utcnow()
    # Base location for Coimbatore
    base_lat, base_lng = 11.0168, 76.9558
    
    # Get some delivery IDs to link status to
    cursor.execute("SELECT id FROM deliveries LIMIT 100")
    delivery_ids = [d[0] for d in cursor.fetchall()]
    
    status_data = []
    print(f"🛰️ Generating live tracking for {len(riders)} riders...")
    for i, (rid, name) in enumerate(riders):
        did = delivery_ids[i % len(delivery_ids)] if delivery_ids else str(uuid.uuid4())
        # Create tracking points per rider
        ts = now - timedelta(minutes=random.randint(0, 2))
        lat = base_lat + random.uniform(-0.02, 0.02)
        lng = base_lng + random.uniform(-0.02, 0.02)
        
        status_data.append((
            str(uuid.uuid4()), did, rid, 
            json.dumps({"latitude": lat, "longitude": lng}),
            'online', ts.isoformat(), random.uniform(20, 45), 
            random.uniform(0, 360), 85, ts.isoformat()
        ))

    cursor.executemany("""
    INSERT INTO delivery_status 
    (id, delivery_id, rider_id, current_location, status, timestamp, speed_kmh, heading, battery_level, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, status_data)

    # 3. Ensure some active deliveries
    print("📦 Creating active delivery queue...")
    # Get some customer IDs
    cursor.execute("SELECT id FROM customers LIMIT 10")
    customers = [c[0] for c in cursor.fetchall()]
    if not customers:
        customers = [None]

    active_deliveries = []
    for i in range(15):
        oid = f"ORD-{random.randint(1000, 9999)}"
        pickup = json.dumps({"lat": base_lat + random.uniform(-0.01, 0.01), "lng": base_lng + random.uniform(-0.01, 0.01), "address": "Pick Point"})
        dropoff = json.dumps({"lat": base_lat + random.uniform(-0.01, 0.01), "lng": base_lng + random.uniform(-0.01, 0.01), "address": "Drop Point"})
        status = random.choice(['pending', 'assigned', 'picked_up', 'in_transit'])
        rider_id = random.choice(riders)[0] if status != 'pending' else None
        
        active_deliveries.append((
            str(uuid.uuid4()), oid, random.choice(customers),
            pickup, dropoff, status, rider_id, random.uniform(70, 95),
            random.uniform(2, 8), random.uniform(10, 30), now.isoformat()
        ))

    cursor.executemany("""
    INSERT INTO deliveries 
    (id, order_id, customer_id, pickup_location, dropoff_location, status, assigned_rider_id, safety_score, estimated_distance, estimated_duration, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, active_deliveries)

    conn.commit()
    conn.close()
    print("✨ Dispatcher dashboard should now show active markers and tasks!")

if __name__ == "__main__":
    go_live()
