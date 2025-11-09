#!/usr/bin/env python3
"""
Direct database schema update for notifications table
This script updates the notifications table structure directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def update_notification_schema():
    """Update the notifications table schema directly"""
    with app.app_context():
        # Connect to the database
        conn = db.engine.connect()
        
        try:
            # Check if the columns we need exist
            result = conn.execute("PRAGMA table_info(notifications)")
            columns = [row[1] for row in result.fetchall()]
            
            print("Current columns in notifications table:", columns)
            
            # Add message column if it doesn't exist
            if 'message' not in columns:
                print("Adding message column...")
                conn.execute("ALTER TABLE notifications ADD COLUMN message TEXT")
            
            # Add read_status column if it doesn't exist
            if 'read_status' not in columns:
                print("Adding read_status column...")
                conn.execute("ALTER TABLE notifications ADD COLUMN read_status BOOLEAN DEFAULT 0")
            
            # Remove old columns if they exist
            if 'content' in columns:
                print("Removing content column...")
                # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
                conn.execute("""
                    CREATE TABLE notifications_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id VARCHAR NOT NULL,
                        message TEXT,
                        type VARCHAR NOT NULL,
                        from_user_id VARCHAR,
                        read_status BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users (id),
                        FOREIGN KEY(from_user_id) REFERENCES users (id)
                    )
                """)
                
                # Copy data from old table
                conn.execute("""
                    INSERT INTO notifications_new (id, user_id, type, from_user_id, read_status, created_at)
                    SELECT id, user_id, type, from_user_id, read, created_at FROM notifications
                """)
                
                # Drop old table and rename new one
                conn.execute("DROP TABLE notifications")
                conn.execute("ALTER TABLE notifications_new RENAME TO notifications")
            
            print("Notifications table schema updated successfully!")
            
        except Exception as e:
            print(f"Error updating schema: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    update_notification_schema()