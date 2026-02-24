
import sqlite3
import os

db_path = 'backend/smartshield.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = [
    'route_segments', 'deliveries', 'delivery_outcomes', 'training_history',
    'delivery_routes', 'delivery_feedback', 'safety_feedback', 'panic_alerts', 'riders', 'users'
]
stats = {}

for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        stats[table] = "Table missing"

print("\n=== Database Statistics ===")
for table, count in stats.items():
    print(f"{table}: {count}")

conn.close()
