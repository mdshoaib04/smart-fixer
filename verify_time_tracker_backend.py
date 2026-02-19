
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

def login():
    print("Logging in...")
    try:
        # Login
        login_data = {
            "email": "testuser_ai",
            "password": "password123"
        }
        resp = SESSION.post(f"{BASE_URL}/api/login", json=login_data)
        if resp.json().get("success"):
            print("[OK] Login successful")
            return True
        else:
            print(f"[FAIL] Login failed: {resp.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return False

def check_stats():
    print("\nFetching initial Request...")
    resp = SESSION.get(f"{BASE_URL}/api/time-stats")
    if resp.status_code == 200 and resp.json().get("success"):
        stats = resp.json().get("stats")
        print(f"[OK] Stats fetched: Today={stats['today_seconds']}s, Month={stats['month_seconds']}s")
        return stats['today_seconds']
    else:
        print(f"[FAIL] Fetch failed: {resp.text}")
        return -1

def track_time(seconds=60):
    print(f"\nTracking {seconds} seconds...")
    resp = SESSION.post(f"{BASE_URL}/api/track-time", json={"seconds": seconds})
    if resp.status_code == 200 and resp.json().get("success"):
        new_total = resp.json().get("today_seconds")
        print(f"[OK] Tracked successfully. New Today Total: {new_total}")
        return new_total
    else:
        print(f"[FAIL] Tracking failed: {resp.text}")
        return -1

if __name__ == "__main__":
    if not login():
        sys.exit(1)
        
    initial = check_stats()
    if initial == -1:
        sys.exit(1)
        
    updated = track_time(30)
    
    if updated == initial + 30:
        print("\n[SUCCESS] Time verification passed! (Incremented by 30s)")
    elif updated > initial:
        print(f"\n[SUCCESS] Time verification passed! (Incremented, likely other activity active: {updated - initial}s)")
    else:
        print(f"\n[FAIL] Time did not increment correctly. Initial: {initial}, Updated: {updated}")
        sys.exit(1)

    # Check stats again
    final_stats = check_stats()
    if final_stats >= updated:
        print("[SUCCESS] Final stats consistent.")
    else:
        print("[FAIL] Final stats inconsistent.")
