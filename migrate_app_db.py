#!/usr/bin/env python3
"""
Migration script to add last_active column to User model in app.db.
"""

import sys
import os
import sqlite3

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_app_db():
    """Add last_active column to app.db users table"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    
    if not os.path.exists(db_path):
        print("app.db not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if last_active column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'last_active' in column_names:
            print("last_active column already exists in app.db")
            conn.close()
            return True
        
        print("Adding last_active column to app.db users table...")
        
        # Add the last_active column
        cursor.execute("ALTER TABLE users ADD COLUMN last_active DATETIME")
        conn.commit()
        print("Successfully added last_active column to app.db users table!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error migrating app.db: {e}")
        return False

if __name__ == "__main__":
    print("Starting app.db migration...")
    if migrate_app_db():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)