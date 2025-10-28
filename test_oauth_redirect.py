import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

print("Testing OAuth Redirect URI Generation...")
print("=" * 50)

# Import app and routes
try:
    from app import app
    from routes import google, github
    
    print("✅ App and routes imported successfully")
    
    # Test different scenarios for redirect URI generation
    test_scenarios = [
        {'host': 'localhost', 'port': 5000, 'scheme': 'http'},
        {'host': '127.0.0.1', 'port': 5000, 'scheme': 'http'},
        {'host': 'localhost', 'port': 80, 'scheme': 'http'},
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\nScenario {i+1}: {scenario['scheme']}://{scenario['host']}:{scenario['port']}")
        with app.test_request_context('/', 
                                    environ_overrides={
                                        'wsgi.url_scheme': scenario['scheme'],
                                        'HTTP_HOST': f"{scenario['host']}:{scenario['port']}"
                                    }):
            from flask import url_for, request
            try:
                callback_url = url_for('google_callback', _external=True)
                print(f"  Generated URL: {callback_url}")
                
                # Check if port is included
                if f":{scenario['port']}" in callback_url or scenario['port'] in [80, 443]:
                    print("  ✅ Port correctly included in URL")
                else:
                    print("  ❌ Port missing from URL")
                    
            except Exception as e:
                print(f"  ❌ Error generating URL: {e}")
    
    # Test our custom redirect URI generation
    print("\nTesting custom redirect URI generation:")
    print("-" * 30)
    
    # Simulate our fixed approach
    scheme = 'http'
    host = 'localhost'
    port = 5000
    
    custom_redirect_uri = f"{scheme}://{host}:{port}/callback/google"
    print(f"Custom redirect URI: {custom_redirect_uri}")
    
    if f":{port}" in custom_redirect_uri:
        print("✅ Custom approach correctly includes port")
    else:
        print("❌ Custom approach missing port")
        
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    import traceback
    traceback.print_exc()

print("\nRecommendations:")
print("-" * 15)
print("1. Make sure the exact URI 'http://localhost:5000/callback/google' is registered")
print("   in your Google Cloud Console OAuth client")
print("2. Double-check there are no extra spaces or characters in the URI")
print("3. Try using 'http://127.0.0.1:5000/callback/google' as an alternative")
print("4. If issues persist, try creating a new OAuth client in Google Cloud Console")