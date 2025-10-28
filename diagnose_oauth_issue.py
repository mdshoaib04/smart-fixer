#!/usr/bin/env python3
"""
Diagnose OAuth Issue for SmartFixer
This script helps diagnose why OAuth signup isn't working
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_oauth_configuration():
    """Check OAuth configuration"""
    print("🔍 Checking OAuth Configuration...")
    print("=" * 35)
    
    # Check environment variables
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"GOOGLE_CLIENT_ID: {google_client_id[:30] + '...' if google_client_id else 'NOT SET'}")
    print(f"GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")
    
    if not google_client_id or google_client_id == 'demo-google-client-id':
        print("❌ ERROR: Google Client ID not properly configured")
        return False
    else:
        print("✅ Google Client ID is properly configured")
        
    return True

def check_oauth_routes():
    """Check OAuth routes"""
    print("\n🔍 Checking OAuth Routes...")
    print("-" * 25)
    
    try:
        from app import app
        
        with app.test_request_context():
            from flask import url_for
            
            # Check if routes exist
            try:
                google_url = url_for('google_login')
                callback_url = url_for('google_callback')
                print(f"✅ Google auth route: {google_url}")
                print(f"✅ Google callback route: {callback_url}")
            except Exception as e:
                print(f"❌ Error generating OAuth URLs: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check OAuth routes: {e}")
        return False

def check_redirect_uri_configuration():
    """Check redirect URI configuration"""
    print("\n🔍 Checking Redirect URI Configuration...")
    print("-" * 35)
    
    # Common redirect URIs that should be configured
    expected_uris = [
        "http://localhost:5000/callback/google",
        "http://localhost:8000/callback/google",
        "http://localhost:3000/callback/google",
        "http://127.0.0.1:5000/callback/google"
    ]
    
    print("Expected redirect URIs that should be configured in Google Cloud Console:")
    for uri in expected_uris:
        print(f"  • {uri}")
        
    print("\n💡 Instructions:")
    print("   1. Go to Google Cloud Console")
    print("   2. Navigate to APIs & Services > Credentials")
    print("   3. Click on your OAuth 2.0 Client ID")
    print("   4. Add all the above URLs to 'Authorized redirect URIs'")
    print("   5. Save the changes")
    
    return True

def test_google_oauth_client():
    """Test Google OAuth client configuration"""
    print("\n🔍 Testing Google OAuth Client...")
    print("-" * 30)
    
    try:
        from routes import google
        
        if not google:
            print("❌ Google OAuth client not initialized")
            return False
            
        print("✅ Google OAuth client is initialized")
        print(f"   Client ID: {google.client_id[:30] + '...' if google.client_id else 'None'}")
        
        # Check if using real credentials
        if google.client_id and google.client_id != 'demo-google-client-id':
            print("✅ Using real Google Client ID")
        else:
            print("❌ Using demo Google Client ID (will not work for real authentication)")
            
        # Check metadata URL
        metadata_url = getattr(google, 'server_metadata_url', None)
        if metadata_url:
            print(f"✅ Metadata URL: {metadata_url}")
        else:
            print("❌ Metadata URL not configured")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to test Google OAuth client: {e}")
        return False

def main():
    """Main diagnosis function"""
    print("🚀 SmartFixer OAuth Issue Diagnosis")
    print("=" * 35)
    
    # Run all checks
    config_ok = check_oauth_configuration()
    routes_ok = check_oauth_routes()
    redirect_ok = check_redirect_uri_configuration()
    client_ok = test_google_oauth_client()
    
    print("\n📋 Diagnosis Results:")
    print("-" * 20)
    
    if config_ok:
        print("✅ OAuth Configuration: OK")
    else:
        print("❌ OAuth Configuration: ISSUE")
        
    if routes_ok:
        print("✅ OAuth Routes: OK")
    else:
        print("❌ OAuth Routes: ISSUE")
        
    if client_ok:
        print("✅ OAuth Client: OK")
    else:
        print("❌ OAuth Client: ISSUE")
        
    print("✅ Redirect URI Info: PROVIDED")
    
    if config_ok and routes_ok and client_ok:
        print("\n🎉 Configuration looks good!")
        print("\n💡 Next steps to troubleshoot:")
        print("   1. Verify redirect URIs are properly configured in Google Cloud Console")
        print("   2. Check that you can access http://localhost:5000/callback/google directly")
        print("   3. Try using an incognito/private browser window")
        print("   4. Check browser developer console for JavaScript errors")
        print("   5. Make sure you've restarted the application after making changes")
    else:
        print("\n❌ Configuration issues detected. Please fix the errors above.")
        
        if not config_ok:
            print("\n🔧 Fix OAuth Configuration:")
            print("   • Verify your .env file contains real Google OAuth credentials")
            print("   • Make sure GOOGLE_CLIENT_ID is not set to demo value")
            
        if not routes_ok:
            print("\n🔧 Fix OAuth Routes:")
            print("   • Check that routes.py is properly imported")
            print("   • Verify route names match URL generation")
            
        if not client_ok:
            print("\n🔧 Fix OAuth Client:")
            print("   • Check Google OAuth client initialization")
            print("   • Verify metadata URL configuration")

if __name__ == "__main__":
    main()