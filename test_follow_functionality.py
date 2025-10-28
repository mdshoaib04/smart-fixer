#!/usr/bin/env python3
"""
Test script to verify the follow functionality works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import User, Friendship, Notification
import json

def test_follow_flow():
    """Test the complete follow request flow"""
    with app.app_context():
        # Create test users
        user1 = User()
        user1.username = "testuser1"
        user1.email = "test1@example.com"
        user1.first_name = "Test"
        user1.last_name = "User1"
        user1.set_password("password123")
        
        user2 = User()
        user2.username = "testuser2"
        user2.email = "test2@example.com"
        user2.first_name = "Test"
        user2.last_name = "User2"
        user2.set_password("password123")
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print(f"Created users: {user1.username} and {user2.username}")
        
        # User1 sends follow request to User2
        friendship = Friendship()
        friendship.user_id = user1.id
        friendship.friend_id = user2.id
        friendship.status = 'pending'
        db.session.add(friendship)
        
        notif = Notification()
        notif.user_id = user2.id
        notif.type = 'friend_request'
        notif.content = f"{user1.first_name} sent you a friend request"
        notif.from_user_id = user1.id
        db.session.add(notif)
        db.session.commit()
        
        print("User1 sent follow request to User2")
        
        # Check notifications for User2
        user2_notifications = Notification.query.filter_by(user_id=user2.id).all()
        print(f"User2 has {len(user2_notifications)} notifications")
        
        # User2 accepts the follow request
        friendship.status = 'accepted'
        notif.content = f"{user1.first_name} started following you"
        
        # Create notification for User1
        user1_notif = Notification()
        user1_notif.user_id = user1.id
        user1_notif.type = 'friend_request_accepted'
        user1_notif.content = f"{user2.first_name} accepted your friend request"
        user1_notif.from_user_id = user2.id
        db.session.add(user1_notif)
        db.session.commit()
        
        print("User2 accepted follow request from User1")
        
        # Check that User1 now follows User2
        user1_following = Friendship.query.filter_by(
            user_id=user1.id, 
            friend_id=user2.id, 
            status='accepted'
        ).first()
        
        if user1_following:
            print("✓ User1 is now following User2")
        else:
            print("✗ User1 is not following User2")
        
        # Check that User2 is followed by User1
        user2_followers = Friendship.query.filter_by(
            user_id=user2.id, 
            friend_id=user1.id, 
            status='accepted'
        ).first()
        
        if user2_followers:
            print("✓ User2 is followed by User1")
        else:
            print("✗ User2 is not followed by User1")
        
        # User2 clicks "Follow Back" on the notification
        # This should create a new pending request from User2 to User1
        reverse_friendship = Friendship()
        reverse_friendship.user_id = user2.id
        reverse_friendship.friend_id = user1.id
        reverse_friendship.status = 'pending'  # Should be pending, not accepted
        db.session.add(reverse_friendship)
        
        # Update User1's notification
        user1_notif.content = f"{user2.first_name} requested to follow you"
        db.session.commit()
        
        print("User2 clicked 'Follow Back' - sent follow request to User1")
        
        # Check that the reverse friendship is pending
        reverse_friendship_check = Friendship.query.filter_by(
            user_id=user2.id, 
            friend_id=user1.id, 
            status='pending'
        ).first()
        
        if reverse_friendship_check:
            print("✓ User2's follow request to User1 is pending")
        else:
            print("✗ User2's follow request to User1 is not pending")
        
        # User1 accepts User2's follow request
        if reverse_friendship_check:
            reverse_friendship_check.status = 'accepted'
        
        # Update notification
        user1_notif.content = f"You and {user2.first_name} now follow each other"
        
        # Create notification for User2
        user2_notif = Notification()
        user2_notif.user_id = user2.id
        user2_notif.type = 'follow_back_accepted'
        user2_notif.content = f"You and {user1.first_name} now follow each other"
        user2_notif.from_user_id = user1.id
        db.session.add(user2_notif)
        db.session.commit()
        
        print("User1 accepted User2's follow request")
        
        # Check that both users now follow each other
        user1_follows_user2 = Friendship.query.filter_by(
            user_id=user1.id, 
            friend_id=user2.id, 
            status='accepted'
        ).first()
        
        user2_follows_user1 = Friendship.query.filter_by(
            user_id=user2.id, 
            friend_id=user1.id, 
            status='accepted'
        ).first()
        
        if user1_follows_user2 and user2_follows_user1:
            print("✓ Both users now follow each other")
        else:
            print("✗ Mutual follow relationship not established")
        
        # Clean up test data
        db.session.delete(user1)
        db.session.delete(user2)
        db.session.commit()
        
        print("Test completed and cleaned up")

if __name__ == "__main__":
    test_follow_flow()