#!/usr/bin/env python3
"""
Cleanup test data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import Notification, FollowRequest

def cleanup_test_data():
    """Cleanup test data"""
    with app.app_context():
        try:
            # Delete all notifications
            Notification.query.delete()
            
            # Delete all follow requests
            FollowRequest.query.delete()
            
            db.session.commit()
            print("Test data cleaned up successfully")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up test data: {e}")

if __name__ == '__main__':
    cleanup_test_data()