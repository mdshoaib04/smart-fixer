#!/usr/bin/env python3
"""
Migration script to add last_active field to User model and update existing users.
This script should be run once after updating the models.py file.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from datetime import datetime

def migrate_user_presence():
    """Add last_active field to existing users"""
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        print(f"Found {len(users)} users to update...")
        
        for user in users:
            # If last_active is not set, initialize it to last_seen or current time
            if not user.last_active:
                user.last_active = user.last_seen or datetime.now()
                print(f"Updated user {user.username} with last_active: {user.last_active}")
        
        # Commit all changes
        try:
            db.session.commit()
            print("Successfully updated all users with last_active field!")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating users: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting user presence migration...")
    if migrate_user_presence():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)