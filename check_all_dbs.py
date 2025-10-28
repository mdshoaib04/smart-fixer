#!/usr/bin/env python3
import sqlite3
import os

db_files = ['site.db', 'app.db', 'smartfixer.db']

for db_file in db_files:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_file)
    if os.path.exists(db_path):
        print(f"\n=== Checking {db_file} ===")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if cursor.fetchone():
                # Get the schema for the users table
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
                result = cursor.fetchone()
                if result:
                    print("Users table schema:")
                    print(result[0])
                else:
                    print("Users table exists but schema not found")
            else:
                print("Users table not found")
            
            conn.close()
        except Exception as e:
            print(f"Error checking {db_file}: {e}")
    else:
        print(f"{db_file} not found")