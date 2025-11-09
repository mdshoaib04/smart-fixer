#!/usr/bin/env python3
"""
Debug script to check notifications and follow requests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import Notification, FollowRequest, User

def debug_notifications():
    """Debug notifications and follow requests"""
    with app.app_context():
        print("=== Notifications ===")
        notifications = Notification.query.all()
        for notif in notifications:
            print(f"ID: {notif.id}, User: {notif.user_id}, Message: {notif.message}, Type: {notif.type}, Follow Request ID: {notif.follow_request_id}")
        
        print("\n=== Follow Requests ===")
        follow_requests = FollowRequest.query.all()
        for req in follow_requests:
            print(f"ID: {req.id}, From: {req.from_user_id}, To: {req.to_user_id}, Status: {req.status}")
        
        print("\n=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Name: {user.full_name}")

if __name__ == '__main__':
    debug_notifications()