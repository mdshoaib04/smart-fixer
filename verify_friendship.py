import sqlite3
import os

# Connect to the database in the instance directory
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check friendships table
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

conn.close()