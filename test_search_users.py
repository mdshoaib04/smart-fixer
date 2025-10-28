import requests
import json

# Create a session
session = requests.Session()

# First, login as the test user
login_response = session.post('http://localhost:5000/api/login', json={
    "email": "test@example.com",
    "password": "password123"
})

print("Login status:", login_response.status_code)
print("Login response:", login_response.json())

# Search for users
search_response = session.get('http://localhost:5000/api/search-users?q=user')
print("Search status:", search_response.status_code)
print("Search response:", search_response.json())