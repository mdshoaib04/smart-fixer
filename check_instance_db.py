import sqlite3
import os

# Connect to the database in the instance directory
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check all tables
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Show table structure
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"    Columns:")
        for column in columns:
            print(f"      - {column[1]} ({column[2]})")
        print()
        
except sqlite3.OperationalError as e:
    print(f"Error querying database: {e}")

# Check friendships table specifically
try:
    cursor.execute("SELECT * FROM friendships")
    friendships = cursor.fetchall()
    
    print("Friendships in database:")
    if friendships:
        for friendship in friendships:
            print(friendship)
    else:
        print("No friendships found")
except sqlite3.OperationalError as e:
    print(f"Error querying friendships table: {e}")

# Check users table
try:
    cursor.execute("SELECT id, username, first_name, last_name FROM users")
    users = cursor.fetchall()
    
    print("\nUsers in database:")
    for user in users:
        print(user)
except sqlite3.OperationalError as e:
    print(f"Error querying users table: {e}")

conn.close()