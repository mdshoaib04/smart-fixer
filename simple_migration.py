#!/usr/bin/env python3
"""
Simple database migration script to add last_active column to User model.
"""

import sys
import os
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_database():
    """Add last_active column to users table using raw SQL"""
    with app.app_context():
        try:
            # Check if the column already exists by trying to query it
            try:
                db.session.execute(db.text("SELECT last_active FROM users LIMIT 1"))
                print("last_active column already exists in users table.")
                return True
            except Exception:
                # Column doesn't exist, so we need to add it
                print("Adding last_active column to users table...")
                
                # For SQLite, add the column
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN last_active DATETIME"))
                
                # Update all existing users with a default last_active value
                db.session.execute(db.text("UPDATE users SET last_active = datetime('now') WHERE last_active IS NULL"))
                
                db.session.commit()
                print("Successfully added last_active column to users table!")
                return True
                
        except Exception as e:
            db.session.rollback()
            print(f"Error migrating database: {e}")
            return False

if __name__ == "__main__":
    print("Starting simple database migration...")
    if migrate_database():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)