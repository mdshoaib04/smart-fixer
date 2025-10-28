#!/usr/bin/env python3
"""
Test App Routes for SmartFixer
This script properly tests if OAuth routes are registered
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_app_routes():
    """Test if app routes are properly registered"""
    print("🔍 Testing App Route Registration...")
    print("=" * 35)
    
    try:
        # Import app and routes in the correct order
        from app import app
        
        # Import routes after app is created to avoid circular imports
        import routes
        
        print("✅ App and routes imported successfully")
        
        # Print all registered routes
        print("\nRegistered routes containing 'google' or 'callback':")
        google_routes = []
        callback_routes = []
        
        for rule in app.url_map.iter_rules():
            if 'google' in rule.rule:
                google_routes.append((rule.rule, rule.endpoint))
                print(f"  • {rule.rule} -> {rule.endpoint}")
            elif 'callback' in rule.rule:
                callback_routes.append((rule.rule, rule.endpoint))
                print(f"  • {rule.rule} -> {rule.endpoint}")
                
        if google_routes:
            print("✅ Google-related routes found")
        else:
            print("❌ No Google-related routes found")
            
        if callback_routes:
            print("✅ Callback routes found")
        else:
            print("❌ No callback routes found")
            
        return len(google_routes) > 0 and len(callback_routes) > 0
        
    except Exception as e:
        print(f"❌ ERROR: Failed to test app routes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 SmartFixer App Route Test")
    print("=" * 30)
    
    routes_ok = test_app_routes()
    
    if routes_ok:
        print("\n🎉 All OAuth routes are properly registered!")
        print("\n💡 Next steps:")
        print("   1. Restart your SmartFixer application")
        print("   2. Try clicking 'Continue with Google' again")
        print("   3. Check if you're redirected to Google login")
    else:
        print("\n❌ OAuth routes are not registered.")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Make sure you're running the app with: python app.py")
        print("   2. Check that routes.py is properly structured")
        print("   3. Verify route decorators are correctly applied")

if __name__ == "__main__":
    main()