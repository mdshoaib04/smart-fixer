import requests
import json
import sys

BASE_URL = "http://localhost:5000"

# Login to get session cookie
session = requests.Session()

def login():
    print("Logging in...")
    try:
        signup_data = {
            "name": "Test User",
            "email": "test_trans@example.com",
            "password": "password123",
            "username": "test_trans_user"
        }
        session.post(f"{BASE_URL}/api/signup", json=signup_data)
    except:
        pass

    login_data = {
        "email": "test_trans@example.com",
        "password": "password123"
    }
    response = session.post(f"{BASE_URL}/api/login", json=login_data)
    if response.status_code == 200 and response.json().get('success'):
        print("Login successful")
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

def test_detect_language():
    print("\nTesting Language Detection...")
    
    # Test Python
    code_py = "def hello(): print('world')"
    resp_py = session.post(f"{BASE_URL}/api/detect-language", json={"code": code_py})
    try:
        print(f"Python Detection: {resp_py.json()}")
    except:
        print(f"Python Detection Failed (Raw): {resp_py.text}")
    
    # Test Shell
    code_sh = "#!/bin/bash\necho 'hello world'"
    resp_sh = session.post(f"{BASE_URL}/api/detect-language", json={"code": code_sh})
    try:
        print(f"Shell Detection: {resp_sh.json()}")
    except:
        print(f"Shell Detection Failed (Raw): {resp_sh.text}")
    
    try:
        if resp_py.json().get('language') == 'python' and resp_sh.json().get('language') == 'shell':
            print("✅ Language Detection Passed")
            return True
        else:
            print("❌ Language Detection Failed")
            return False
    except:
        return False

def test_translate_with_autodetect():
    print("\nTesting Translation with Auto-detect...")
    data = {
        "code": "System.out.println('Hello');",
        "to_lang": "python",
        "from_lang": "java" # Simulating what the frontend would send after auto-detect
    }
    response = session.post(f"{BASE_URL}/api/translate", json=data)
    result = response.json()
    
    if result.get('success') and 'result' in result:
        print("✅ Translation API Success")
        print(f"Result Preview: {result['result'][:50]}...")
        return True
    else:
        print(f"❌ Translation API Failed: {result}")
        return False

if __name__ == "__main__":
    if login():
        results = [
            test_detect_language(),
            test_translate_with_autodetect()
        ]
        
        if all(results):
            print("\n✅ ALL TESTS PASSED")
            sys.exit(0)
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
    else:
        sys.exit(1)
