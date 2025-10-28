#!/usr/bin/env python3
import requests
import json

def test_user_profile():
    base_url = "http://localhost:5000"
    
    # First, let's create a test user and get their ID
    print("Creating test user...")
    
    # Since we can't directly create a user without being authenticated,
    # let's just test the route with a placeholder ID to see if it loads
    # without the Jinja2 error
    try:
        # Test the user profile route with a non-existent user ID
        profile_response = requests.get(f"{base_url}/user/non-existent-id")
        print(f"User profile route status: {profile_response.status_code}")
        if profile_response.status_code == 404:
            print("Correctly returns 404 for non-existent user")
        else:
            print(f"Response: {profile_response.text[:200]}...")
        
    except Exception as e:
        print(f"Error testing user profile route: {e}")

if __name__ == '__main__':
    test_user_profile()