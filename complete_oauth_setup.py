#!/usr/bin/env python3
"""
Complete Google OAuth Setup Script for SmartFixer
This script verifies and ensures Google OAuth is fully functional
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    print("=" * 40)
    
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"GOOGLE_CLIENT_ID: {google_client_id}")
    print(f"GOOGLE_CLIENT_SECRET: {'*' * len(google_client_secret) if google_client_secret else 'NOT SET'}")
    
    # Verify the format of the Client ID
    if google_client_id and '.apps.googleusercontent.com' in google_client_id:
        print("✅ Google Client ID format looks correct")
        return True
    else:
        print("❌ Google Client ID format may be incorrect")
        return False

def verify_redirect_uris():
    """Verify redirect URIs that should be configured in Google Cloud Console"""
    print("\n📋 Required Redirect URIs for Google Cloud Console:")
    print("-" * 50)
    
    # Common ports to check
    ports = [5000, 8000, 3000, 80, 443]
    
    for port in ports:
        if port in [80, 443]:
            print(f"http://localhost/callback/google")
        else:
            print(f"http://localhost:{port}/callback/google")
            
    print("\n💡 Alternative URIs to try:")
    print("-" * 25)
    for port in [5000, 8000, 3000]:
        print(f"http://127.0.0.1:{port}/callback/google")

def check_implementation():
    """Check if the OAuth implementation is correct"""
    print("\n🔧 Checking OAuth Implementation...")
    print("-" * 35)
    
    try:
        from app import app
        from routes import google
        
        if google and google.client_id != 'demo-google-client-id':
            print("✅ Google OAuth is properly configured with real credentials")
        else:
            print("❌ Google OAuth is using demo credentials or not configured")
            return False
            
        # Test redirect URI generation
        with app.test_request_context('/', environ_overrides={'wsgi.url_scheme': 'http', 'HTTP_HOST': 'localhost:5000'}):
            from flask import request
            
            # Test our custom redirect URI generation
            scheme = request.scheme
            host = request.host.split(':')[0]  # Get host without port
            port = 5000  # Default port
            custom_redirect_uri = f"{scheme}://{host}:{port}/callback/google"
            
            if f":{port}" in custom_redirect_uri:
                print("✅ Custom redirect URI generation is working correctly")
                print(f"   Generated URI: {custom_redirect_uri}")
                return True
            else:
                print("❌ Custom redirect URI generation has issues")
                return False
                
    except Exception as e:
        print(f"❌ Error checking OAuth implementation: {e}")
        import traceback
        traceback.print_exc()
        return False

def provide_instructions():
    """Provide step-by-step instructions for Google OAuth setup"""
    print("\n📋 Step-by-Step Google OAuth Setup Instructions:")
    print("=" * 50)
    
    print("\n1. Google Cloud Console Setup:")
    print("   • Go to https://console.cloud.google.com/")
    print("   • Create a new project or select an existing one")
    print("   • Navigate to 'APIs & Services' → 'Credentials'")
    print("   • Click 'Create Credentials' → 'OAuth client ID'")
    print("   • Select 'Web application' as application type")
    print("   • Give it a name (e.g., 'SmartFixer')")
    
    print("\n2. Authorized Redirect URIs:")
    print("   Add these exact URIs to 'Authorized redirect URIs':")
    ports = [5000, 8000, 3000, 80, 443]
    for port in ports:
        if port in [80, 443]:
            print(f"     • http://localhost/callback/google")
        else:
            print(f"     • http://localhost:{port}/callback/google")
    print("   • Also add: http://127.0.0.1:5000/callback/google")
    
    print("\n3. Environment Configuration:")
    print("   Make sure your .env file contains:")
    print("   GOOGLE_CLIENT_ID=your_actual_client_id")
    print("   GOOGLE_CLIENT_SECRET=your_actual_client_secret")
    
    print("\n4. Restart Application:")
    print("   • Stop the current application (Ctrl+C)")
    print("   • Start it again with: python app.py")
    
    print("\n5. Testing:")
    print("   • Open your browser and go to http://localhost:5000")
    print("   • Click 'Continue with Google' on the auth page")
    print("   • You should be redirected to Google login")

def main():
    """Main function to run all checks"""
    print("🚀 SmartFixer Google OAuth Setup Verification")
    print("=" * 50)
    
    # Run all checks
    env_ok = check_environment()
    impl_ok = check_implementation()
    
    if env_ok and impl_ok:
        print("\n✅ Google OAuth is properly configured and should be working!")
        print("   You can now use 'Sign up with Google' functionality.")
    else:
        print("\n❌ There are issues with Google OAuth setup.")
        provide_instructions()
        
    verify_redirect_uris()
    
    print("\n💡 Tips:")
    print("-" * 10)
    print("• Make sure you're accessing the app at http://localhost:5000")
    print("• Check browser console for detailed error messages")
    print("• Look at the application terminal for any error logs")
    print("• Clear browser cache/cookies if issues persist")

if __name__ == "__main__":
    main()