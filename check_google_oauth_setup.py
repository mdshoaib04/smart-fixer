import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Checking Google OAuth Setup...")
print("=" * 40)

# Check Google OAuth credentials
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"Google Client ID: {google_client_id}")
print(f"Google Client Secret: {'*' * len(google_client_secret) if google_client_secret else 'Not set'}")

# Verify the format of the Client ID
if google_client_id and '.apps.googleusercontent.com' in google_client_id:
    print("✅ Google Client ID format looks correct")
else:
    print("❌ Google Client ID format may be incorrect")

# Check what redirect URIs should be configured
print("\nRequired Redirect URIs for Google Cloud Console:")
print("-" * 30)

# Common ports to check
ports = [5000, 8000, 3000, 80, 443]

for port in ports:
    if port in [80, 443]:
        print(f"http://localhost/callback/google")
    else:
        print(f"http://localhost:{port}/callback/google")

print("\nInstructions:")
print("-" * 15)
print("1. Go to Google Cloud Console")
print("2. Navigate to APIs & Services > Credentials")
print("3. Click on your OAuth 2.0 Client ID")
print("4. Add all the above URLs to 'Authorized redirect URIs'")
print("5. Save the changes")
print("6. Restart your SmartFixer application")