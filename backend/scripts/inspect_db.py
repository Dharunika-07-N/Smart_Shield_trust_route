import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import engine
from sqlalchemy import text

def inspect_db():
    with engine.connect() as conn:
        print("--- Tables ---")
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        for table in tables:
            print(f"Table: {table[0]}")
            columns = conn.execute(text(f"PRAGMA table_info({table[0]})")).fetchall()
            for col in columns:
                print(f"  Column: {col[1]} ({col[2]})")

if __name__ == "__main__":
    inspect_db()
