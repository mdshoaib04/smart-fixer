import requests
import json

# Create a session
session = requests.Session()

# Signup a new user
signup_response = session.post('http://localhost:5000/api/signup', json={
    "name": "Another User",
    "email": "another@example.com",
    "password": "password123"
})

print("Signup status:", signup_response.status_code)
print("Signup response:", signup_response.json())

# Login as the new user
login_response = session.post('http://localhost:5000/api/login', json={
    "email": "another@example.com",
    "password": "password123"
})

print("Login status:", login_response.status_code)
print("Login response:", login_response.json())

# Search for the first user
search_response = session.get('http://localhost:5000/api/search-users?q=test')
print("Search status:", search_response.status_code)
print("Search response:", search_response.json())

# Try to follow the first user
if search_response.status_code == 200:
    users = search_response.json().get('users', [])
    if users:
        target_user_id = users[0]['id']
        print(f"Trying to follow user with ID: {target_user_id}")
        
        follow_response = session.post('http://localhost:5000/api/follow-user', json={
            "user_id": target_user_id
        })
        print("Follow status:", follow_response.status_code)
        print("Follow response:", follow_response.json())