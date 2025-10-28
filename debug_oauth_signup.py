#!/usr/bin/env python3
"""
Debug OAuth Signup for SmartFixer
This script helps debug issues with Google OAuth signup
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_user_creation_logic():
    """Test the user creation logic"""
    print("🔍 Testing User Creation Logic...")
    print("=" * 35)
    
    try:
        from models import User
        from app import db
        
        # Test creating a sample user
        print("Creating test user...")
        user = User()
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"
        user.oauth_provider = "google"
        user.oauth_id = "123456789"
        user.username = "testuser"
        
        print("✅ User object created successfully")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Username: {user.username}")
        print(f"   OAuth Provider: {user.oauth_provider}")
        print(f"   OAuth ID: {user.oauth_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create test user: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_oauth_routes():
    """Check OAuth routes implementation"""
    print("\n🔍 Checking OAuth Routes...")
    print("-" * 25)
    
    try:
        from routes import google_login, google_callback
        
        if not google_login or not google_callback:
            print("❌ ERROR: OAuth routes not properly implemented")
            return False
            
        print("✅ Google OAuth routes exist")
        
        # Check source code for key elements
        import inspect
        callback_source = inspect.getsource(google_callback)
        
        # Check for user creation logic
        if "user = User()" in callback_source and "db.session.add(user)" in callback_source:
            print("✅ User creation logic is implemented")
        else:
            print("❌ User creation logic is missing")
            
        # Check for login logic
        if "login_user(user, remember=True)" in callback_source:
            print("✅ User login logic is implemented")
        else:
            print("❌ User login logic is missing")
            
        # Check for redirect logic
        if "redirect(url_for('upload_or_write'))" in callback_source:
            print("✅ Redirect logic is implemented")
        else:
            print("❌ Redirect logic is missing")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check OAuth routes: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_connection():
    """Check database connection and schema"""
    print("\n🔍 Checking Database Connection...")
    print("-" * 30)
    
    try:
        from app import db
        from models import User
        
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        print("✅ Database connection is working")
        
        # Check if User table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' in tables:
            print("✅ Users table exists")
        else:
            print("❌ Users table does not exist")
            
        # Check User model fields
        required_fields = ['oauth_provider', 'oauth_id', 'username', 'email']
        
        # Check if the User model has the required attributes
        missing_fields = []
        for field in required_fields:
            if not hasattr(User, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields in User model: {missing_fields}")
            return False
        else:
            print("✅ All required fields exist in User model")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🚀 SmartFixer OAuth Signup Debug")
    print("=" * 35)
    
    # Run all checks
    db_ok = check_database_connection()
    user_ok = test_user_creation_logic()
    routes_ok = check_oauth_routes()
    
    print("\n📋 Debug Results:")
    print("-" * 18)
    
    if db_ok:
        print("✅ Database: OK")
    else:
        print("❌ Database: ISSUE")
        
    if user_ok:
        print("✅ User Creation: OK")
    else:
        print("❌ User Creation: ISSUE")
        
    if routes_ok:
        print("✅ OAuth Routes: OK")
    else:
        print("❌ OAuth Routes: ISSUE")
    
    if db_ok and user_ok and routes_ok:
        print("\n🎉 All systems check out!")
        print("\n💡 Troubleshooting Tips:")
        print("   1. Check the application terminal for error messages during OAuth flow")
        print("   2. Verify that your Google OAuth credentials are correctly configured")
        print("   3. Make sure you've restarted the application after making changes")
        print("   4. Check that the redirect URIs are properly configured in Google Cloud Console")
        print("   5. Try clearing your browser cache and cookies")
    else:
        print("\n❌ Issues detected. Please check the errors above.")
        
        if not db_ok:
            print("\n🔧 Database Issues:")
            print("   • Verify database connection")
            print("   • Check that all required tables exist")
            
        if not user_ok:
            print("\n🔧 User Creation Issues:")
            print("   • Check User model implementation")
            print("   • Verify field names match database schema")
            
        if not routes_ok:
            print("\n🔧 OAuth Route Issues:")
            print("   • Check route implementations")
            print("   • Verify redirect logic")

if __name__ == "__main__":
    main()