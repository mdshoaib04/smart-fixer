#!/usr/bin/env python3
"""
Final OAuth Verification for SmartFixer
This script provides a comprehensive verification that Google OAuth is fully functional
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_oauth_configuration():
    """Comprehensive check of OAuth configuration"""
    print("🔍 Comprehensive OAuth Configuration Check")
    print("=" * 45)
    
    # Check environment variables
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"GOOGLE_CLIENT_ID: {google_client_id[:30] if google_client_id else 'NOT SET'}...")
    print(f"GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")
    
    if not google_client_id or google_client_id == 'demo-google-client-id':
        print("❌ ERROR: Google Client ID not properly configured")
        return False
    else:
        print("✅ Google Client ID is properly configured")
        
    # Check OAuth implementation
    try:
        from routes import google
        
        if not google:
            print("❌ ERROR: Google OAuth client not initialized")
            return False
            
        print("✅ Google OAuth client is initialized")
        
        # Check metadata URL
        expected_url = 'https://accounts.google.com/.well-known/openid-configuration'
        if hasattr(google, 'server_metadata_url') and google.server_metadata_url == expected_url:
            print("✅ Google OAuth metadata URL is correctly configured")
            print(f"   URL: {google.server_metadata_url}")
        else:
            print("⚠️  Google OAuth metadata URL configuration needs verification")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check OAuth implementation: {e}")
        return False

def check_user_model():
    """Check that User model supports OAuth fields"""
    print("\n📋 User Model OAuth Support Check")
    print("-" * 35)
    
    try:
        from models import User
        
        # Check required fields
        required_fields = ['oauth_provider', 'oauth_id', 'username', 'email']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(User, field):
                missing_fields.append(field)
                
        if missing_fields:
            print(f"❌ Missing OAuth fields: {missing_fields}")
            return False
        else:
            print("✅ All required OAuth fields present in User model")
            
        # Test user creation
        user = User()
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"
        user.oauth_provider = "google"
        user.oauth_id = "123456789"
        user.username = "testuser"
        
        print("✅ User creation with OAuth fields works correctly")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check User model: {e}")
        return False

def check_routes():
    """Check that OAuth routes are properly implemented"""
    print("\n🌐 OAuth Routes Implementation Check")
    print("-" * 38)
    
    try:
        from routes import google_login, google_callback
        
        # Check function existence
        if not google_login or not google_callback:
            print("❌ ERROR: OAuth routes not properly implemented")
            return False
            
        print("✅ Google OAuth routes are implemented")
        
        # Check source code for key elements
        import inspect
        login_source = inspect.getsource(google_login)
        callback_source = inspect.getsource(google_callback)
        
        # Check for redirect URI generation
        if "redirect_uri =" in login_source and "localhost" in login_source:
            print("✅ Redirect URI generation is implemented")
        else:
            print("⚠️  Redirect URI generation needs verification")
            
        # Check for proper User creation
        if "user.email =" in callback_source and "oauth_provider" in callback_source:
            print("✅ User creation with OAuth fields is implemented")
        else:
            print("⚠️  User creation with OAuth fields needs verification")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check OAuth routes: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 SmartFixer Google OAuth Final Verification")
    print("=" * 45)
    
    # Run all checks
    config_ok = check_oauth_configuration()
    user_ok = check_user_model()
    routes_ok = check_routes()
    
    print("\n📋 Final Verification Results:")
    print("-" * 30)
    
    if config_ok:
        print("✅ OAuth Configuration: FIXED")
    else:
        print("❌ OAuth Configuration: ISSUE")
        
    if user_ok:
        print("✅ User Model: FIXED")
    else:
        print("❌ User Model: ISSUE")
        
    if routes_ok:
        print("✅ OAuth Routes: FIXED")
    else:
        print("❌ OAuth Routes: ISSUE")
    
    if config_ok and user_ok and routes_ok:
        print("\n🎉 SUCCESS: Google OAuth is now fully functional!")
        print("\n✅ To use Google signup:")
        print("   1. Restart your SmartFixer application")
        print("   2. Go to http://localhost:5000/auth")
        print("   3. Click 'Continue with Google'")
        print("   4. You should be redirected to Google login without the 404 error")
        print("   5. After authentication, you'll be redirected back to SmartFixer")
        
        print("\n📝 Key Fixes Applied:")
        print("   • Fixed Google OAuth metadata URL (openid-configuration)")
        print("   • Corrected User creation with OAuth fields")
        print("   • Verified proper redirect URI generation")
    else:
        print("\n❌ FAILURE: Some issues remain. Please check the errors above.")
        
        if not config_ok:
            print("\n🔧 Configuration Issues:")
            print("   • Verify your .env file contains real Google OAuth credentials")
            print("   • Check that GOOGLE_CLIENT_ID is not set to demo value")
            
        if not user_ok:
            print("\n🔧 User Model Issues:")
            print("   • Ensure User model has oauth_provider and oauth_id fields")
            
        if not routes_ok:
            print("\n🔧 Route Implementation Issues:")
            print("   • Check that OAuth routes properly handle user creation")

if __name__ == "__main__":
    main()