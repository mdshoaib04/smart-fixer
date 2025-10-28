import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing OAuth Configuration...")
print("=" * 40)

# Check if environment variables are loaded
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"GOOGLE_CLIENT_ID: {google_client_id}")
print(f"GOOGLE_CLIENT_SECRET: {google_client_secret}")

if google_client_id and google_client_id != 'demo-google-client-id':
    print("✅ Google OAuth credentials appear to be set correctly")
else:
    print("❌ Google OAuth credentials are not set or are still using demo values")

if google_client_secret and google_client_secret != 'demo-google-client-secret':
    print("✅ Google OAuth secret appears to be set correctly")
else:
    print("❌ Google OAuth secret is not set or is still using demo values")

print("\nAll environment variables:")
print("-" * 20)
for key, value in os.environ.items():
    if 'GOOGLE' in key or 'CLIENT' in key:
        print(f"{key}: {value}")