
import sqlite3
import os

DB_PATH = "instance/smartfixer.db"

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(time_spent)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'total_seconds' not in columns:
            print("Adding total_seconds column...")
            cursor.execute("ALTER TABLE time_spent ADD COLUMN total_seconds INTEGER DEFAULT 0")
        else:
            print("total_seconds column already exists.")

        if 'last_updated' not in columns:
            print("Adding last_updated column...")
            cursor.execute("ALTER TABLE time_spent ADD COLUMN last_updated TIMESTAMP")
        else:
            print("last_updated column already exists.")

        conn.commit()
        print("Schema update complete.")
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
