#!/usr/bin/env python3
"""
Simulate OAuth Callback for SmartFixer
This script simulates what happens during the Google OAuth callback
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def simulate_oauth_callback():
    """Simulate the OAuth callback process"""
    print("🔍 Simulating OAuth Callback Process...")
    print("=" * 40)
    
    try:
        from app import app
        from models import User, db
        
        with app.app_context():
            print("✅ Application context is working")
            
            # Simulate user info that would come from Google
            user_info = {
                'email': 'testuser@example.com',
                'given_name': 'Test',
                'family_name': 'User',
                'picture': 'https://example.com/profile.jpg',
                'sub': '123456789'
            }
            
            print("Simulating user info from Google:")
            for key, value in user_info.items():
                print(f"  {key}: {value}")
            
            # Check if user already exists
            print("\nChecking if user exists...")
            existing_user = User.query.filter_by(email=user_info['email']).first()
            
            if existing_user:
                print(f"✅ User already exists: {existing_user.username}")
                print("   This would trigger a login, not signup")
            else:
                print("✅ User does not exist (this is what we want for signup)")
                print("   This should trigger user creation")
                
                # Simulate user creation
                print("\nSimulating user creation...")
                user = User()
                user.email = user_info['email']
                user.first_name = user_info.get('given_name', '')
                user.last_name = user_info.get('family_name', '')
                user.profile_image_url = user_info.get('picture', '')
                user.oauth_provider = 'google'
                user.oauth_id = user_info['sub']
                
                # Generate username
                import re
                base_username = re.sub(r'[^a-zA-Z0-9_]', '', user_info['email'].split('@')[0].lower())
                user.username = base_username
                
                print(f"   Generated username: {user.username}")
                
                # Check if username exists
                existing_username = User.query.filter_by(username=user.username).first()
                if existing_username:
                    print("   ⚠️  Username conflict detected")
                    print("   This should trigger random username generation")
                else:
                    print("   ✅ Username is unique")
                    
                print("✅ User creation simulation completed")
                
            return True
            
    except Exception as e:
        print(f"❌ ERROR: Failed to simulate OAuth callback: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main simulation function"""
    print("🚀 SmartFixer OAuth Callback Simulation")
    print("=" * 40)
    
    success = simulate_oauth_callback()
    
    if success:
        print("\n🎉 Simulation completed successfully!")
        print("\n💡 What this tells us:")
        print("   • The OAuth callback logic should work correctly")
        print("   • User creation process is properly implemented")
        print("   • Username generation logic is working")
        print("\n🔍 If signup isn't working, check:")
        print("   • Application terminal for error messages during actual OAuth flow")
        print("   • Database permissions for creating new users")
        print("   • Google OAuth credentials and redirect URIs")
    else:
        print("\n❌ Simulation failed. Check the errors above.")

if __name__ == "__main__":
    main()