"""
Database migration script to add missing columns to messages table
"""
import sqlite3
import os

# Path to database
db_path = 'smartfixer.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(messages)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Existing columns in messages table: {columns}")

# Add missing columns
columns_to_add = [
    ("code_snippet", "TEXT"),
    ("file_attachment", "VARCHAR(255)"),
    ("file_type", "VARCHAR(50)")
]

for col_name, col_type in columns_to_add:
    if col_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name} ({col_type})")
        except sqlite3.OperationalError as e:
            print(f"Error adding {col_name}: {e}")
    else:
        print(f"  Column {col_name} already exists")

# Commit changes
conn.commit()
conn.close()

print("\nDatabase migration completed successfully!")
print("Please restart the server for changes to take effect.")
