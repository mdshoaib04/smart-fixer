#!/usr/bin/env python3
"""
Database update script for the follow system
This script creates the necessary tables for the follow system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import FollowRequest, Follower, Notification

def update_database():
    """Create the new tables for the follow system"""
    with app.app_context():
        # Create all tables (this will create the new tables if they don't exist)
        db.create_all()
        print("Database updated successfully!")
        print("Created tables:")
        print("- follow_requests")
        print("- followers")
        print("- Updated notifications table structure")

if __name__ == '__main__':
    update_database()