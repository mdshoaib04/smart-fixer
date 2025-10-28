import requests
import json

# Create a session for the first user
session1 = requests.Session()

# Login as the first user (test@example.com)
login_response1 = session1.post('http://localhost:5000/api/login', json={
    "email": "test@example.com",
    "password": "password123"
})

print("Login status for user 1:", login_response1.status_code)

# Create a session for the second user
session2 = requests.Session()

# Login as the second user (another@example.com)
login_response2 = session2.post('http://localhost:5000/api/login', json={
    "email": "another@example.com",
    "password": "password123"
})

print("Login status for user 2:", login_response2.status_code)

# User 2 searches for user 1
search_response = session2.get('http://localhost:5000/api/search-users?q=test')
print("Search status:", search_response.status_code)
search_data = search_response.json()
print("Search response:", search_data)

# User 2 tries to follow user 1
if search_data.get('users'):
    target_user_id = search_data['users'][0]['id']
    print(f"User 2 trying to follow user 1 with ID: {target_user_id}")
    
    follow_response = session2.post('http://localhost:5000/api/follow-user', json={
        "user_id": target_user_id
    })
    print("Follow status:", follow_response.status_code)
    print("Follow response:", follow_response.json())
    
    # Check if user 1 can see the follow request
    notifications_response = session1.get('http://localhost:5000/api/notifications')
    print("Notifications status:", notifications_response.status_code)
    print("Notifications response:", notifications_response.json())