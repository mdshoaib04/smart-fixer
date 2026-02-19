import sqlite3
import os

db_path = 'instance/smartfixer.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create conversations table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id VARCHAR NOT NULL,
    user2_id VARCHAR NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user1_id) REFERENCES users(id),
    FOREIGN KEY(user2_id) REFERENCES users(id)
)
""")
print("Ensured conversations table exists.")

# 2. Add new columns to messages table
cursor.execute("PRAGMA table_info(messages)")
columns = [col[1] for col in cursor.fetchall()]

new_columns = [
    ("conversation_id", "INTEGER"),
    ("message_type", "VARCHAR(50) DEFAULT 'text'"),
    ("is_read", "BOOLEAN DEFAULT 0")
]

for col_name, col_type in new_columns:
    if col_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except Exception as e:
            print(f"Error adding {col_name}: {e}")
    else:
        print(f"Column {col_name} already exists.")

conn.commit()
conn.close()
print("Migration completed.")
