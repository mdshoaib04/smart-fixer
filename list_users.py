import os
import sys
from app import app, db
from models import User

# Set environment variables for testing
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SESSION_SECRET', 'test-secret')

with app.app_context():
    # List all users
    users = User.query.all()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}")