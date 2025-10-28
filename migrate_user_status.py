import sqlite3
import os
from datetime import datetime

def migrate_user_status():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add last_seen column if it doesn't exist
        if 'last_seen' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_seen DATETIME")
            print("Added last_seen column to users table")
        
        # Add is_online column if it doesn't exist
        if 'is_online' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT 0")
            print("Added is_online column to users table")
        
        # Update existing records with default values
        cursor.execute("UPDATE users SET last_seen = ? WHERE last_seen IS NULL", (datetime.now(),))
        cursor.execute("UPDATE users SET is_online = 0 WHERE is_online IS NULL")
        
        conn.commit()
        conn.close()
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    migrate_user_status()