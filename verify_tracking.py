
import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
STATS_URL = f"{BASE_URL}/api/user-stats"
TRACK_URL = f"{BASE_URL}/api/track-time"

# Test User Credentials (assuming admin/password or similar exists, or creating one)
# I will try to use the session from the browser if I could, but here I need credentials.
# I'll try to register a new user or rely on existing 'admin' user if I know credentials.
# Since I don't know credentials, I will look at 'check_db_detailed.py' or similar to find a user.
# Or I can just try to register a temp user.

def register_and_test():
    session = requests.Session()
    
    # Generate unique user
    username = f"tester_{int(time.time())}"
    email = f"{username}@test.com"
    password = "password123"
    name = "Test User"
    
    print(f"Registering user: {username}")
    reg_url = f"{BASE_URL}/api/signup"
    reg_data = {
        "username": username,
        "email": email,
        "password": password,
        "name": name
    }
    
    # Try register
    res = session.post(reg_url, json=reg_data)
    print(f"Registration Response: {res.status_code} - {res.text}")
        
    # Login
    print("Logging in...")
    login_url = f"{BASE_URL}/api/login"
    login_data = {
        "email": email, # The API accepts email or username in 'email' field
        "password": password
    }
    res = session.post(login_url, json=login_data)
    print(f"Login Response: {res.status_code} - {res.text}")
    
    # Check stats (should be 0)
    print("Checking initial stats...")
    res = session.get(STATS_URL)
    if res.status_code != 200:
        print(f"Failed to get stats: {res.status_code}")
        return
        
    stats = res.json()
    print(f"Initial Stats: Today={stats.get('today_minutes')}m, Streak={stats.get('current_streak')}")
    
    # Track time (60 seconds)
    print("Tracking 60 seconds...")
    res = session.post(TRACK_URL, json={"duration": 60})
    print(f"Track Response: {res.json()}")
    
    # Check stats again
    res = session.get(STATS_URL)
    stats = res.json()
    print(f"Updated Stats: Today={stats.get('today_minutes')}m, Streak={stats.get('current_streak')}")
    
    if stats.get('today_minutes') >= 1:
        print("SUCCESS: Time tracking works!")
    else:
        print("FAILURE: Time tracking did not update minutes.")

if __name__ == "__main__":
    try:
        register_and_test()
    except Exception as e:
        print(f"Error: {e}")
