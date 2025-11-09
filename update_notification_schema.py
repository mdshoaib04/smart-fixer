#!/usr/bin/env python3
"""
Database update script for the notification schema
This script adds the follow_request_id column to the notifications table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def update_notification_schema():
    """Add follow_request_id column to notifications table"""
    with app.app_context():
        try:
            # Add the follow_request_id column to notifications table
            db.engine.execute("ALTER TABLE notifications ADD COLUMN follow_request_id INTEGER")
            print("Successfully added follow_request_id column to notifications table")
        except Exception as e:
            # Column might already exist
            if "duplicate column name" in str(e).lower():
                print("Column follow_request_id already exists in notifications table")
            else:
                print(f"Error adding column: {e}")
                return False
        return True

if __name__ == '__main__':
    update_notification_schema()