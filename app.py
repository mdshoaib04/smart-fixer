from flask import Flask, render_template, redirect, url_for, request, jsonify, session, send_from_directory
from database import db
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
import re
import sys
import socket

load_dotenv()
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Suppress all logging except critical errors
logging.basicConfig(level=logging.CRITICAL)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or 'your-secret-key-here'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session configuration for better persistence
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_page'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
# Remember user sessions
login_manager.session_protection = 'strong'

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Add support for PWA files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize database with app
db.init_app(app)

# Initialize SocketIO with proper configuration
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import and register routes after app and socketio are defined
import routes
routes.init_app(app, socketio)

with app.app_context():
    import models
    # Only create tables if they don't exist, don't drop them
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    try:
        return User.query.get(user_id)
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

# Test route to check if basic routing works
@app.route('/test-direct')
def test_direct():
    return "Direct route in app.py works!"

# Add main routes directly to test
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload_or_write'))
    return render_template('welcome.html')

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

@app.route('/upload-or-write')
def upload_or_write():
    from flask_login import login_required
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('upload_or_write.html', user=current_user)

@app.route('/editor')
def editor():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('editor.html', user=current_user)

@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('profile.html', user=current_user)

@app.route('/posts')
def posts():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('posts.html', user=current_user)

@app.route('/explore')
def explore():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('explore.html', user=current_user)

@app.route('/notifications')
def notifications():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('notifications.html', user=current_user)

@app.route('/time-tracker')
def time_tracker():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('time_tracker.html', user=current_user)

@app.route('/flexible-time-tracker')
def flexible_time_tracker():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('flexible_time_tracker.html', user=current_user)

@app.route('/chat')
def chat():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page'))
    return render_template('chat.html', user=current_user)

# Essential API routes
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email_or_username = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email_or_username or not password:
        return jsonify({'success': False, 'message': 'Email/username and password are required'})
    
    from models import User
    # Find user by email or username
    user = User.query.filter(
        (User.email == email_or_username) | (User.username == email_or_username)
    ).first()
    
    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    username = data.get('username', '').strip()
    
    # Validation
    if not name or not email or not password or not username:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Email validation
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({'success': False, 'message': 'Invalid email format'})
    
    # Username validation
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({'success': False, 'message': 'Username must be 3-20 characters and contain only letters, numbers, and underscores'})
    
    # Password validation
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'})
    
    from models import User
    # Check if user already exists by email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'})
    
    # Check if username already exists
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return jsonify({'success': False, 'message': 'Username already taken. Please choose a different username.'})
    
    # Create new user
    try:
        user = User(
            username=username,
            email=email,
            first_name=name.split()[0] if name.split() else name,
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            profession='student'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Account created successfully', 'username': username})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to create account'})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/static/uploads/profiles/<filename>')
def uploaded_file(filename):
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'profiles')
    return send_from_directory(upload_dir, filename)

@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == '__main__':
    import sys
    port = 5000
    if '--port' in sys.argv:
        try:
            port_index = sys.argv.index('--port') + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
        except (ValueError, IndexError):
            print("Invalid port specified, using default port 5000")
    
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get local IP
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🚀 SMARTFIXER CODE REVIEWER STARTING...")
    print("="*60)
    print("📡 Server Status: Starting...")
    print(f"🌐 Main URL: http://localhost:{port}")
    print(f"🔗 Alternative URL: http://127.0.0.1:{port}")
    print(f"💻 Local Network: http://{local_ip}:{port}")
    print("="*60)
    print("✅ Click on any URL above to access your SmartFixer!")
    print("🛑 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=port)






