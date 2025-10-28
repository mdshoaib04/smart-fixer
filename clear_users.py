#!/usr/bin/env python3
"""
Script to clear all users and related data from the SmartFixer database.
This script will delete all users along with their posts, comments, friendships, messages, etc.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Post, PostLike, Comment, Friendship, Message, Group, GroupMember, Notification, CodeHistory, TimeSpent, OAuth

def clear_all_users():
    """Clear all users and related data from the database."""
    with app.app_context():
        try:
            print("Starting to clear all users and related data...")
            
            # Delete all records in the correct order to respect foreign key constraints
            print("Deleting OAuth records...")
            OAuth.query.delete()
            
            print("Deleting TimeSpent records...")
            TimeSpent.query.delete()
            
            print("Deleting CodeHistory records...")
            CodeHistory.query.delete()
            
            print("Deleting Notification records...")
            Notification.query.delete()
            
            print("Deleting GroupMember records...")
            GroupMember.query.delete()
            
            print("Deleting Group records...")
            Group.query.delete()
            
            print("Deleting Message records...")
            Message.query.delete()
            
            print("Deleting Friendship records...")
            Friendship.query.delete()
            
            print("Deleting PostLike records...")
            PostLike.query.delete()
            
            print("Deleting Comment records...")
            Comment.query.delete()
            
            print("Deleting Post records...")
            Post.query.delete()
            
            print("Deleting User records...")
            User.query.delete()
            
            # Commit all deletions
            db.session.commit()
            
            print("✅ Successfully cleared all users and related data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error clearing users: {str(e)}")
            raise e

if __name__ == "__main__":
    # For automated execution, we'll proceed directly
    print("⚠️  This will DELETE ALL USERS and related data.")
    print("Proceeding with deletion...")
    clear_all_users()
    print("✅ Database cleanup completed!")
