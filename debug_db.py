#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

with app.app_context():
    # Print the actual database URI being used
    print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    
    # Try to query the users table
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        print("Columns in users table:", columns)
        
        if 'last_active' in columns:
            print("last_active column exists")
        else:
            print("last_active column MISSING")
            
        # Try to query a user
        user = User.query.first()
        if user:
            print("Successfully queried user:", user.id)
        else:
            print("No users found in database")
            
    except Exception as e:
        print("Error querying database:", e)
        import traceback
        traceback.print_exc()