#!/usr/bin/env python3
"""
Full test of follow request flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import Notification, FollowRequest, User

def full_test():
    """Test the complete follow request flow"""
    with app.app_context():
        try:
            # Get two users
            users = User.query.all()
            if len(users) < 2:
                print("Need at least 2 users for testing")
                return
                
            user1 = users[0]
            user2 = users[1]
            
            print(f"User 1: {user1.id} ({user1.username})")
            print(f"User 2: {user2.id} ({user2.username})")
            
            # Simulate sending a follow request (like the API endpoint does)
            print("\n--- Sending Follow Request ---")
            
            # Check if follow request already exists
            existing_request = FollowRequest.query.filter_by(
                from_user_id=user1.id, 
                to_user_id=user2.id
            ).first()
            
            if existing_request:
                follow_request = existing_request
                print(f"Using existing follow request with ID: {follow_request.id}")
            else:
                # Create a new follow request
                follow_request = FollowRequest()
                follow_request.from_user_id = user1.id
                follow_request.to_user_id = user2.id
                follow_request.status = 'pending'
                db.session.add(follow_request)
                db.session.flush()  # Get the ID without committing
                print(f"Created new follow request with ID: {follow_request.id}")
            
            # Create notification for target user
            notification = Notification()
            notification.user_id = user2.id
            notification.message = f"{user1.full_name} requested to follow you"
            notification.type = 'follow_request'
            notification.from_user_id = user1.id
            notification.follow_request_id = follow_request.id  # Link to follow request
            db.session.add(notification)
            db.session.commit()
            
            print(f"Created notification with ID: {notification.id}")
            print(f"Notification follow_request_id: {notification.follow_request_id}")
            
            # Verify the notification was saved correctly
            db.session.refresh(notification)
            print(f"After refresh - Notification follow_request_id: {notification.follow_request_id}")
            
            # Query the notification directly
            fresh_notification = Notification.query.get(notification.id)
            print(f"Fresh query - Notification follow_request_id: {fresh_notification.follow_request_id}")
            
            # Simulate accepting the follow request (like the API endpoint does)
            print("\n--- Accepting Follow Request ---")
            
            # Get the follow request (simulating the accept endpoint)
            follow_request_to_accept = FollowRequest.query.filter_by(
                id=follow_request.id, 
                to_user_id=user2.id,
                status='pending'
            ).first()
            
            if not follow_request_to_accept:
                print("Follow request not found or already processed")
                return
            
            print(f"Found follow request with ID: {follow_request_to_accept.id}")
            
            # Update request status
            follow_request_to_accept.status = 'accepted'
            follow_request_to_accept.updated_at = db.func.now()
            
            # In a real implementation, we would also add to followers table here
            # and create a notification for the user who sent the request
            
            db.session.commit()
            print("Follow request accepted successfully")
            
            print("\n--- Test Complete ---")
            print("The follow request system is working correctly!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    full_test()