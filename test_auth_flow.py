#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import json
import requests

# Load environment variables
load_dotenv()

def test_auth_flow():
    # Base URL for the application
    base_url = "http://localhost:5000"
    
    # Test signup with a new user
    print("Testing signup flow...")
    signup_data = {
        'name': 'Flow Test User',
        'username': 'flowtestuser',
        'email': 'flowtest@example.com',
        'password': 'flowtestpassword'
    }
    
    try:
        signup_response = requests.post(
            f"{base_url}/api/signup",
            json=signup_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Signup response status: {signup_response.status_code}")
        print(f"Signup response headers: {dict(signup_response.headers)}")
        print(f"Signup response text: {signup_response.text}")
        
        # Try to parse JSON response
        try:
            response_data = signup_response.json()
            print(f"Signup response data: {response_data}")
            
            if response_data.get('success'):
                print("Signup successful!")
            else:
                print("Signup failed!")
                return
        except json.JSONDecodeError:
            print("Could not parse JSON response")
            return
        
        # Test login with the new user
        print("\nTesting login flow...")
        login_data = {
            'email': 'flowtest@example.com',
            'password': 'flowtestpassword'
        }
        
        login_response = requests.post(
            f"{base_url}/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response text: {login_response.text}")
        
        try:
            login_data = login_response.json()
            print(f"Login response data: {login_data}")
            
            if login_data.get('success'):
                print("Login successful!")
            else:
                print("Login failed!")
        except json.JSONDecodeError:
            print("Could not parse JSON response for login")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the application is running.")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_auth_flow()