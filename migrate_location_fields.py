#!/usr/bin/env python3
"""
Migration script to add location fields to the users table.
This script adds the 'location' and 'location_enabled' columns to the existing users table.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app and database
from app import app, db
from models import User

def migrate_location_fields():
    """Add location fields to existing users table"""
    with app.app_context():
        # Get the database engine
        engine = db.engine
        
        # Check if columns already exist
        try:
            # Try to query the location column
            db.session.execute(text("SELECT location FROM users LIMIT 1"))
            print("Location columns already exist. No migration needed.")
            return
        except OperationalError:
            # Columns don't exist, proceed with migration
            pass
        
        # Add the new columns
        try:
            # Add location column
            db.session.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR(255)"))
            print("Added 'location' column to users table")
            
            # Add location_enabled column with default value
            db.session.execute(text("ALTER TABLE users ADD COLUMN location_enabled BOOLEAN DEFAULT 0"))
            print("Added 'location_enabled' column to users table")
            
            # Commit the changes
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_location_fields()