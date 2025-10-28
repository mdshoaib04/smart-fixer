#!/usr/bin/env python3
import sqlite3
import os

# Connect directly to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.db')
print(f"Checking database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
table_exists = cursor.fetchone()

if table_exists:
    print("Users table exists")
    
    # Get the schema for the users table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("Columns in users table:")
    column_names = []
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")
        column_names.append(column[1])
    
    # Check if last_active column exists
    if 'last_active' in column_names:
        print("\n✓ last_active column exists")
    else:
        print("\n✗ last_active column is MISSING")
        
    # Check if there are any rows in the table
    cursor.execute("SELECT COUNT(*) FROM users")
    row_count = cursor.fetchone()[0]
    print(f"\nNumber of users in table: {row_count}")
    
else:
    print("Users table does not exist")

conn.close()