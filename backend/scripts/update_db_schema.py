import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "../smartshield.db")

def add_column():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "emergency_contact_email" not in columns:
            print("Adding emergency_contact_email column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN emergency_contact_email VARCHAR")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column emergency_contact_email already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
