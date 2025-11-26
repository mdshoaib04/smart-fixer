import requests
import json
import sys

BASE_URL = "http://localhost:5000"

# Login to get session cookie
session = requests.Session()

def login():
    print("Logging in...")
    # Try to create a test user first
    try:
        signup_data = {
            "name": "Test User",
            "email": "test_dict@example.com",
            "password": "password123",
            "username": "test_dict_user"
        }
        session.post(f"{BASE_URL}/api/signup", json=signup_data)
    except:
        pass

    login_data = {
        "email": "test_dict@example.com",
        "password": "password123"
    }
    response = session.post(f"{BASE_URL}/api/login", json=login_data)
    if response.status_code == 200 and response.json().get('success'):
        print("Login successful")
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

def test_dictionary():
    print("\nTesting Dictionary API...")
    data = {
        "term": "bubble sort",
        "language": "python"
    }
    response = session.post(f"{BASE_URL}/api/dictionary", json=data)
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        if result.get('success') and 'result' in result:
            print("✅ Dictionary API Success: 'result' key found")
            print(f"Preview: {result['result'][:50]}...")
            return True
        else:
            print(f"❌ Dictionary API Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Dictionary API Error: {e}")
        return False

def test_translate():
    print("\nTesting Translate API...")
    data = {
        "code": "print('Hello')",
        "to_lang": "java",
        "from_lang": "python"
    }
    response = session.post(f"{BASE_URL}/api/translate", json=data)
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        if result.get('success') and 'result' in result:
            print("✅ Translate API Success: 'result' key found")
            return True
        else:
            print(f"❌ Translate API Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Translate API Error: {e}")
        return False

def test_review():
    print("\nTesting Review API...")
    data = {
        "code": "def hello(): print('hi')",
        "language": "python"
    }
    response = session.post(f"{BASE_URL}/api/review", json=data)
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        if result.get('success') and 'result' in result:
            print("✅ Review API Success: 'result' key found")
            return True
        else:
            print(f"❌ Review API Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Review API Error: {e}")
        return False

def test_explain():
    print("\nTesting Explain API...")
    data = {
        "code": "print('Hello')",
        "language": "python",
        "role": "student"
    }
    response = session.post(f"{BASE_URL}/api/explain", json=data)
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        if result.get('success') and 'result' in result:
            print("✅ Explain API Success: 'result' key found")
            return True
        else:
            print(f"❌ Explain API Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Explain API Error: {e}")
        return False

def test_question():
    print("\nTesting Question API...")
    data = {
        "question": "What does this do?",
        "code": "print('Hello')",
        "language": "python"
    }
    response = session.post(f"{BASE_URL}/api/question", json=data)
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        if result.get('success') and 'result' in result:
            print("✅ Question API Success: 'result' key found")
            return True
        else:
            print(f"❌ Question API Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Question API Error: {e}")
        return False

if __name__ == "__main__":
    if login():
        results = [
            test_dictionary(),
            test_translate(),
            test_review(),
            test_explain(),
            test_question()
        ]
        
        if all(results):
            print("\n✅ ALL TESTS PASSED")
            sys.exit(0)
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
    else:
        sys.exit(1)
