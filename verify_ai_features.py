import requests
import json
import time

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

def login():
    print("Logging in...")
    # Assuming a test user exists or we can create one. 
    # For this verification, we'll try to log in as 'testuser' if exists, or create one.
    try:
        # Try signup first to ensure user exists
        signup_data = {
            "username": "testuser_ai",
            "email": "test_ai@example.com",
            "password": "password123",
            "name": "Test User"
        }
        SESSION.post(f"{BASE_URL}/api/signup", json=signup_data)
        
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

def test_dictionary():
    print("\nTesting Dictionary (Code Generation)...")
    data = {"prompt": "sum of two numbers", "language": "python"}
    resp = SESSION.post(f"{BASE_URL}/api/dictionary", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        print(f"[OK] Dictionary Success: {resp.json().get('result')[:50]}...")
    else:
        print(f"[FAIL] Dictionary Failed: {resp.text}")

def test_translate():
    print("\nTesting Translation...")
    code = "def add(a, b): return a + b"
    data = {"code": code, "target_lang": "java", "source_lang": "python"}
    resp = SESSION.post(f"{BASE_URL}/api/translate", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        print(f"[OK] Translation Success: {resp.json().get('result')[:50]}...")
    else:
        print(f"[FAIL] Translation Failed: {resp.text}")

def test_review():
    print("\nTesting Review...")
    code = "def add(a, b) return a + b" # Missing colon
    data = {"code": code, "language": "python"}
    resp = SESSION.post(f"{BASE_URL}/api/review", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        print(f"[OK] Review Success: {resp.json().get('result')[:50]}...")
    else:
        print(f"[FAIL] Review Failed: {resp.text}")

def test_explain():
    print("\nTesting Explanation...")
    code = "print('Hello')"
    data = {"code": code, "language": "python", "role": "student"}
    resp = SESSION.post(f"{BASE_URL}/api/explain", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        print(f"[OK] Explanation Success: {resp.json().get('result')[:50]}...")
    else:
        print(f"[FAIL] Explanation Failed: {resp.text}")

def test_question():
    print("\nTesting AI Question...")
    data = {"question": "How do I print in Python?", "code": "", "language": "python"}
    resp = SESSION.post(f"{BASE_URL}/api/question", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        print(f"[OK] Question Success: {resp.json().get('result')[:50]}...")
    else:
        print(f"[FAIL] Question Failed: {resp.text}")

def test_compile_web():
    print("\nTesting Web Compilation...")
    code = "<h1>Hello</h1>"
    data = {"code": code, "language": "html"}
    resp = SESSION.post(f"{BASE_URL}/api/execute", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        res = resp.json()
        if res.get("type") == "web" and res.get("url"):
            print(f"[OK] Web Compile Success: URL={res.get('url')}")
        else:
            print(f"[FAIL] Web Compile Unexpected Response: {res}")
    else:
        print(f"[FAIL] Web Compile Failed: {resp.text}")

def test_compile_interactive():
    print("\nTesting Interactive Compilation (Start)...")
    code = "print('Hello')"
    data = {"code": code, "language": "python"}
    resp = SESSION.post(f"{BASE_URL}/api/execute", json=data)
    if resp.status_code == 200 and resp.json().get("success"):
        res = resp.json()
        if res.get("type") == "interactive" and res.get("session_id"):
            print(f"[OK] Interactive Start Success: SessionID={res.get('session_id')}")
        else:
            print(f"[FAIL] Interactive Start Unexpected Response: {res}")
    else:
        print(f"[FAIL] Interactive Start Failed: {resp.text}")

if __name__ == "__main__":
    if login():
        test_dictionary()
        test_translate()
        test_review()
        test_explain()
        test_question()
        test_compile_web()
        test_compile_interactive()
