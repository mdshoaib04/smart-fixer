#!/usr/bin/env python3
"""
Verification script to test the new profile API endpoints
"""
import requests
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    base_url = "http://localhost:5000"
    
    print("Testing new profile API endpoints...")
    
    # Test user posts endpoint
    try:
        response = requests.get(f"{base_url}/api/user-stats")
        if response.status_code == 200:
            data = response.json()
            print("✓ /api/user-stats endpoint working")
            print(f"  Post count: {data.get('post_count', 'N/A')}")
            print(f"  Follower count: {data.get('follower_count', 'N/A')}")
            print(f"  Following count: {data.get('following_count', 'N/A')}")
        else:
            print(f"✗ /api/user-stats endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing /api/user-stats: {e}")
    
    # Since we can't easily get a user ID without being logged in,
    # we'll just verify the endpoints exist by checking if they return proper error codes
    # when accessed without proper authentication
    
    endpoints_to_test = [
        "/api/user/1/posts",
        "/api/user/1/saved-posts", 
        "/api/user/1/liked-posts",
        "/api/user/1/followers",
        "/api/user/1/following"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            # We expect 401/403 for unauthorized access, not 404
            if response.status_code in [401, 403, 200]:
                print(f"✓ {endpoint} endpoint exists (status: {response.status_code})")
            else:
                print(f"? {endpoint} endpoint exists but returned unexpected status: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing {endpoint}: {e}")

if __name__ == "__main__":
    test_api_endpoints()