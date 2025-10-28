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
    # Print the actual database URI being used
    print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    
    # Try to authenticate the existing user
    try:
        print("Attempting to authenticate existing user...")
        user = User.query.filter_by(email="test@example.com").first()
        if user:
            print(f"User found: {user.username} ({user.email})")
            print(f"User ID: {user.id}")
            
            # Test password checking
            if user.check_password("testpassword"):
                print("Password verification successful!")
            else:
                print("Password verification failed!")
                print("Setting password and trying again...")
                user.set_password("testpassword")
                db.session.commit()
                
                # Try again
                if user.check_password("testpassword"):
                    print("Password verification successful after update!")
                else:
                    print("Password verification still failed!")
        else:
            print("User not found!")
            
    except Exception as e:
        print("Error authenticating user:", e)
        import traceback
        traceback.print_exc()