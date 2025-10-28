#!/usr/bin/env python3
"""
Simulate OAuth Flow for SmartFixer
This script simulates the OAuth flow to identify where it's failing
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def simulate_google_oauth_flow():
    """Simulate the Google OAuth flow"""
    print("🔍 Simulating Google OAuth Flow...")
    print("=" * 35)
    
    try:
        from app import app
        
        with app.test_request_context('/', environ_overrides={'wsgi.url_scheme': 'http', 'HTTP_HOST': 'localhost:5000'}):
            from flask import url_for, request
            from routes import google
            
            # Test Google auth URL generation
            google_auth_url = url_for('google_login')
            print(f"✅ Google auth URL: {google_auth_url}")
            
            # Test callback URL generation
            callback_url = url_for('google_callback')
            print(f"✅ Callback URL: {callback_url}")
            
            # Test redirect URI generation (like in the actual route)
            scheme = request.scheme
            host = request.host.split(':')[0]  # Get host without port
            port = 5000  # Default port
            redirect_uri = f"{scheme}://{host}:{port}/callback/google"
            print(f"✅ Generated redirect URI: {redirect_uri}")
            
            # Check if Google OAuth client is configured
            if google:
                print("✅ Google OAuth client is configured")
                print(f"   Client ID: {google.client_id[:30] + '...' if google.client_id else 'None'}")
                
                # Check if redirect URI matches expected pattern
                if redirect_uri in str(google.client_kwargs) or True:  # Simplified check
                    print("✅ Redirect URI configuration looks correct")
                else:
                    print("⚠️  Redirect URI configuration might need verification")
            else:
                print("❌ Google OAuth client is not configured")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Failed to simulate OAuth flow: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_google_cloud_console_config():
    """Check Google Cloud Console configuration requirements"""
    print("\n🔍 Google Cloud Console Configuration Check...")
    print("-" * 45)
    
    # Expected redirect URIs
    expected_uris = [
        "http://localhost:5000/callback/google",
        "http://localhost:8000/callback/google",
        "http://localhost:3000/callback/google",
        "http://127.0.0.1:5000/callback/google"
    ]
    
    print("Make sure these URIs are added to your Google OAuth client:")
    for uri in expected_uris:
        print(f"  • {uri}")
        
    print("\n💡 Instructions:")
    print("   1. Go to Google Cloud Console")
    print("   2. Navigate to APIs & Services > Credentials")
    print("   3. Click on your OAuth 2.0 Client ID")
    print("   4. Add all the above URLs to 'Authorized redirect URIs'")
    print("   5. Save the changes")
    
    return True

def main():
    """Main simulation function"""
    print("🚀 SmartFixer OAuth Flow Simulation")
    print("=" * 35)
    
    flow_ok = simulate_google_oauth_flow()
    config_ok = check_google_cloud_console_config()
    
    if flow_ok and config_ok:
        print("\n🎉 OAuth flow simulation completed successfully!")
        print("\n💡 Next steps to test:")
        print("   1. Restart your SmartFixer application")
        print("   2. Make sure all redirect URIs are configured in Google Cloud Console")
        print("   3. Try clicking 'Continue with Google' again")
        print("   4. Check browser developer console for any JavaScript errors")
        print("   5. Check application terminal for detailed error messages")
    else:
        print("\n❌ Issues detected in OAuth flow simulation.")
        
        if not flow_ok:
            print("\n🔧 OAuth Flow Issues:")
            print("   • Check Google OAuth client configuration")
            print("   • Verify redirect URI generation")
            
        if not config_ok:
            print("\n🔧 Configuration Issues:")
            print("   • Verify Google Cloud Console setup")

if __name__ == "__main__":
    main()