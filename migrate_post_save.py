#!/usr/bin/env python3
"""
Migration script to add post_saves table to the database.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app and database
from app import app, db
from models import PostSave

def migrate_post_save_table():
    """Create the post_saves table"""
    with app.app_context():
        # Check if table already exists
        try:
            # Try to query the post_saves table
            db.session.execute(text("SELECT id FROM post_saves LIMIT 1"))
            print("Post saves table already exists. No migration needed.")
            return
        except OperationalError:
            # Table doesn't exist, proceed with migration
            pass
        
        # Create the post_saves table
        try:
            # Create all tables (this will only create missing tables)
            db.create_all()
            print("Created 'post_saves' table successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_post_save_table()