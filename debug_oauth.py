import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

print("Debugging OAuth Configuration...")
print("=" * 40)

# Check if environment variables are properly loaded
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"GOOGLE_CLIENT_ID: {google_client_id}")
print(f"GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")

# Check if we're using demo values
if google_client_id == 'demo-google-client-id' or not google_client_id:
    print("❌ ERROR: Using demo Google Client ID or no ID set")
else:
    print("✅ Google Client ID is properly configured")

if google_client_secret == 'demo-google-client-secret' or not google_client_secret:
    print("❌ ERROR: Using demo Google Client Secret or no secret set")
else:
    print("✅ Google Client Secret is properly configured")

# Check if the routes module can import authlib
try:
    from routes import google, github
    print("✅ Routes module loaded successfully")
    
    if google:
        print(f"✅ Google OAuth object created with client_id: {google.client_id}")
        if google.client_id == 'demo-google-client-id':
            print("❌ ERROR: Google OAuth is still using demo credentials")
        else:
            print("✅ Google OAuth is using real credentials")
    else:
        print("❌ ERROR: Google OAuth object is None")
        
except Exception as e:
    print(f"❌ ERROR: Failed to load routes module: {e}")

# Check the port configuration
port = 5000
if '--port' in sys.argv:
    try:
        port_index = sys.argv.index('--port') + 1
        if port_index < len(sys.argv):
            port = int(sys.argv[port_index])
    except (ValueError, IndexError):
        pass

print(f"\nApplication port: {port}")

# Show what redirect URI should be used
print(f"\nExpected redirect URI: http://localhost:{port}/callback/google")

print("\nTroubleshooting steps:")
print("-" * 20)
print("1. Verify the exact redirect URI is added in Google Cloud Console")
print("2. Make sure there are no typos in the URI")
print("3. Check that you've saved the changes in Google Cloud Console")
print("4. Try restarting the application completely")
print("5. Check the browser console for any additional error messages")