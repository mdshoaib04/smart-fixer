import requests
import time

# Wait for the server to start
time.sleep(5)

# Create a session
session = requests.Session()

# Login as a user
login_response = session.post('http://localhost:5000/api/login', json={
    "email": "test@example.com",
    "password": "password123"
})

print("Login status:", login_response.status_code)

# Get user stats
stats_response = session.get('http://localhost:5000/api/user-stats')
print("Stats status:", stats_response.status_code)
if stats_response.status_code == 200:
    print("Stats response:", stats_response.json())

# Search for users
search_response = session.get('http://localhost:5000/api/search-users?q=another')
print("Search status:", search_response.status_code)
if search_response.status_code == 200:
    print("Search response:", search_response.json())