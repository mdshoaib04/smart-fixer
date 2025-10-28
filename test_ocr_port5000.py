import requests
import time

# Wait a bit for the server to start
time.sleep(5)

# First, let's login to get a session
login_url = "http://localhost:5000/api/login"
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

# Create a session to maintain cookies
session = requests.Session()

try:
    # Try to login (this will fail if the user doesn't exist)
    login_response = session.post(login_url, json=login_data)
    print("Login status:", login_response.status_code)
    
    # If login fails, try to signup first
    if not login_response.json().get('success'):
        signup_url = "http://localhost:5000/api/signup"
        signup_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        signup_response = session.post(signup_url, json=signup_data)
        print("Signup status:", signup_response.status_code)
        print("Signup response:", signup_response.json())
        
        # Try to login again
        login_response = session.post(login_url, json=login_data)
        print("Login status after signup:", login_response.status_code)
    
    print("Login response:", login_response.json())
    
    # Now test the OCR endpoint with the authenticated session
    ocr_url = "http://localhost:5000/api/extract-code-from-image"
    
    # Upload the image file
    with open('static/uploads/profiles/47cdb7a7-2470-4d94-a78c-a9b28249b5d4.png', 'rb') as f:
        files = {'image': f}
        ocr_response = session.post(ocr_url, files=files)
    
    print("OCR Status Code:", ocr_response.status_code)
    print("OCR Response Text:", ocr_response.text)
    
    # Try to parse JSON if possible
    try:
        response_data = ocr_response.json()
        print("OCR Response JSON:", response_data)
        
        if response_data.get('success'):
            print("OCR extraction successful!")
            print("Extracted code:", response_data.get('code', 'No code extracted'))
            print("Detected language:", response_data.get('language', 'Unknown'))
        else:
            print("OCR extraction failed:", response_data.get('error', 'Unknown error'))
    except Exception as e:
        print("Could not parse JSON response:", str(e))
        
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()