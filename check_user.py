#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

with app.app_context():
    # Try to find the specific user mentioned in the error
    user_id = '2bba1874-cdde-47c4-8a86-d47e411f786e'
    user = User.query.get(user_id)
    
    if user:
        print(f"User found: {user.username} ({user.email})")
        print(f"User last_active: {user.last_active}")
    else:
        print(f"User with ID {user_id} not found in database")
        
    # List all users
    all_users = User.query.all()
    print(f"Total users in database: {len(all_users)}")
    for u in all_users:
        print(f"  - {u.id}: {u.username} ({u.email})")