#!/usr/bin/env python3
"""
Detailed OAuth Debug for SmartFixer
This script provides detailed debugging of the OAuth flow
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def debug_google_login_route():
    """Debug the Google login route"""
    print("🔍 Debugging Google Login Route...")
    print("=" * 35)
    
    try:
        from app import app
        import routes
        
        with app.test_request_context('/auth/google', environ_overrides={'wsgi.url_scheme': 'http', 'HTTP_HOST': 'localhost:5000'}):
            from flask import request, session
            from routes import google_login
            
            print("✅ App context and routes loaded")
            
            # Simulate calling the google_login function
            print("\nSimulating google_login() function call...")
            
            # Check if Google OAuth client exists
            from routes import google
            if not google:
                print("❌ Google OAuth client not initialized")
                return False
                
            print("✅ Google OAuth client is available")
            print(f"   Client ID: {google.client_id[:30] + '...' if google.client_id else 'None'}")
            
            # Check if we're in the right environment
            print(f"   Request scheme: {request.scheme}")
            print(f"   Request host: {request.host}")
            print(f"   Request URL: {request.url}")
            
            # Test redirect URI generation logic
            import sys
            port = 5000
            if '--port' in sys.argv:
                try:
                    port_index = sys.argv.index('--port') + 1
                    if port_index < len(sys.argv):
                        port = int(sys.argv[port_index])
                except (ValueError, IndexError):
                    pass  # Use default port 5000
                    
            scheme = request.scheme
            host = request.host.split(':')[0]  # Get host without port
            redirect_uri = f"{scheme}://{host}:{port}/callback/google"
            
            print(f"✅ Generated redirect URI: {redirect_uri}")
            
            # Check if redirect URI contains port (this was a previous issue)
            if f":{port}" in redirect_uri:
                print("✅ Redirect URI correctly includes port number")
            else:
                print("❌ Redirect URI missing port number")
                
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Failed to debug Google login route: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_authlib_configuration():
    """Check Authlib configuration"""
    print("\n🔍 Checking Authlib Configuration...")
    print("-" * 35)
    
    try:
        from routes import google
        
        if not google:
            print("❌ Google OAuth client not configured")
            return False
            
        print("✅ Google OAuth client is configured")
        
        # Check server metadata URL
        metadata_url = getattr(google, 'server_metadata_url', None)
        if metadata_url:
            print(f"✅ Server metadata URL: {metadata_url}")
            if 'openid-configuration' in metadata_url:
                print("✅ Metadata URL format is correct")
            else:
                print("❌ Metadata URL format may be incorrect")
        else:
            print("❌ Server metadata URL not configured")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check Authlib configuration: {e}")
        return False

def main():
    """Main debug function"""
    print("🚀 SmartFixer Detailed OAuth Debug")
    print("=" * 35)
    
    login_ok = debug_google_login_route()
    authlib_ok = check_authlib_configuration()
    
    print("\n📋 Debug Results:")
    print("-" * 18)
    
    if login_ok:
        print("✅ Google Login Route: OK")
    else:
        print("❌ Google Login Route: ISSUE")
        
    if authlib_ok:
        print("✅ Authlib Configuration: OK")
    else:
        print("❌ Authlib Configuration: ISSUE")
    
    if login_ok and authlib_ok:
        print("\n🎉 All systems check out!")
        print("\n💡 Troubleshooting Tips:")
        print("   1. Make sure you're running the app with: python app.py")
        print("   2. Verify all redirect URIs are configured in Google Cloud Console")
        print("   3. Try using an incognito/private browser window")
        print("   4. Check browser developer console for JavaScript errors")
        print("   5. Look at application terminal for detailed error messages during OAuth flow")
        print("   6. Make sure your Google OAuth credentials are correct")
    else:
        print("\n❌ Issues detected. Please check the errors above.")
        
        if not login_ok:
            print("\n🔧 Google Login Route Issues:")
            print("   • Check redirect URI generation")
            print("   • Verify Google OAuth client initialization")
            
        if not authlib_ok:
            print("\n🔧 Authlib Configuration Issues:")
            print("   • Check server metadata URL")
            print("   • Verify OAuth client configuration")

if __name__ == "__main__":
    main()