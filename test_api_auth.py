#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def test_signup():
    with app.test_client() as client:
        # Test signup with a new user
        signup_data = {
            'name': 'Test User',
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpassword123'
        }
        
        print("Testing signup...")
        response = client.post('/api/signup', 
                              data=json.dumps(signup_data),
                              content_type='application/json')
        
        print(f"Signup response status: {response.status_code}")
        print(f"Signup response data: {response.get_json()}")
        return response

def test_login():
    with app.test_client() as client:
        # Test login with existing user
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        
        print("Testing login...")
        response = client.post('/api/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response data: {response.get_json()}")
        return response

if __name__ == '__main__':
    print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    
    # Test signup
    signup_response = test_signup()
    
    # Test login
    login_response = test_login()