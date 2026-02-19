
from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}")
