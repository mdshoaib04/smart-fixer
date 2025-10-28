import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

print("Testing OAuth Functionality...")
print("=" * 40)

# Initialize variables
app = None

google = None
github = None

# Import the app and check OAuth configuration
try:
    from app import app
    from routes import google, github
    
    print("✅ App and routes imported successfully")
    
    if google:
        print("✅ Google OAuth is configured")
        print(f"Google Client ID: {google.client_id}")
        # Check if it's using the real client ID or demo one
        if google.client_id and google.client_id != 'demo-google-client-id':
            print("✅ Using real Google Client ID")
        else:
            print("❌ Still using demo Google Client ID")
    else:
        print("❌ Google OAuth is not configured")
        
    if github:
        print("✅ GitHub OAuth is configured")
    else:
        print("❌ GitHub OAuth is not configured")
        
except Exception as e:
    print(f"❌ Error importing app or routes: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking redirect URI...")
try:
    if app is not None:
        with app.test_request_context():
            from flask import url_for
            google_callback_url = url_for('google_callback', _external=True)
            print(f"Google callback URL: {google_callback_url}")
    else:
        print("❌ App not initialized, cannot generate callback URL")
except Exception as e:
    print(f"❌ Error generating callback URL: {e}")