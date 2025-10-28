import requests
import json

# Create a session for user 1 (test_user)
session1 = requests.Session()
login_response1 = session1.post('http://localhost:5000/api/login', json={
    "email": "test@example.com",
    "password": "password123"
})

print("Login status for test_user:", login_response1.status_code)

# Create a session for user 2 (another_user)
session2 = requests.Session()
login_response2 = session2.post('http://localhost:5000/api/login', json={
    "email": "another@example.com",
    "password": "password123"
})

print("Login status for another_user:", login_response2.status_code)

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
    
    # User 1 accepts the friend request
    # First, find the notification ID for the friend request
    notifications = notifications_response.json()
    friend_request_notification = None
    for notification in notifications:
        if notification.get('type') == 'friend_request':
            friend_request_notification = notification
            break
    
    if friend_request_notification:
        notification_id = friend_request_notification['id']
        print(f"Accepting friend request with notification ID: {notification_id}")
        
        accept_response = session1.post(f'http://localhost:5000/api/notifications/{notification_id}/respond', json={
            "action": "accept"
        })
        print("Accept status:", accept_response.status_code)
        print("Accept response:", accept_response.json())
        
        # Check the friendship status
        search_response2 = session2.get('http://localhost:5000/api/search-users?q=test')
        print("Search status after accepting:", search_response2.status_code)
        search_data2 = search_response2.json()
        print("Search response after accepting:", search_data2)