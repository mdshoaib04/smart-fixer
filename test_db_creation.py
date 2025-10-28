import requests
import time

# Wait for the server to start
time.sleep(5)

# Create a new user to trigger database creation
signup_response = requests.post('http://localhost:5000/api/signup', json={
    "name": "Database Test User",
    "email": "dbtest@example.com",
    "password": "password123"
})

print("Signup status:", signup_response.status_code)
print("Signup response:", signup_response.json())

# Login as the new user
login_response = requests.post('http://localhost:5000/api/login', json={
    "email": "dbtest@example.com",
    "password": "password123"
})

print("Login status:", login_response.status_code)
print("Login response:", login_response.json())