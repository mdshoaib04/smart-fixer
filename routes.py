from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_socketio import emit, join_room
from database import db
from models import User, Friendship
from datetime import datetime
from functools import wraps

# Global variables to hold app and socketio instances
app = None
socketio = None

def init_app(flask_app, flask_socketio):
    """Initialize the routes with the Flask app and SocketIO instances"""
    global app, socketio
    app = flask_app
    socketio = flask_socketio
    register_routes()

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes():
    """Register all routes with the Flask app"""
    
    @app.route('/api/search-users', methods=['GET'])
    @require_login
    def api_search_users():
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'users': []})
        
        # Search for users by username, first name, or last name
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.first_name.ilike(f'%{query}%')) |
            (User.last_name.ilike(f'%{query}%'))
        ).limit(20).all()
        
        user_list = []
        for user in users:
            # Check if there's an accepted friendship
            friendship = Friendship.query.filter(
                ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user.id)) |
                ((Friendship.user_id == user.id) & (Friendship.friend_id == current_user.id))
            ).filter(Friendship.status == 'accepted').first()
            
            user_list.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_image_url': user.profile_image_url,
                'is_following': friendship is not None
            })
        
        return jsonify({'users': user_list})

    @app.route('/user/<user_id>')
    @require_login
    def user_profile(user_id):
        """Display user profile page"""
        user = User.query.get(user_id)
        if not user:
            return "User not found", 404
        
        # Check if current user is following this user
        is_following = False
        friendship = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
            ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if friendship:
            is_following = friendship.status == 'accepted'
        
        # Check if current user is viewing their own profile
        is_current_user = (current_user.id == user_id)
        
        # For now, pass default values for the other required variables
        # In a full implementation, these would be fetched from the database
        return render_template('user_profile.html', 
                             user=current_user,  # Current logged-in user
                             target_user=user,   # User whose profile is being viewed
                             is_following=is_following,
                             is_current_user=is_current_user,
                             post_count=0,
                             follower_count=0,
                             following_count=0,
                             posts=[])

    @app.route('/api/follow-user', methods=['POST'])
    @require_login
    def follow_user():
        """API endpoint to follow/unfollow a user"""
        try:
            data = request.get_json()
            target_user_id = data.get('user_id')
            
            if not target_user_id:
                return jsonify({'success': False, 'error': 'User ID is required'}), 400
            
            # Don't allow users to follow themselves
            if target_user_id == current_user.id:
                return jsonify({'success': False, 'error': 'You cannot follow yourself'}), 400
            
            # Check if target user exists
            target_user = User.query.get(target_user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Check if friendship already exists
            existing_friendship = Friendship.query.filter(
                ((Friendship.user_id == current_user.id) & (Friendship.friend_id == target_user_id)) |
                ((Friendship.user_id == target_user_id) & (Friendship.friend_id == current_user.id))
            ).first()
            
            if existing_friendship:
                # If it's a pending request from current user, cancel it
                if existing_friendship.user_id == current_user.id and existing_friendship.status == 'pending':
                    db.session.delete(existing_friendship)
                    db.session.commit()
                    response_data = {'success': True, 'action': 'cancelled'}
                    return jsonify(response_data)
                # If it's an accepted friendship, unfollow
                elif existing_friendship.status == 'accepted':
                    db.session.delete(existing_friendship)
                    db.session.commit()
                    response_data = {'success': True, 'action': 'unfollowed'}
                    return jsonify(response_data)
                # If there's a pending request from target user, accept it
                elif existing_friendship.friend_id == current_user.id and existing_friendship.status == 'pending':
                    existing_friendship.status = 'accepted'
                    db.session.commit()
                    response_data = {'success': True, 'action': 'accepted'}
                    return jsonify(response_data)
            else:
                # Create new friendship request
                new_friendship = Friendship()
                new_friendship.user_id = current_user.id
                new_friendship.friend_id = target_user_id
                new_friendship.status = 'pending'
                db.session.add(new_friendship)
                db.session.commit()
                response_data = {'success': True, 'action': 'requested'}
                return jsonify(response_data)
                
        except Exception as e:
            db.session.rollback()
            print(f"Error following user: {e}")
            return jsonify({'success': False, 'error': 'Failed to update follow status'}), 500

    def update_user_presence(user_id):
        """Update user's last active timestamp and online status"""
        user = User.query.get(user_id)
        if user:
            user.last_active = datetime.now()
            user.is_online = True
            db.session.commit()
            # Emit presence update to all connected clients
            socketio.emit('user_presence_update', {
                'user_id': user_id,
                'is_online': True,
                'last_active': user.last_active.isoformat()
            })
            return True
        return False

    def get_user_presence_status(user_id):
        """Get formatted presence status for a user"""
        user = User.query.get(user_id)
        if not user:
            return {'is_online': False, 'status': 'Offline'}
        
        now = datetime.now()
        last_active = user.last_active or user.last_seen
        
        # If user is marked as online and last active within 5 minutes
        if user.is_online and (now - last_active).total_seconds() <= 300:  # 5 minutes
            return {'is_online': True, 'status': 'online'}
        
        # Calculate time difference
        diff_seconds = (now - last_active).total_seconds()
        diff_minutes = int(diff_seconds / 60)
        
        # If less than 5 minutes ago, still show as active
        if diff_minutes < 5:
            return {'is_online': True, 'status': 'online'}
        
        # If less than 1 hour ago
        if diff_minutes < 60:
            return {
                'is_online': False, 
                'status': f'Active {diff_minutes} minute{"s" if diff_minutes != 1 else ""} ago'
            }
        
        # Same day
        if (now.date() - last_active.date()).days == 0:
            return {
                'is_online': False,
                'status': f'Last seen today at {last_active.strftime("%H:%M")}'
            }
        
        # Yesterday
        if (now.date() - last_active.date()).days == 1:
            return {
                'is_online': False,
                'status': f'Last seen yesterday at {last_active.strftime("%H:%M")}'
            }
        
        # Other days
        return {
            'is_online': False,
            'status': f'Last seen on {last_active.strftime("%d/%m/%Y")} at {last_active.strftime("%H:%M")}'
        }

    @socketio.on('user_activity')
    def handle_user_activity(data):
        """Handle user activity events to update presence"""
        if current_user.is_authenticated:
            update_user_presence(current_user.id)

    @socketio.on('connect')
    def handle_connect_presence():
        """Handle user connection to update online status"""
        if current_user.is_authenticated:
            update_user_presence(current_user.id)
            # Join user's personal room for presence notifications
            join_room(f'user_{current_user.id}')
            print(f'User {current_user.username} connected')

    @socketio.on('disconnect')
    def handle_disconnect_presence():
        """Handle user disconnection to update online status"""
        if current_user.is_authenticated:
            # Mark user as offline
            user = User.query.get(current_user.id)
            if user:
                user.is_online = False
                db.session.commit()
                # Emit presence update to all connected clients
                socketio.emit('user_presence_update', {
                    'user_id': current_user.id,
                    'is_online': False,
                    'last_active': user.last_active.isoformat() if user.last_active else None
                })
            print(f'User {current_user.username} disconnected')

    @app.route('/api/user-presence/<user_id>')
    def get_user_presence(user_id):
        """API endpoint to get user presence status"""
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401
        
        status = get_user_presence_status(user_id)
        return jsonify(status)