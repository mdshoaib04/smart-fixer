import requests
import time

BASE_URL = 'http://localhost:5000/api/execute'

def test_python_local():
    print("\n--- Testing Python (Local/Interactive) ---")
    payload = {
        'code': 'print("Hello from Python Local")',
        'language': 'python',
        'session_id': 'test_py_local'
    }
    try:
        res = requests.post(BASE_URL, json=payload)
        data = res.json()
        print(f"Response: {data}")
        if data.get('type') == 'interactive':
            print("SUCCESS: Python started as interactive session (Local).")
        else:
            print("FAILURE: Python did not start as interactive.")
    except Exception as e:
        print(f"Error: {e}")

def test_java_piston():
    print("\n--- Testing Java (Piston Fallback) ---")
    code = """
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello from Java Piston");
        }
    }
    """
    payload = {
        'code': code,
        'language': 'java',
        'session_id': 'test_java_piston'
    }
    try:
        res = requests.post(BASE_URL, json=payload)
        data = res.json()
        print(f"Response: {data}")
        if data.get('success') and 'Hello from Java Piston' in data.get('output', ''):
            print("SUCCESS: Java executed via Piston fallback.")
        else:
            print("FAILURE: Java execution failed.")
    except Exception as e:
        print(f"Error: {e}")

def test_c_detection_piston():
    print("\n--- Testing C Detection & Piston Fallback ---")
    # Sending C code but labeled as 'python' to test auto-detection + fallback
    code = """
    #include <stdio.h>
    int main() {
        printf("Hello from C Piston");
        return 0;
    }
    """
    payload = {
        'code': code,
        'language': 'python', # Intentional wrong label
        'session_id': 'test_c_piston'
    }
    try:
        res = requests.post(BASE_URL, json=payload)
        data = res.json()
        print(f"Response: {data}")
        if data.get('success') and 'Hello from C Piston' in data.get('output', ''):
            print("SUCCESS: C detected and executed via Piston fallback.")
        else:
            print("FAILURE: C execution failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    time.sleep(3) # Wait for server
    test_python_local()
    test_java_piston()
    test_c_detection_piston()
