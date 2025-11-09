#!/usr/bin/env python3
"""
Direct database check
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def check_db():
    """Check database directly"""
    with app.app_context():
        try:
            # Check if follow_request_id column exists
            result = db.engine.execute("SELECT * FROM notifications LIMIT 1")
            columns = [column[0] for column in result.cursor.description]
            print("Notification table columns:", columns)
            
            # Check a specific notification
            result = db.engine.execute("SELECT id, user_id, message, type, follow_request_id FROM notifications WHERE type='follow_request' LIMIT 1")
            row = result.fetchone()
            if row:
                print("Sample follow request notification:")
                print(f"  ID: {row[0]}")
                print(f"  User ID: {row[1]}")
                print(f"  Message: {row[2]}")
                print(f"  Type: {row[3]}")
                print(f"  Follow Request ID: {row[4]}")
            else:
                print("No follow request notifications found")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    check_db()