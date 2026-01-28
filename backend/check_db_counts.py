import sqlite3
import os

db_path = 'smartshield.db'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

print(f"{'Table':<25} | {'Count':<10}")
print("-" * 40)
for table in sorted(tables):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} | {count:<10}")
    except Exception as e:
        print(f"{table:<25} | Error: {e}")

conn.close()
