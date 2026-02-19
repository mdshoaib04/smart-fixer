
import requests
import json
import time
from datetime import datetime, date, timedelta
import sys
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000"

def get_session():
    return requests.Session()

def register_user(session, username):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Registering user: {username}")
    reg_url = f"{BASE_URL}/api/signup"
    reg_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "password123",
        "name": "Test User"
    }
    res = session.post(reg_url, json=reg_data)
    if res.status_code != 200:
        print(f"Registration failed: {res.text}")
        return False
    return True

def login_user(session, username):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logging in...")
    login_url = f"{BASE_URL}/api/login"
    login_data = {
        "email": f"{username}@test.com",
        "password": "password123"
    }
    res = session.post(login_url, json=login_data)
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return False
    return True

def track_time(session, duration=60):
    track_url = f"{BASE_URL}/api/track-time"
    res = session.post(track_url, json={"duration": duration})
    return res.json()

def get_stats(session):
    stats_url = f"{BASE_URL}/api/user-stats"
    res = session.get(stats_url)
    return res.json()

# This function injects past data directly into DB to simulate history
# WE need to run this code in the context of the Flask app, or 
# create a special "backdoor" route. 
# Since we are running outside the app context here, and we can't easily import app 
# without side effects (if it runs server), we might need a separate script 
# OR we can just rely on the fact that we can manipulate the DB if we are on the same machine.
# But let's try to do it via a python script that imports app but NOT run it.

def simulate_past_activity(username):
    # This runs in a separate process/context to access DB directly
    sys.path.append(os.getcwd())
    from app import app, db
    from models import User, TimeSpent
    from datetime import date, timedelta
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print("User not found for simulation")
            return

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Simulating past activity for {username}...")
        
        # Scenario: 4 days of activity ending yesterday
        # Dates: Today-4, Today-3, Today-2, Today-1
        today = date.today()
        
        # Clear existing time logs for this user
        TimeSpent.query.filter_by(user_id=user.id).delete()
        
        history_days = 4
        for i in range(history_days, 0, -1):
            day = today - timedelta(days=i)
            # Add time record
            ts = TimeSpent(user_id=user.id, date=day, minutes=30)
            db.session.add(ts)
            
        # Manually set streak state as if they had tracked yesterday
        user.current_streak = 4
        user.longest_streak = 4
        user.last_streak_date = today - timedelta(days=1)
        
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Injected 4 days of history. User should have streak 4.")

def simulate_broken_streak(username):
    sys.path.append(os.getcwd())
    from app import app, db
    from models import User, TimeSpent
    from datetime import date, timedelta
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Simulating BROKEN streak for {username}...")
        
        # Scenario: Active 5 days ago, then stopped.
        today = date.today()
        user.last_streak_date = today - timedelta(days=5)
        user.current_streak = 10 # Was on a 10 day streak
        user.longest_streak = 10
        
        # Add that old record
        ts = TimeSpent(user_id=user.id, date=user.last_streak_date, minutes=60)
        db.session.add(ts)
        
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Injected broken streak (last active 5 days ago).")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'db_setup':
        action = sys.argv[2]
        user = sys.argv[3]
        if action == 'streak_build':
            simulate_past_activity(user)
        elif action == 'streak_break':
            simulate_broken_streak(user)
        sys.exit(0)

    # Main Test Flow
    session = get_session()
    username = f"real_tester_{int(time.time())}"
    
    # 1. Register & Login
    if not register_user(session, username): exit(1)
    if not login_user(session, username): exit(1)
    
    # 2. Test Real-time Tracking (Today)
    print(f"\n--- Scenario 1: Real-time Tracking (Today: {date.today()}) ---")
    initial_stats = get_stats(session)
    print(f"Initial Minutes: {initial_stats['today_minutes']}")
    
    print("Tracking 60 seconds of activity...")
    track_res = track_time(session, 60)
    
    stats = get_stats(session)
    print(f"Updated Minutes: {stats['today_minutes']}")
    if stats['today_minutes'] == initial_stats['today_minutes'] + 1:
        print("✅ Real-time tracking verified (+1 minute).")
    else:
        print("❌ Real-time tracking failed.")

    # 3. Test Streak Building
    print(f"\n--- Scenario 2: Streak Building (4 past days + Today) ---")
    # Call self to run DB setup in separate process
    import subprocess
    subprocess.run([sys.executable, __file__, 'db_setup', 'streak_build', username])
    
    # Refresh stats to see injection
    stats = get_stats(session)
    print(f"Streak before tracking today (simulated): {stats['current_streak']}") 
    # Note: API might show 4 if logic is correct, or 0 if strictly checking 'yesterday' logic without today's track.
    # Our API logic: if last_streak_date < yesterday, return 0. 
    # We set last_streak_date = yesterday. So it should return 4.
    
    print("Tracking activity for TODAY...")
    track_time(session, 60) # Track time to trigger streak update
    
    stats = get_stats(session)
    print(f"Streak after tracking: {stats['current_streak']}")
    
    if stats['current_streak'] == 5:
        print("✅ Streak correctly incremented to 5.")
    else:
        print(f"❌ Streak failed. Expected 5, got {stats['current_streak']}")

    # 4. Test Streak Breaking
    print(f"\n--- Scenario 3: Streak Breaking (Missed days) ---")
    subprocess.run([sys.executable, __file__, 'db_setup', 'streak_break', username])
    
    stats = get_stats(session)
    print(f"Streak state (simulated broken): {stats['current_streak']}") 
    # Should ideally be 0 or old value but displayed as 0?
    # Our API: if last_streak_date < yesterday (which it is, 5 days ago), returns 0.
    
    print("Tracking activity for TODAY (Reviving)...")
    track_time(session, 60)
    
    stats = get_stats(session)
    print(f"Streak after reviving: {stats['current_streak']}")
    print(f"Longest Streak preserved: {stats['longest_streak']}")
    
    if stats['current_streak'] == 1:
        print("✅ Streak correctly reset to 1.")
    else:
        print(f"❌ Streak reset failed. Expected 1, got {stats['current_streak']}")
        
    if stats['longest_streak'] >= 10:
        print("✅ Longest streak preserved/updated.")
    else:
        print(f"❌ Longest streak lost. Expected >= 10, got {stats['longest_streak']}")

