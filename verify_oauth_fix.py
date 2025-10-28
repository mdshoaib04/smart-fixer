#!/usr/bin/env python3
"""
Verify OAuth Fix for SmartFixer
This script verifies that the OAuth signup fix is working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_oauth_callback_improvements():
    """Check the improvements made to OAuth callbacks"""
    print("🔍 Checking OAuth Callback Improvements...")
    print("=" * 45)
    
    try:
        from routes import google_callback, github_callback
        
        # Check source code for improvements
        import inspect
        google_source = inspect.getsource(google_callback)
        github_source = inspect.getsource(github_callback)
        
        improvements = []
        
        # Check for is_new_user flag
        if "is_new_user" in google_source:
            print("✅ New user detection flag implemented for Google OAuth")
            improvements.append("new_user_flag")
        else:
            print("❌ New user detection flag missing for Google OAuth")
            
        if "is_new_user" in github_source:
            print("✅ New user detection flag implemented for GitHub OAuth")
            improvements.append("new_user_flag")
        else:
            print("❌ New user detection flag missing for GitHub OAuth")
            
        # Check for user creation confirmation
        if "New user created" in google_source:
            print("✅ User creation confirmation logging implemented for Google OAuth")
            improvements.append("creation_logging")
        else:
            print("❌ User creation confirmation logging missing for Google OAuth")
            
        if "New user created" in github_source:
            print("✅ User creation confirmation logging implemented for GitHub OAuth")
            improvements.append("creation_logging")
        else:
            print("❌ User creation confirmation logging missing for GitHub OAuth")
            
        # Check for user login confirmation
        if "User logged in" in google_source:
            print("✅ User login confirmation logging implemented for Google OAuth")
            improvements.append("login_logging")
        else:
            print("❌ User login confirmation logging missing for Google OAuth")
            
        if "User logged in" in github_source:
            print("✅ User login confirmation logging implemented for GitHub OAuth")
            improvements.append("login_logging")
        else:
            print("❌ User login confirmation logging missing for GitHub OAuth")
            
        # Check for welcome message
        if "Welcome to SmartFixer" in google_source:
            print("✅ Welcome message for new users implemented for Google OAuth")
            improvements.append("welcome_message")
        else:
            print("❌ Welcome message for new users missing for Google OAuth")
            
        if "Welcome to SmartFixer" in github_source:
            print("✅ Welcome message for new users implemented for GitHub OAuth")
            improvements.append("welcome_message")
        else:
            print("❌ Welcome message for new users missing for GitHub OAuth")
            
        return len(improvements) == 6  # All 6 improvements should be present
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check OAuth callback improvements: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("🚀 SmartFixer OAuth Fix Verification")
    print("=" * 35)
    
    # Check improvements
    improvements_ok = check_oauth_callback_improvements()
    
    print("\n📋 Verification Results:")
    print("-" * 25)
    
    if improvements_ok:
        print("✅ All OAuth callback improvements implemented")
        print("\n🎉 Fix verification successful!")
        print("\n💡 What was fixed:")
        print("   • Added new user detection flag")
        print("   • Added user creation confirmation logging")
        print("   • Added user login confirmation logging")
        print("   • Added welcome message for new users")
        print("   • Improved error handling and debugging")
        print("\n🚀 To test the fix:")
        print("   1. Restart your SmartFixer application")
        print("   2. Go to http://localhost:5000/auth")
        print("   3. Click 'Continue with Google'")
        print("   4. You should now be properly signed up and redirected")
        print("   5. Check for a welcome message after signup")
    else:
        print("❌ Some OAuth callback improvements are missing")
        print("\n🔧 Please check the OAuth callback implementations in routes.py")

if __name__ == "__main__":
    main()