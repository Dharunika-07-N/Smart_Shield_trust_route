
import sqlite3
import uuid
import random
from datetime import datetime, timedelta

def seed_reports():
    print("📊 Seeding AI Report Data...")
    db_path = 'backend/smartshield.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Seed Riders
    print("👤 Seeding Riders...")
    rider_ids = []
    riders = []
    for i in range(15):
        rid = str(uuid.uuid4())
        rider_ids.append(rid)
        riders.append((
            rid, f"Rider-{i+100}", f"rider{i}@example.com", f"999000{i:04d}",
            "moto_id", "motorcycle", random.choice(['male', 'female', 'neutral']),
            1, datetime.utcnow() - timedelta(days=random.randint(0, 60)), 1
        ))
    
    cursor.executemany("""
    INSERT INTO riders (id, name, email, phone, company_id, vehicle_type, gender, prefers_safe_routes, created_at, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, riders)

    # 2. Seed Delivery Routes
    print("🗺️ Seeding Delivery Routes...")
    route_ids = []
    routes = []
    for i in range(50):
        rid = f"ROUTE-{i+1000}"
        route_ids.append(rid)
        # origin/dest around Coimbatore
        lat1, lng1 = 11.0168 + random.uniform(-0.05, 0.05), 76.9558 + random.uniform(-0.05, 0.05)
        lat2, lng2 = 11.0168 + random.uniform(-0.05, 0.05), 76.9558 + random.uniform(-0.05, 0.05)
        routes.append((
            rid, lat1, lng1, lat2, lng2,
            random.uniform(10, 40), random.uniform(2, 10), random.uniform(65, 98),
            random.uniform(20, 50), random.uniform(5, 12),
            (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat(),
            '{"condition": "Clear", "temp": 28}', '{"level": "Low"}'
        ))
    
    cursor.executemany("""
    INSERT INTO delivery_routes (route_id, origin_lat, origin_lng, destination_lat, destination_lng, predicted_time, predicted_distance, safety_score, actual_time, actual_distance, created_at, weather_conditions, traffic_conditions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, routes)

    # 3. Seed Safety Feedback
    print("💬 Seeding Safety Feedback...")
    feedback = []
    for i in range(30):
        feedback.append((
            str(uuid.uuid4()), random.choice(route_ids), random.choice(rider_ids),
            random.choice(['route', 'area', 'general']), random.randint(3, 5),
            '{"lat": 11.0, "lng": 76.9}', "Found well lit area", 
            random.choice(['lighting', 'patrol', 'traffic']), "night",
            (datetime.now() - timedelta(days=random.randint(0, 10))).isoformat(), 0
        ))
    
    cursor.executemany("""
    INSERT INTO safety_feedback (id, route_id, rider_id, feedback_type, rating, location, comments, incident_type, time_of_day, date_submitted, processed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, feedback)

    # 4. Seed Delivery Feedback (Specific table)
    print("📝 Seeding Delivery Feedback...")
    # Need to get integer ids from delivery_routes
    cursor.execute("SELECT id, route_id FROM delivery_routes")
    db_routes = cursor.fetchall()
    
    d_feedback = []
    for db_id, r_id in db_routes:
        if random.random() > 0.5:
             d_feedback.append((
                 db_id, random.choice(rider_ids), random.randint(4, 5),
                 random.randint(4, 5), random.randint(4, 5),
                 '[]', '[]', "Great route, very safe", 
                 (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat()
             ))
    
    cursor.executemany("""
    INSERT INTO delivery_feedback (route_id, rider_id, safety_rating, route_quality_rating, comfort_rating, incidents_reported, unsafe_areas, feedback_text, submitted_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, d_feedback)

    # 5. Seed Panic Alerts
    print("🚨 Seeding Panic Alerts...")
    alerts = []
    for i in range(5):
        alerts.append((
            str(uuid.uuid4()), random.choice(rider_ids), random.choice(route_ids),
            '{"lat": 11.02, "lng": 76.96}', "resolved", "[]", 1, 0,
            (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
        ))
    
    cursor.executemany("""
    INSERT INTO panic_alerts (id, rider_id, route_id, location, status, alerted_contacts, company_notified, emergency_services_notified, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts)

    conn.commit()
    conn.close()
    print("✨ AI Report Data seeding complete!")

if __name__ == "__main__":
    seed_reports()
