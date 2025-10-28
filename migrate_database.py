#!/usr/bin/env python3
"""
Database migration script to add last_active column to User model.
This script should be run once after updating the models.py file.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def migrate_database():
    """Add last_active column to users table"""
    with app.app_context():
        # Check if the column already exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'last_active' not in columns:
            print("Adding last_active column to users table...")
            # For SQLite, we need to recreate the table
            try:
                # Get all existing users
                users_data = []
                users = User.query.all()
                for user in users:
                    users_data.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'password_hash': user.password_hash,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'profile_image_url': user.profile_image_url,
                        'profile_image_path': user.profile_image_path,
                        'bio': user.bio,
                        'profession': user.profession,
                        'oauth_provider': user.oauth_provider,
                        'oauth_id': user.oauth_id,
                        'is_user_active': user.is_user_active,
                        'last_seen': user.last_seen,
                        'is_online': user.is_online,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at,
                        'location': getattr(user, 'location', None),
                        'location_enabled': getattr(user, 'location_enabled', False)
                    })
                
                # Drop the old table
                User.__table__.drop(db.engine)
                
                # Create the new table with last_active column
                db.create_all()
                
                # Reinsert the users with default last_active values
                for user_data in users_data:
                    # Set last_active to last_seen if available, otherwise to current time
                    user_data['last_active'] = user_data['last_seen']
                    user = User(**user_data)
                    db.session.add(user)
                
                db.session.commit()
                print("Successfully added last_active column to users table!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error migrating database: {e}")
                return False
        else:
            print("last_active column already exists in users table.")
            return True

if __name__ == "__main__":
    print("Starting database migration...")
    if migrate_database():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)