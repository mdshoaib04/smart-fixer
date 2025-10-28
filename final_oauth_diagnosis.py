#!/usr/bin/env python3
"""
Final OAuth Diagnosis for SmartFixer
This script provides a comprehensive diagnosis of the OAuth issue
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def comprehensive_oauth_check():
    """Comprehensive OAuth check"""
    print("🔍 Comprehensive OAuth Diagnosis...")
    print("=" * 35)
    
    try:
        from app import app
        import routes
        
        with app.app_context():
            print("✅ App context loaded")
            
            # Check OAuth client configuration
            from routes import google
            
            if not google:
                print("❌ Google OAuth client not initialized")
                return False
                
            print("✅ Google OAuth client initialized")
            
            # Check all attributes of the OAuth client
            print("\nOAuth Client Attributes:")
            attributes_to_check = [
                'client_id',
                'client_secret', 
                'server_metadata_url',
                'authorize_url',
                'token_url'
            ]
            
            for attr in attributes_to_check:
                value = getattr(google, attr, 'Not found')
                if value != 'Not found':
                    print(f"  • {attr}: {str(value)[:50] + '...' if len(str(value)) > 50 else value}")
                else:
                    print(f"  • {attr}: {value}")
                    
            # Check if all required attributes are present
            required_attrs = ['client_id', 'client_secret']
            missing_attrs = [attr for attr in required_attrs if getattr(google, attr, None) is None]
            
            if missing_attrs:
                print(f"❌ Missing required attributes: {missing_attrs}")
                return False
            else:
                print("✅ All required OAuth client attributes present")
                
            # Check if client_id is real (not demo)
            client_id = getattr(google, 'client_id', '')
            if client_id and client_id != 'demo-google-client-id':
                print("✅ Using real Google Client ID")
            else:
                print("❌ Using demo Google Client ID")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Failed comprehensive OAuth check: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_and_config():
    """Check environment variables and configuration"""
    print("\n🔍 Environment and Configuration Check...")
    print("-" * 40)
    
    # Check environment variables
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'demo-{var.lower()}':
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET or using demo value")
        else:
            print(f"✅ {var}: SET")
            
    if missing_vars:
        print(f"❌ Missing or invalid environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are properly set")
        return True

def provide_actionable_steps():
    """Provide actionable steps to fix the issue"""
    print("\n📋 Actionable Steps to Fix OAuth Issue:")
    print("=" * 40)
    
    print("\n1. 🔧 Verify Google Cloud Console Configuration:")
    print("   • Go to Google Cloud Console")
    print("   • Navigate to APIs & Services > Credentials")
    print("   • Click on your OAuth 2.0 Client ID")
    print("   • Make sure these URIs are in 'Authorized redirect URIs':")
    print("     - http://localhost:5000/callback/google")
    print("     - http://127.0.0.1:5000/callback/google")
    print("   • Click 'Save' to apply changes")
    
    print("\n2. 🔄 Restart Your Application:")
    print("   • Stop the current application (Ctrl+C)")
    print("   • Start it again with: python app.py")
    
    print("\n3. 🔍 Test in Incognito Mode:")
    print("   • Open an incognito/private browser window")
    print("   • Navigate to http://localhost:5000/auth")
    print("   • Click 'Continue with Google'")
    
    print("\n4. 📋 Check Browser Console:")
    print("   • Press F12 to open developer tools")
    print("   • Go to the 'Console' tab")
    print("   • Look for any JavaScript errors when clicking the button")
    
    print("\n5. 🖥️ Monitor Application Terminal:")
    print("   • Watch the terminal where you started the app")
    print("   • Look for error messages when OAuth flow is initiated")
    
    print("\n6. 🧪 Verify Environment Variables:")
    print("   • Check that your .env file contains real Google OAuth credentials")
    print("   • Make sure there are no extra spaces or characters")

def main():
    """Main diagnosis function"""
    print("🚀 SmartFixer Final OAuth Diagnosis")
    print("=" * 35)
    
    oauth_ok = comprehensive_oauth_check()
    env_ok = check_environment_and_config()
    
    print("\n📊 Diagnosis Summary:")
    print("-" * 20)
    
    if oauth_ok:
        print("✅ OAuth Configuration: OK")
    else:
        print("❌ OAuth Configuration: ISSUE")
        
    if env_ok:
        print("✅ Environment Variables: OK")
    else:
        print("❌ Environment Variables: ISSUE")
    
    if oauth_ok and env_ok:
        print("\n🎉 OAuth configuration looks good!")
        print("\n💡 If you're still having issues, try these steps:")
        provide_actionable_steps()
    else:
        print("\n❌ Issues detected in OAuth configuration.")
        print("\n🔧 Please fix the issues above and try again.")
        provide_actionable_steps()

if __name__ == "__main__":
    main()