
import os

file_path = r'c:\Users\Admin\OneDrive\Desktop\SmartFixer\routes.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Reconstruct the top part
header = """from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_socketio import emit, join_room
from database import db
from models import User, Friendship, FollowRequest, Follower, Notification, Message
from datetime import datetime
from functools import wraps

# Add imports for interactive program execution
import threading
import queue
import subprocess
import tempfile
import os
import shutil
import json
import time

# Global variables to hold app and socketio instances
app = None
socketio = None

# Dictionary to store running processes
running_processes = {}


def init_app(flask_app, flask_socketio):
    \"\"\"Initialize the routes with the Flask app and SocketIO instances\"\"\"
    global app, socketio
    app = flask_app
    socketio = flask_socketio
    register_routes()
    register_socketio_events()

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes():
    \"\"\"Register all routes with the Flask app\"\"\"
    
    @app.route('/api/search-users', methods=['GET'])
    @require_login
    def api_search_users():
"""

# Find where the body of api_search_users starts in the current broken file
# It starts at line 37: "        query = request.args.get('q', '').strip()"
# We need to find this line and keep everything after it
start_index = -1
for i, line in enumerate(lines):
    if "query = request.args.get('q', '').strip()" in line:
        start_index = i
        break

if start_index != -1:
    rest_of_file = "".join(lines[start_index:])
    full_content = header + rest_of_file
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print("Successfully reconstructed routes.py")
else:
    print("Could not find start of api_search_users body")
