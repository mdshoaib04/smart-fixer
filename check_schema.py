#!/usr/bin/env python3
"""
Check database schema
This script checks the current database schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def check_schema():
    """Check the current database schema"""
    with app.app_context():
        # Connect to the database
        conn = db.engine.connect()
        
        try:
            # Check table structure
            result = conn.execute("PRAGMA table_info(notifications)")
            columns = result.fetchall()
            
            print("Current notifications table structure:")
            for column in columns:
                print(f"  {column[1]} ({column[2]}) - Not Null: {column[3]}, Default: {column[4]}, PK: {column[5]}")
            
        except Exception as e:
            print(f"Error checking schema: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    check_schema()