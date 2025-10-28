#!/usr/bin/env python3
import requests
import json

def test_routes():
    base_url = "http://localhost:5000"
    
    # Test if the new routes exist
    try:
        # Test the follow user route
        follow_response = requests.post(f"{base_url}/api/follow-user", 
                                       json={"user_id": "test-id"},
                                       headers={"Content-Type": "application/json"})
        print(f"Follow user route status: {follow_response.status_code}")
        print(f"Follow user route response: {follow_response.text}")
        
        # Test the user profile route
        profile_response = requests.get(f"{base_url}/user/test-id")
        print(f"User profile route status: {profile_response.status_code}")
        print(f"User profile route response: {profile_response.text[:100]}...")
        
    except Exception as e:
        print(f"Error testing routes: {e}")

if __name__ == '__main__':
    test_routes()