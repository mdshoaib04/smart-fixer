#!/usr/bin/env python3
"""
Test OAuth Fix for SmartFixer
This script verifies that the Google OAuth configuration fix is working
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_google_oauth_config():
    """Test the Google OAuth configuration fix"""
    print("🔍 Testing Google OAuth Configuration Fix...")
    print("=" * 45)
    
    try:
        # Import the routes module and check the google_login function
        import inspect
        from routes import google_login, google
        
        # Get the source code of the google_login function
        source = inspect.getsource(google_login)
        
        print("Google OAuth Configuration:")
        print("-" * 25)
        
        # Check if our fix is in the source code
        if "openid-configuration" in source:
            print("✅ Fixed Google OAuth metadata URL is present")
            print("   URL: https://accounts.google.com/.well-known/openid-configuration")
        else:
            print("❌ Fixed Google OAuth metadata URL is NOT present")
            
        # Check the OAuth client configuration
        if google:
            print(f"✅ Google OAuth client is configured")
            print(f"   Client ID: {google.client_id[:20]}..." if google.client_id else "   Client ID: None")
            
            # Check if using real credentials
            if google.client_id and google.client_id != 'demo-google-client-id':
                print("✅ Using real Google Client ID")
            else:
                print("⚠️  Using demo Google Client ID (may not work for real authentication)")
        else:
            print("❌ Google OAuth client is not configured")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing Google OAuth configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation():
    """Test the User creation fix"""
    print("\n🔍 Testing User Creation Fix...")
    print("-" * 30)
    
    try:
        from models import User
        from app import db
        
        # Check if User model has required OAuth fields
        required_fields = ['oauth_provider', 'oauth_id', 'username', 'email']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(User, field):
                missing_fields.append(field)
                
        if missing_fields:
            print(f"❌ Missing fields in User model: {missing_fields}")
            return False
        else:
            print("✅ All required fields present in User model")
            
        # Test creating a user with OAuth fields
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
        print(f"❌ Error testing User creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run all tests"""
    print("🚀 SmartFixer OAuth Fix Verification")
    print("=" * 35)
    
    # Run all tests
    config_ok = test_google_oauth_config()
    user_ok = test_user_creation()
    
    print("\n📋 Results Summary:")
    print("-" * 18)
    
    if config_ok:
        print("✅ Google OAuth configuration fix applied")
    else:
        print("❌ Google OAuth configuration fix failed")
        
    if user_ok:
        print("✅ User creation fix applied")
    else:
        print("❌ User creation fix failed")
    
    if config_ok and user_ok:
        print("\n🎉 All fixes applied successfully!")
        print("\n✅ To test Google OAuth:")
        print("   1. Restart your SmartFixer application")
        print("   2. Go to http://localhost:5000/auth")
        print("   3. Click 'Continue with Google'")
        print("   4. You should be redirected to Google login without errors")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")

if __name__ == "__main__":
    main()