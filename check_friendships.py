import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), 'smartfixer.db')
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check all friendships (table name is 'friendships')
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

# Check all users
try:
    cursor.execute("SELECT id, username, first_name, last_name FROM users")
    users = cursor.fetchall()
    
    print("\nUsers in database:")
    for user in users:
        print(user)
except sqlite3.OperationalError as e:
    print(f"Error querying users table: {e}")

conn.close()