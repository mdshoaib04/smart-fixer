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
import uuid

with app.app_context():
    # Print the actual database URI being used
    print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    
    # Create a test user to ensure the table structure is correct
    try:
        # Check if any users exist
        user_count = User.query.count()
        print(f"Number of users in database: {user_count}")
        
        # If no users exist, create a test user
        if user_count == 0:
            print("Creating test user...")
            test_user = User()
            test_user.id = str(uuid.uuid4())
            test_user.username = "testuser"
            test_user.email = "test@example.com"
            test_user.set_password("testpassword")
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully")
        
        # Try to query a specific user (like in the error)
        user = User.query.first()
        if user:
            print("Successfully queried user:", user.id)
            # Try to access the last_active attribute
            print("User last_active:", user.last_active)
        else:
            print("No users found in database")
            
    except Exception as e:
        print("Error querying database:", e)
        import traceback
        traceback.print_exc()