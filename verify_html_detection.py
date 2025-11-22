import requests
import time

def test_html_detection():
    url = 'http://localhost:5000/api/execute'
    
    # Test case: HTML code but language set to 'python'
    # This simulates the user's scenario where they forget to switch the dropdown
    payload = {
        'code': '<!DOCTYPE html>\n<html><body><h1>Hello</h1></body></html>',
        'language': 'python', # Intentionally wrong
        'session_id': 'test_html_detection'
    }
    
    try:
        print("Sending HTML code with language='python'...")
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"Response: {data}")
        
        if data.get('success') and data.get('type') == 'web':
            print("SUCCESS: HTML detected correctly despite wrong language label!")
        else:
            print("FAILURE: HTML not detected correctly.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Wait a bit for server to start if running immediately after restart
    time.sleep(2)
    test_html_detection()
