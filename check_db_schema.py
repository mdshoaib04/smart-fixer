#!/usr/bin/env python3
import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the schema for the users table
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
result = cursor.fetchone()

if result:
    print("Users table schema:")
    print(result[0])
else:
    print("Users table not found")

conn.close()