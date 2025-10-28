import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

print("Testing Google OAuth Implementation...")
print("=" * 40)

# Check environment variables
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"GOOGLE_CLIENT_ID: {google_client_id}")
print(f"GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")

app = None
google = None

# Import the app and check OAuth configuration
try:
    from app import app
    from routes import google
    
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
        
except Exception as e:
    print(f"❌ Error importing app or routes: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking redirect URI generation...")
try:
    if app is not None:
        with app.test_request_context('/', environ_overrides={'wsgi.url_scheme': 'http', 'HTTP_HOST': 'localhost:5000'}):
            from flask import url_for, request
            
            # Test our custom redirect URI generation
            scheme = request.scheme
            host = request.host.split(':')[0]  # Get host without port
            port = 5000  # Default port
            custom_redirect_uri = f"{scheme}://{host}:{port}/callback/google"
            print(f"Custom redirect URI: {custom_redirect_uri}")
            
            if f":{port}" in custom_redirect_uri:
                print("✅ Custom approach correctly includes port")
            else:
                print("❌ Custom approach missing port")
    else:
        print("❌ App not initialized, cannot generate redirect URI")
except Exception as e:
    print(f"❌ Error generating redirect URI: {e}")
    import traceback
    traceback.print_exc()

print("\nRecommendations:")
print("-" * 15)
print("1. Make sure the exact URI 'http://localhost:5000/callback/google' is registered")
print("   in your Google Cloud Console OAuth client")
print("2. Double-check there are no extra spaces or characters in the URI")
print("3. Try using 'http://127.0.0.1:5000/callback/google' as an alternative")
print("4. If issues persist, try creating a new OAuth client in Google Cloud Console")