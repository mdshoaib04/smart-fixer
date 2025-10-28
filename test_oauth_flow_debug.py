#!/usr/bin/env python3
"""
Test OAuth Flow Debug for SmartFixer
This script tests the OAuth flow within the application context
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_oauth_flow():
    """Test the OAuth flow within application context"""
    print("🔍 Testing OAuth Flow Within Application Context...")
    print("=" * 50)
    
    try:
        from app import app
        from routes import google_callback
        
        with app.app_context():
            print("✅ Application context is working")
            
            # Check if we can import the models
            from models import User, db
            
            print("✅ Models imported successfully")
            
            # Test database connection
            try:
                db.session.execute(db.text('SELECT 1'))
                print("✅ Database connection is working")
            except Exception as e:
                print(f"⚠️  Database connection issue: {e}")
                
            # Check User model fields
            required_fields = ['oauth_provider', 'oauth_id', 'username', 'email']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(User, field):
                    missing_fields.append(field)
                    
            if missing_fields:
                print(f"❌ Missing fields in User model: {missing_fields}")
                return False
            else:
                print("✅ All required OAuth fields present in User model")
                
            # Test User creation
            try:
                user = User()
                user.email = "test@example.com"
                user.first_name = "Test"
                user.last_name = "User"
                user.oauth_provider = "google"
                user.oauth_id = "123456789"
                user.username = "testuser"
                
                print("✅ User creation test passed")
                return True
                
            except Exception as e:
                print(f"❌ User creation test failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ ERROR: Failed to test OAuth flow: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_google_oauth_config():
    """Check Google OAuth configuration"""
    print("\n🔍 Checking Google OAuth Configuration...")
    print("-" * 40)
    
    try:
        from routes import google
        
        if not google:
            print("❌ Google OAuth client not configured")
            return False
            
        print("✅ Google OAuth client is configured")
        
        # Check client ID
        client_id = google.client_id
        if client_id and client_id != 'demo-google-client-id':
            print("✅ Using real Google Client ID")
        else:
            print("❌ Using demo Google Client ID (will not work for real authentication)")
            
        # Check metadata URL
        metadata_url = getattr(google, 'server_metadata_url', None)
        if metadata_url and 'openid-configuration' in metadata_url:
            print("✅ Google OAuth metadata URL is correctly configured")
        else:
            print("❌ Google OAuth metadata URL is not correctly configured")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check Google OAuth configuration: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SmartFixer OAuth Flow Debug Test")
    print("=" * 35)
    
    # Run tests
    config_ok = check_google_oauth_config()
    flow_ok = test_oauth_flow()
    
    print("\n📋 Test Results:")
    print("-" * 15)
    
    if config_ok:
        print("✅ Google OAuth Configuration: OK")
    else:
        print("❌ Google OAuth Configuration: ISSUE")
        
    if flow_ok:
        print("✅ OAuth Flow Test: OK")
    else:
        print("❌ OAuth Flow Test: ISSUE")
    
    if config_ok and flow_ok:
        print("\n🎉 OAuth configuration and flow tests passed!")
        print("\n💡 To debug the signup issue:")
        print("   1. Start the application: python app.py")
        print("   2. Watch the terminal for error messages when clicking 'Continue with Google'")
        print("   3. Check that you're being redirected to Google login")
        print("   4. Check that you're being redirected back to your app after Google login")
        print("   5. Look for any database errors during user creation")
    else:
        print("\n❌ Issues detected. Please check the errors above.")
        
        if not config_ok:
            print("\n🔧 Configuration Issues:")
            print("   • Verify your .env file contains real Google OAuth credentials")
            print("   • Check that GOOGLE_CLIENT_ID is not set to demo value")
            
        if not flow_ok:
            print("\n🔧 Flow Issues:")
            print("   • Check database connection")
            print("   • Verify User model implementation")

if __name__ == "__main__":
    main()