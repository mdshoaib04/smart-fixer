from app import app, db
from models import User
from sqlalchemy import text

def update_db():
    with app.app_context():
        # Check if columns exist
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        with db.engine.connect() as conn:
            if 'current_streak' not in columns:
                print("Adding current_streak column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0"))
            
            if 'longest_streak' not in columns:
                print("Adding longest_streak column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0"))
                
            if 'last_streak_date' not in columns:
                print("Adding last_streak_date column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN last_streak_date DATE"))
                
            conn.commit()
            print("Database updated successfully!")

if __name__ == "__main__":
    update_db()
