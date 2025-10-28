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
    
    # Try to create a test user
    try:
        print("Creating test user...")
        test_user = User()
        test_user.id = str(uuid.uuid4())
        test_user.username = "testuser"
        test_user.email = "test@example.com"
        test_user.set_password("testpassword")
        
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully")
        
        # Try to authenticate the user
        user = User.query.filter_by(email="test@example.com").first()
        if user and user.check_password("testpassword"):
            print("Authentication successful!")
        else:
            print("Authentication failed!")
            
    except Exception as e:
        print("Error creating user:", e)
        import traceback
        traceback.print_exc()
        db.session.rollback()