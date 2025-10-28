import os
import sys
from app import app, db
from models import User

# Set environment variables for testing
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SESSION_SECRET', 'test-secret')

with app.app_context():
    # Create a test user
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        profession='student'
    )
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    print('Test user created successfully')