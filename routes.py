from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_socketio import emit, join_room
from database import db
from models import User, Friendship, FollowRequest, Follower, Notification
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
        
        # Check if current user is following this user (using new Follower model)
        is_following = Follower.query.filter_by(
            user_id=user_id, 
            follower_id=current_user.id
        ).first() is not None
        
        # Check if target user is following current user (for follow back functionality)
        is_following_me = Follower.query.filter_by(
            user_id=current_user.id, 
            follower_id=user_id
        ).first() is not None
        
        # Check if current user is viewing their own profile
        is_current_user = (current_user.id == user_id)
        
        # Calculate post count
        post_count = 0  # In a full implementation, this would query posts
        
        # Calculate follower and following counts
        follower_count = Follower.query.filter_by(user_id=user_id).count()
        following_count = Follower.query.filter_by(follower_id=user_id).count()
        
        # For now, pass default values for the other required variables
        # In a full implementation, these would be fetched from the database
        return render_template('user_profile.html', 
                             user=current_user,  # Current logged-in user
                             target_user=user,   # User whose profile is being viewed
                             is_following=is_following,
                             is_following_me=is_following_me,  # Whether target user is following current user
                             is_current_user=is_current_user,
                             post_count=post_count,
                             follower_count=follower_count,
                             following_count=following_count,
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

    @app.route('/api/follow/request', methods=['POST'])
    @require_login
    def follow_request():
        """API endpoint to send a follow request"""
        try:
            data = request.get_json()
            to_user_id = data.get('to_user_id')
            
            if not to_user_id:
                return jsonify({'success': False, 'error': 'Target user ID is required'}), 400
            
            # Don't allow users to follow themselves
            if to_user_id == current_user.id:
                return jsonify({'success': False, 'error': 'You cannot follow yourself'}), 400
            
            # Check if target user exists
            target_user = User.query.get(to_user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Check if already following
            existing_follower = Follower.query.filter_by(user_id=to_user_id, follower_id=current_user.id).first()
            if existing_follower:
                return jsonify({'success': False, 'error': 'You are already following this user'}), 400
            
            # Check if follow request already exists
            existing_request = FollowRequest.query.filter_by(
                from_user_id=current_user.id, 
                to_user_id=to_user_id
            ).first()
            
            if existing_request:
                if existing_request.status == 'pending':
                    return jsonify({'success': False, 'error': 'Follow request already sent'}), 400
                elif existing_request.status == 'accepted':
                    return jsonify({'success': False, 'error': 'You are already following this user'}), 400
                elif existing_request.status == 'rejected':
                    # Update rejected request to pending
                    existing_request.status = 'pending'
                    existing_request.updated_at = datetime.now()
                    db.session.commit()
                    
                    # Create notification for target user
                    notification = Notification()
                    notification.user_id = to_user_id
                    notification.message = f"{current_user.full_name} requested to follow you"
                    notification.type = 'follow_request'
                    notification.from_user_id = current_user.id
                    notification.follow_request_id = existing_request.id  # Link to follow request
                    db.session.add(notification)
                    db.session.commit()
                    
                    # Emit notification to target user with the follow request ID
                    socketio.emit('new_notification', {
                        'user_id': to_user_id,
                        'message': f"{current_user.full_name} requested to follow you",
                        'type': 'follow_request',
                        'follow_request_id': existing_request.id  # Include the follow request ID
                    }, room=f'user_{to_user_id}')
                    
                    # Emit notification update to update badge
                    socketio.emit('notification_update', {
                        'user_id': to_user_id,
                        'count': Notification.query.filter_by(user_id=to_user_id, read_status=False).count()
                    }, room=f'user_{to_user_id}')
                    
                    return jsonify({'success': True, 'message': 'Follow request sent'})
            
            # Create new follow request
            follow_request = FollowRequest()
            follow_request.from_user_id = current_user.id
            follow_request.to_user_id = to_user_id
            follow_request.status = 'pending'
            db.session.add(follow_request)
            db.session.flush()  # Ensure the follow request gets an ID
            
            # Create notification for target user
            notification = Notification()
            notification.user_id = to_user_id
            notification.message = f"{current_user.full_name} requested to follow you"
            notification.type = 'follow_request'
            notification.from_user_id = current_user.id
            notification.follow_request_id = follow_request.id  # Link to follow request
            db.session.add(notification)
            db.session.commit()
            
            # Emit notification to target user with the follow request ID
            socketio.emit('new_notification', {
                'user_id': to_user_id,
                'message': f"{current_user.full_name} requested to follow you",
                'type': 'follow_request',
                'follow_request_id': follow_request.id  # Include the follow request ID
            }, room=f'user_{to_user_id}')
            
            # Emit notification update to update badge
            socketio.emit('notification_update', {
                'user_id': to_user_id,
                'count': Notification.query.filter_by(user_id=to_user_id, read_status=False).count()
            }, room=f'user_{to_user_id}')
            
            return jsonify({'success': True, 'message': 'Follow request sent'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error sending follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to send follow request'}), 500

    @app.route('/api/follow/accept', methods=['POST'])
    @require_login
    def accept_follow_request():
        """API endpoint to accept a follow request"""
        try:
            data = request.get_json()
            request_id = data.get('request_id')
            
            if not request_id:
                return jsonify({'success': False, 'error': 'Request ID is required'}), 400
            
            # Get the follow request
            follow_request = FollowRequest.query.filter_by(
                id=request_id, 
                to_user_id=current_user.id,
                status='pending'
            ).first()
            
            if not follow_request:
                return jsonify({'success': False, 'error': 'Follow request not found or already processed'}), 404
            
            # Update request status
            follow_request.status = 'accepted'
            follow_request.updated_at = datetime.now()
            
            # Add to followers table (current user is followed by the requester)
            follower = Follower()
            follower.user_id = current_user.id  # The user being followed
            follower.follower_id = follow_request.from_user_id  # The user who is following
            db.session.add(follower)
            
            # Add reverse relationship (requester is now following current user)
            reverse_follower = Follower()
            reverse_follower.user_id = follow_request.from_user_id  # The requester
            reverse_follower.follower_id = current_user.id  # Current user (who accepted)
            db.session.add(reverse_follower)
            
            # Create notification for the user who sent the request
            notification = Notification()
            notification.user_id = follow_request.from_user_id
            notification.message = f"{current_user.full_name} accepted your follow request"
            notification.type = 'accepted'
            notification.from_user_id = current_user.id
            db.session.add(notification)
            
            db.session.commit()
            
            # Emit notification to the user who sent the request
            socketio.emit('new_notification', {
                'user_id': follow_request.from_user_id,
                'message': f"{current_user.full_name} accepted your follow request",
                'type': 'accepted'
            }, room=f'user_{follow_request.from_user_id}')
            
            # Emit follow update events to both users
            socketio.emit('follow_update', {
                'user_id': current_user.id,
                'follower_count': Follower.query.filter_by(user_id=current_user.id).count(),
                'following_count': Follower.query.filter_by(follower_id=current_user.id).count()
            }, room=f'user_{current_user.id}')
            
            socketio.emit('follow_update', {
                'user_id': follow_request.from_user_id,
                'follower_count': Follower.query.filter_by(user_id=follow_request.from_user_id).count(),
                'following_count': Follower.query.filter_by(follower_id=follow_request.from_user_id).count()
            }, room=f'user_{follow_request.from_user_id}')
            
            return jsonify({'success': True, 'message': 'Follow request accepted'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error accepting follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to accept follow request'}), 500

    @app.route('/api/follow/reject', methods=['POST'])
    @require_login
    def reject_follow_request():
        """API endpoint to reject a follow request"""
        try:
            data = request.get_json()
            request_id = data.get('request_id')
            
            if not request_id:
                return jsonify({'success': False, 'error': 'Request ID is required'}), 400
            
            # Get the follow request
            follow_request = FollowRequest.query.filter_by(
                id=request_id, 
                to_user_id=current_user.id,
                status='pending'
            ).first()
            
            if not follow_request:
                return jsonify({'success': False, 'error': 'Follow request not found or already processed'}), 404
            
            # Update request status
            follow_request.status = 'rejected'
            follow_request.updated_at = datetime.now()
            
            # Optionally create notification for the user who sent the request
            notification = Notification()
            notification.user_id = follow_request.from_user_id
            notification.message = f"Your follow request to {current_user.full_name} was declined"
            notification.type = 'rejected'
            notification.from_user_id = current_user.id
            db.session.add(notification)
            
            db.session.commit()
            
            # Emit notification to the user who sent the request
            socketio.emit('new_notification', {
                'user_id': follow_request.from_user_id,
                'message': f"Your follow request to {current_user.full_name} was declined",
                'type': 'rejected'
            }, room=f'user_{follow_request.from_user_id}')
            
            return jsonify({'success': True, 'message': 'Follow request rejected'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error rejecting follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to reject follow request'}), 500

    @app.route('/api/follow/direct', methods=['POST'])
    @require_login
    def direct_follow():
        """API endpoint for direct follow (public accounts)"""
        try:
            data = request.get_json()
            to_user_id = data.get('to_user_id')
            
            if not to_user_id:
                return jsonify({'success': False, 'error': 'Target user ID is required'}), 400
            
            # Don't allow users to follow themselves
            if to_user_id == current_user.id:
                return jsonify({'success': False, 'error': 'You cannot follow yourself'}), 400
            
            # Check if target user exists
            target_user = User.query.get(to_user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Check if already following
            existing_follower = Follower.query.filter_by(user_id=to_user_id, follower_id=current_user.id).first()
            if existing_follower:
                return jsonify({'success': False, 'error': 'You are already following this user'}), 400
            
            # Add to followers table directly (for public accounts)
            follower = Follower()
            follower.user_id = to_user_id  # The user being followed
            follower.follower_id = current_user.id  # The user who is following
            db.session.add(follower)
            
            # Check for mutual follow (follow back)
            mutual_follow = Follower.query.filter_by(user_id=current_user.id, follower_id=to_user_id).first()
            if mutual_follow:
                # Both users are following each other - create notification for follow back
                notification = Notification()
                notification.user_id = to_user_id
                notification.message = f"{current_user.full_name} followed you back"
                notification.type = 'follow_back'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                # Emit notification to target user
                socketio.emit('new_notification', {
                    'user_id': to_user_id,
                    'message': f"{current_user.full_name} followed you back",
                    'type': 'follow_back'
                }, room=f'user_{to_user_id}')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Successfully followed user'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error following user: {e}")
            return jsonify({'success': False, 'error': 'Failed to follow user'}), 500

    @app.route('/api/follow/back', methods=['POST'])
    @require_login
    def follow_back():
        """API endpoint for follow back functionality"""
        try:
            data = request.get_json()
            to_user_id = data.get('to_user_id')
            
            if not to_user_id:
                return jsonify({'success': False, 'error': 'Target user ID is required'}), 400
            
            # Don't allow users to follow themselves
            if to_user_id == current_user.id:
                return jsonify({'success': False, 'error': 'You cannot follow yourself'}), 400
            
            # Check if target user exists
            target_user = User.query.get(to_user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Check if already following
            existing_follower = Follower.query.filter_by(user_id=to_user_id, follower_id=current_user.id).first()
            if existing_follower:
                return jsonify({'success': False, 'error': 'You are already following this user'}), 400
            
            # Check if the target user is already following the current user (mutual follow check)
            is_following_me = Follower.query.filter_by(user_id=current_user.id, follower_id=to_user_id).first()
            
            if is_following_me:
                # This is a mutual follow - both users follow each other
                # Add to followers table directly
                follower = Follower()
                follower.user_id = to_user_id  # The user being followed
                follower.follower_id = current_user.id  # The user who is following
                db.session.add(follower)
                
                # Create notification for both users
                notification = Notification()
                notification.user_id = to_user_id
                notification.message = f"{current_user.full_name} followed you back"
                notification.type = 'follow_back'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                # Emit notification to target user
                socketio.emit('new_notification', {
                    'user_id': to_user_id,
                    'message': f"{current_user.full_name} followed you back",
                    'type': 'follow_back'
                }, room=f'user_{to_user_id}')
                
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Successfully followed user back', 'mutual': True})
            else:
                # Target user is not following current user, send follow request
                # Check if follow request already exists
                existing_request = FollowRequest.query.filter_by(
                    from_user_id=current_user.id,
                    to_user_id=to_user_id
                ).first()
                
                if existing_request:
                    if existing_request.status == 'pending':
                        return jsonify({'success': False, 'error': 'Follow request already sent'}), 400
                    elif existing_request.status == 'accepted':
                        return jsonify({'success': False, 'error': 'You are already following this user'}), 400
                    elif existing_request.status == 'rejected':
                        # Update rejected request to pending
                        existing_request.status = 'pending'
                        existing_request.updated_at = datetime.now()
                        db.session.commit()
                        
                        # Create notification for target user
                        notification = Notification()
                        notification.user_id = to_user_id
                        notification.message = f"{current_user.full_name} wants to follow you"
                        notification.type = 'follow_request'
                        notification.from_user_id = current_user.id
                        db.session.add(notification)
                        db.session.commit()
                        
                        # Emit notification to target user
                        socketio.emit('new_notification', {
                            'user_id': to_user_id,
                            'message': f"{current_user.full_name} wants to follow you",
                            'type': 'follow_request'
                        }, room=f'user_{to_user_id}')
                        
                        return jsonify({'success': True, 'message': 'Follow request sent'})
                
                # Create new follow request
                follow_request = FollowRequest()
                follow_request.from_user_id = current_user.id
                follow_request.to_user_id = to_user_id
                follow_request.status = 'pending'
                db.session.add(follow_request)
                
                # Create notification for target user
                notification = Notification()
                notification.user_id = to_user_id
                notification.message = f"{current_user.full_name} wants to follow you"
                notification.type = 'follow_request'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                db.session.commit()
                
                # Emit notification to target user
                socketio.emit('new_notification', {
                    'user_id': to_user_id,
                    'message': f"{current_user.full_name} wants to follow you",
                    'type': 'follow_request'
                }, room=f'user_{to_user_id}')
                
                return jsonify({'success': True, 'message': 'Follow request sent'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error following user back: {e}")
            return jsonify({'success': False, 'error': 'Failed to follow user back'}), 500

    @app.route('/followers/<user_id>')
    @require_login
    def get_followers(user_id):
        """API endpoint to get followers list"""
        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get followers
            followers = db.session.query(Follower, User).join(User, Follower.follower_id == User.id).filter(
                Follower.user_id == user_id
            ).all()
            
            followers_list = []
            for follower_record, follower_user in followers:
                # Check if current user is following this follower
                is_following = Follower.query.filter_by(
                    user_id=follower_user.id,
                    follower_id=current_user.id
                ).first() is not None
                
                followers_list.append({
                    'id': follower_user.id,
                    'username': follower_user.username,
                    'first_name': follower_user.first_name,
                    'last_name': follower_user.last_name,
                    'profile_image_url': follower_user.profile_image_url,
                    'is_following': is_following,
                    'followed_at': follower_record.created_at.isoformat()
                })
            
            return jsonify({'success': True, 'followers': followers_list})
                
        except Exception as e:
            print(f"Error getting followers: {e}")
            return jsonify({'success': False, 'error': 'Failed to get followers'}), 500

    @app.route('/followers/page/<user_id>')
    @require_login
    def followers_page(user_id):
        """Serve the followers page"""
        # Check if user exists
        target_user = User.query.get(user_id)
        if not target_user:
            return "User not found", 404
        
        return render_template('followers.html', 
                             user=current_user,
                             target_user=target_user)

    @app.route('/following/<user_id>')
    @require_login
    def get_following(user_id):
        """API endpoint to get following list"""
        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get following
            following = db.session.query(Follower, User).join(User, Follower.user_id == User.id).filter(
                Follower.follower_id == user_id
            ).all()
            
            following_list = []
            for following_record, following_user in following:
                # Check if current user is following this user
                is_following = Follower.query.filter_by(
                    user_id=following_user.id,
                    follower_id=current_user.id
                ).first() is not None
                
                following_list.append({
                    'id': following_user.id,
                    'username': following_user.username,
                    'first_name': following_user.first_name,
                    'last_name': following_user.last_name,
                    'profile_image_url': following_user.profile_image_url,
                    'is_following': is_following,
                    'followed_at': following_record.created_at.isoformat()
                })
            
            return jsonify({'success': True, 'following': following_list})
                
        except Exception as e:
            print(f"Error getting following: {e}")
            return jsonify({'success': False, 'error': 'Failed to get following'}), 500

    @app.route('/following/page/<user_id>')
    @require_login
    def following_page(user_id):
        """Serve the following page"""
        # Check if user exists
        target_user = User.query.get(user_id)
        if not target_user:
            return "User not found", 404
        
        return render_template('following.html', 
                             user=current_user,
                             target_user=target_user)
    
    @app.route('/api/user/<user_id>/stats')
    @require_login
    def get_user_stats(user_id):
        """API endpoint to get user statistics"""
        try:
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Calculate follower and following counts
            follower_count = Follower.query.filter_by(user_id=user_id).count()
            following_count = Follower.query.filter_by(follower_id=user_id).count()
            
            return jsonify({
                'success': True,
                'follower_count': follower_count,
                'following_count': following_count
            })
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return jsonify({'success': False, 'error': 'Failed to get user stats'}), 500

    @app.route('/api/notifications')
    @require_login
    def get_notifications():
        """API endpoint to get user notifications"""
        try:
            # Get notifications for current user
            notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
                Notification.created_at.desc()
            ).all()
            
            notifications_list = []
            for notification in notifications:
                notifications_list.append({
                    'id': notification.id,
                    'message': notification.message,
                    'type': notification.type,
                    'read_status': notification.read_status,
                    'created_at': notification.created_at.isoformat(),
                    'follow_request_id': notification.follow_request_id,  # Include follow request ID if available
                    'from_user': {
                        'id': notification.from_user.id if notification.from_user else None,
                        'username': notification.from_user.username if notification.from_user else None,
                        'first_name': notification.from_user.first_name if notification.from_user else None,
                        'last_name': notification.from_user.last_name if notification.from_user else None,
                        'profile_image_url': notification.from_user.profile_image_url if notification.from_user else None
                    } if notification.from_user_id else None
                })
            
            return jsonify({'success': True, 'notifications': notifications_list})
                
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return jsonify({'success': False, 'error': 'Failed to get notifications'}), 500

    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @require_login
    def mark_notification_read(notification_id):
        """API endpoint to mark a notification as read"""
        try:
            # Get notification
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=current_user.id
            ).first()
            
            if not notification:
                return jsonify({'success': False, 'error': 'Notification not found'}), 404
            
            # Mark as read
            notification.read_status = True
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Notification marked as read'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error marking notification as read: {e}")
            return jsonify({'success': False, 'error': 'Failed to mark notification as read'}), 500

    @app.route('/api/notifications/read-all', methods=['POST'])
    @require_login
    def mark_all_notifications_read():
        """API endpoint to mark all notifications as read"""
        try:
            # Mark all notifications as read
            Notification.query.filter_by(user_id=current_user.id).update({
                'read_status': True
            })
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'All notifications marked as read'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error marking all notifications as read: {e}")
            return jsonify({'success': False, 'error': 'Failed to mark all notifications as read'}), 500

    @app.route('/api/notifications/unread-count')
    @require_login
    def get_unread_notifications_count():
        """API endpoint to get unread notifications count"""
        try:
            count = Notification.query.filter_by(user_id=current_user.id, read_status=False).count()
            return jsonify({'success': True, 'count': count})
        except Exception as e:
            print(f"Error getting unread notifications count: {e}")
            return jsonify({'success': False, 'error': 'Failed to get unread notifications count'}), 500

    @app.route('/api/chats/unread-count')
    @require_login
    def get_unread_chats_count():
        """API endpoint to get unread chats count"""
        try:
            # In a real implementation, this would query the actual chat messages
            # For now, we'll return 0 as a placeholder
            return jsonify({'success': True, 'count': 0})
        except Exception as e:
            print(f"Error getting unread chats count: {e}")
            return jsonify({'success': False, 'error': 'Failed to get unread chats count'}), 500

    @app.route('/api/system-announcement', methods=['POST'])
    @require_login
    def create_system_announcement():
        """API endpoint to create a system announcement (admin only)"""
        try:
            # In a real implementation, this would check if the user is an admin
            # For now, we'll allow anyone to create announcements for testing
            
            data = request.get_json()
            message = data.get('message', '').strip()
            title = data.get('title', 'System Update').strip()
            
            if not message:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            
            # Get all users
            users = User.query.all()
            
            # Create notification for each user
            for user in users:
                notification = Notification()
                notification.user_id = user.id
                notification.message = f"{title}: {message}"
                notification.type = 'system_update'
                # No from_user_id for system announcements
                db.session.add(notification)
                
                # Emit notification to user
                socketio.emit('new_notification', {
                    'user_id': user.id,
                    'message': f"{title}: {message}",
                    'type': 'system_update'
                }, room=f'user_{user.id}')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'System announcement created'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error creating system announcement: {e}")
            return jsonify({'success': False, 'error': 'Failed to create system announcement'}), 500

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
    
    @socketio.on('join')
    def handle_join_room(data):
        """Handle user joining a specific room"""
        if current_user.is_authenticated and 'room' in data:
            join_room(data['room'])
            print(f'User {current_user.username} joined room {data["room"]}')

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

    # AI Feature API Routes
    @app.route('/api/review', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_review_code():
        """API endpoint for code review"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            language = data.get('language', 'python')
            profession = data.get('profession', 'student')
            
            if not code:
                return jsonify({'success': False, 'result': 'No code provided'}), 400
            
            # Import the AI helper
            from gemini_helper import review_code
            result = review_code(code, language, profession)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in code review: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/explain', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_explain_code():
        """API endpoint for code explanation"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            language = data.get('language', 'python')
            profession = data.get('profession', 'student')
            
            if not code:
                return jsonify({'success': False, 'result': 'No code provided'}), 400
            
            # Import the AI helper
            from gemini_helper import explain_code
            result = explain_code(code, language, profession)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in code explanation: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/compile', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_compile_code():
        """API endpoint for code compilation check"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            language = data.get('language', 'python')
            profession = data.get('profession', 'student')
            
            if not code:
                return jsonify({'success': False, 'result': 'No code provided'}), 400
            
            # Import the AI helper
            from gemini_helper import compile_check
            result = compile_check(code, language, profession)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in code compilation: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/execute', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_execute_code():
        """API endpoint for actual code execution"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            language = data.get('language', 'python').lower()
            input_data = data.get('input', '')
            
            if not code:
                return jsonify({'success': False, 'result': 'No code provided', 'type': 'error'}), 400
            
            # Create a temporary directory for execution
            temp_dir = tempfile.mkdtemp()
            
            try:
                if language in ['python', 'py']:
                    # Write Python code to a temporary file
                    file_path = os.path.join(temp_dir, 'program.py')
                    with open(file_path, 'w') as f:
                        f.write(code)
                    
                    # Execute the Python code
                    try:
                        # For interactive programs, we need to handle input/output differently
                        process = subprocess.Popen(
                            ['python', file_path],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                        
                        # Store process info
                        import uuid
                        execution_id = str(uuid.uuid4())
                        running_processes[execution_id] = {
                            'process': process,
                            'temp_dir': temp_dir,
                            'output_buffer': '',
                            'input_queue': queue.Queue()
                        }
                        
                        # If initial input provided, send it
                        if input_data:
                            process.stdin.write(input_data + '\n')
                            process.stdin.flush()
                        
                        # Wait a short time to see if program finishes immediately
                        time.sleep(0.1)
                        
                        # Check if process has finished
                        if process.poll() is not None:
                            # Process finished
                            stdout, stderr = process.communicate()
                            output = stdout
                            error = stderr
                            
                            # Clean up
                            if execution_id in running_processes:
                                del running_processes[execution_id]
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            
                            if process.returncode == 0:
                                return jsonify({
                                    'success': True, 
                                    'result': output, 
                                    'type': 'output',
                                    'execution_id': execution_id
                                })
                            else:
                                return jsonify({
                                    'success': False, 
                                    'result': error, 
                                    'type': 'error',
                                    'execution_id': execution_id
                                })
                        else:
                            # Process is still running, likely waiting for input
                            # Read any initial output
                            initial_output = ''
                            while True:
                                line = process.stdout.readline()
                                if line:
                                    initial_output += line
                                else:
                                    break
                            
                            return jsonify({
                                'success': True,
                                'result': initial_output,
                                'type': 'output',
                                'execution_id': execution_id,
                                'waiting_for_input': True
                            })
                            
                    except subprocess.TimeoutExpired:
                        return jsonify({'success': False, 'result': 'Execution timed out', 'type': 'error'})
                    except Exception as e:
                        return jsonify({'success': False, 'result': f'Execution error: {str(e)}', 'type': 'error'})
                
                elif language in ['javascript', 'js']:
                    # Write JavaScript code to a temporary file
                    file_path = os.path.join(temp_dir, 'program.js')
                    with open(file_path, 'w') as f:
                        f.write(code)
                    
                    # Execute the JavaScript code
                    try:
                        result = subprocess.run(['node', file_path], 
                                              input=input_data, 
                                              capture_output=True, 
                                              text=True, 
                                              timeout=30)
                        output = result.stdout
                        error = result.stderr
                        
                        if result.returncode == 0:
                            return jsonify({'success': True, 'result': output, 'type': 'output'})
                        else:
                            return jsonify({'success': False, 'result': error, 'type': 'error'})
                    except subprocess.TimeoutExpired:
                        return jsonify({'success': False, 'result': 'Execution timed out', 'type': 'error'})
                    except Exception as e:
                        return jsonify({'success': False, 'result': f'Execution error: {str(e)}', 'type': 'error'})
                
                elif language in ['html']:
                    # For HTML, return the code as is for rendering
                    return jsonify({'success': True, 'result': code, 'type': 'html'})
                
                elif language in ['java']:
                    # For Java, we'll simulate the output since actual compilation would be complex
                    from gemini_helper import compile_check
                    result = compile_check(code, language, 'student')
                    return jsonify({'success': True, 'result': result, 'type': 'simulation'})
                
                elif language in ['c', 'cpp', 'c++']:
                    # For C/C++, check if compiler is available and compile/execute with interactive input support
                    try:
                        # Check if gcc/g++ is available
                        compiler_available = False
                        compiler_name = 'gcc' if language in ['c'] else 'g++'
                        
                        # Check for gcc/g++
                        if shutil.which(compiler_name):
                            compiler_available = True
                        # Check for clang/clang++
                        elif shutil.which('clang' if language in ['c'] else 'clang++'):
                            compiler_name = 'clang' if language in ['c'] else 'clang++'
                            compiler_available = True
                        # Check for Visual Studio compiler (Windows)
                        elif shutil.which('cl'):
                            compiler_name = 'cl'
                            compiler_available = True
                        
                        if not compiler_available:
                            # No compiler available, use AI simulation with proper message
                            from gemini_helper import compile_check
                            result = compile_check(code, language, 'student')
                            return jsonify({'success': True, 'result': result + '\n\nNote: No C/C++ compiler found on this system. Please install a compiler (GCC, Clang, or Visual Studio) to run C/C++ programs with interactive input.', 'type': 'simulation'})
                        
                        # Write C code to a temporary file
                        if language in ['c']:
                            file_path = os.path.join(temp_dir, 'program.c')
                        else:
                            file_path = os.path.join(temp_dir, 'program.cpp')
                        
                        with open(file_path, 'w') as f:
                            f.write(code)
                        
                        # Compile the C/C++ code
                        if compiler_name in ['gcc', 'clang']:
                            compile_process = subprocess.Popen([compiler_name, file_path, '-o', os.path.join(temp_dir, 'program')], 
                                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        elif compiler_name == 'g++':
                            compile_process = subprocess.Popen([compiler_name, file_path, '-o', os.path.join(temp_dir, 'program')], 
                                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        elif compiler_name == 'clang++':
                            compile_process = subprocess.Popen([compiler_name, file_path, '-o', os.path.join(temp_dir, 'program')], 
                                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        elif compiler_name == 'cl':
                            # Visual Studio compiler
                            compile_process = subprocess.Popen([compiler_name, '/Fe:' + os.path.join(temp_dir, 'program.exe'), file_path], 
                                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
                        # Wait for compilation to complete
                        compile_stdout, compile_stderr = compile_process.communicate(timeout=30)
                        
                        # Check if compilation was successful
                        if compile_process.returncode != 0:
                            error = compile_stderr
                            # Clean up temp directory
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            return jsonify({'success': False, 'result': f'Compilation error:\n{error}', 'type': 'error'})
                        
                        # Execute the compiled program with interactive input support
                        if compiler_name == 'cl':
                            executable_path = os.path.join(temp_dir, 'program.exe')
                        else:
                            executable_path = os.path.join(temp_dir, 'program')
                        
                        process = subprocess.Popen(
                            [executable_path],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                        
                        # Store process info
                        import uuid
                        execution_id = str(uuid.uuid4())
                        running_processes[execution_id] = {
                            'process': process,
                            'temp_dir': temp_dir,
                            'output_buffer': '',
                            'input_queue': queue.Queue()
                        }
                        
                        # If initial input provided, send it
                        if input_data:
                            process.stdin.write(input_data + '\n')
                            process.stdin.flush()
                        
                        # Wait a short time to see if program finishes immediately
                        time.sleep(0.1)
                        
                        # Check if process has finished
                        if process.poll() is not None:
                            # Process finished
                            stdout, stderr = process.communicate()
                            output = stdout
                            error = stderr
                            
                            # Clean up
                            if execution_id in running_processes:
                                del running_processes[execution_id]
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            
                            if process.returncode == 0:
                                return jsonify({
                                    'success': True, 
                                    'result': output, 
                                    'type': 'output',
                                    'execution_id': execution_id
                                })
                            else:
                                return jsonify({
                                    'success': False, 
                                    'result': error, 
                                    'type': 'error',
                                    'execution_id': execution_id
                                })
                        else:
                            # Process is still running, likely waiting for input
                            # Read any initial output
                            initial_output = ''
                            while True:
                                line = process.stdout.readline()
                                if line:
                                    initial_output += line
                                else:
                                    break
                            
                            return jsonify({
                                'success': True,
                                'result': initial_output,
                                'type': 'output',
                                'execution_id': execution_id,
                                'waiting_for_input': True
                            })
                            
                    except subprocess.TimeoutExpired:
                        # Clean up temp directory
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        return jsonify({'success': False, 'result': 'Compilation or execution timed out', 'type': 'error'})
                    except Exception as e:
                        # Clean up temp directory
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        return jsonify({'success': False, 'result': f'Compilation or execution error: {str(e)}', 'type': 'error'})
                
                elif language in ['php']:
                    # For PHP, we'll simulate the output since actual execution would require a web server
                    from gemini_helper import compile_check
                    result = compile_check(code, language, 'student')
                    return jsonify({'success': True, 'result': result, 'type': 'simulation'})
                
                else:
                    # For unsupported languages, use AI simulation
                    from gemini_helper import compile_check
                    result = compile_check(code, language, 'student')
                    return jsonify({'success': True, 'result': result, 'type': 'simulation'})
            
            except Exception as e:
                # Clean up temp directory on error
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise e
                
        except Exception as e:
            print(f"Error in code execution: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}', 'type': 'error'}), 500

    @app.route('/api/send-input', methods=['POST'])
    def api_send_input():
        """API endpoint for sending input to a running program"""
        try:
            data = request.get_json()
            execution_id = data.get('execution_id')
            user_input = data.get('input', '')
            
            if not execution_id:
                return jsonify({'success': False, 'result': 'No execution ID provided'}), 400
            
            if not user_input:
                return jsonify({'success': False, 'result': 'No input provided'}), 400
            
            # Check if execution exists
            if execution_id not in running_processes:
                return jsonify({'success': False, 'result': 'Program not found or already finished'}), 404
            
            process_info = running_processes[execution_id]
            process = process_info['process']
            
            try:
                # Send input to the process
                process.stdin.write(user_input + '\n')
                process.stdin.flush()
                
                # Wait a short time for output
                time.sleep(0.2)
                
                # Read output
                output = ''
                while True:
                    line = process.stdout.readline()
                    if line:
                        output += line
                    else:
                        break
                
                # Check if process has finished
                if process.poll() is not None:
                    # Process finished, clean up
                    stdout, stderr = process.communicate()
                    final_output = output + stdout
                    error_output = stderr
                    
                    # Clean up
                    if execution_id in running_processes:
                        shutil.rmtree(running_processes[execution_id]['temp_dir'], ignore_errors=True)
                        del running_processes[execution_id]
                    
                    if process.returncode == 0:
                        return jsonify({
                            'success': True,
                            'output': final_output,
                            'waiting_for_input': False
                        })
                    else:
                        return jsonify({
                            'success': True,
                            'output': error_output,
                            'waiting_for_input': False
                        })
                else:
                    # Process is still running
                    return jsonify({
                        'success': True,
                        'output': output,
                        'waiting_for_input': True
                    })
                    
            except Exception as e:
                # Clean up on error
                if execution_id in running_processes:
                    shutil.rmtree(running_processes[execution_id]['temp_dir'], ignore_errors=True)
                    del running_processes[execution_id]
                return jsonify({'success': False, 'result': f'Error sending input: {str(e)}'}), 500
                
        except Exception as e:
            print(f"Error in sending input: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/question', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_answer_question():
        """API endpoint for answering questions about code"""
        try:
            data = request.get_json()
            question = data.get('question', '')
            code = data.get('code', '')
            language = data.get('language', 'python')
            
            if not question:
                return jsonify({'success': False, 'result': 'No question provided'}), 400
            
            # Import the AI helper
            from gemini_helper import answer_question
            result = answer_question(question, code, language)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in answering question: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/detect-language', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_detect_language():
        """API endpoint for detecting code language"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            
            if not code:
                return jsonify({'success': False, 'language': 'python'}), 400
            
            # Import the AI helper
            from gemini_helper import detect_language
            language = detect_language(code)
            
            return jsonify({'success': True, 'language': language})
        except Exception as e:
            print(f"Error in language detection: {e}")
            return jsonify({'success': False, 'language': 'python'}), 500

    @app.route('/api/test-gemini', methods=['GET'])
    # @require_login  # Temporarily disable for testing
    def api_test_gemini():
        """API endpoint for testing Gemini connection"""
        try:
            # Import the AI helper
            from gemini_helper import test_gemini_connection
            result = test_gemini_connection()
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in Gemini test: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/translate', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_translate_code():
        """API endpoint for translating code"""
        try:
            data = request.get_json()
            code = data.get('code', '')
            from_lang = data.get('from_lang', 'python')
            to_lang = data.get('to_lang', 'javascript')
            
            if not code:
                return jsonify({'success': False, 'result': 'No code provided'}), 400
            
            # Import the AI helper
            from gemini_helper import translate_code
            result = translate_code(code, from_lang, to_lang)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in code translation: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/dictionary', methods=['POST'])
    # @require_login  # Temporarily disable for testing
    def api_dictionary():
        """API endpoint for dictionary content"""
        try:
            data = request.get_json()
            term = data.get('term', '')
            language = data.get('language', 'python')
            
            if not term:
                return jsonify({'success': False, 'result': 'No term provided'}), 400
            
            # Import the AI helper
            from gemini_helper import get_dictionary_content
            result = get_dictionary_content(language, term)
            
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            print(f"Error in dictionary lookup: {e}")
            return jsonify({'success': False, 'result': f'Error: {str(e)}'}), 500

    @app.route('/api/post/<int:post_id>/like', methods=['POST'])
    @require_login
    def like_post(post_id):
        """API endpoint to like a post"""
        try:
            # Get the post
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'success': False, 'error': 'Post not found'}), 404
            
            # Check if user has already liked this post
            existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
            if existing_like:
                # Unlike the post
                db.session.delete(existing_like)
                db.session.commit()
                
                # Create notification for post owner (unlike)
                if post.user_id != current_user.id:
                    # Check if there's an existing like notification and remove it
                    existing_notification = Notification.query.filter_by(
                        user_id=post.user_id,
                        from_user_id=current_user.id,
                        type='like',
                        message=f"{current_user.full_name} liked your post"
                    ).first()
                    if existing_notification:
                        db.session.delete(existing_notification)
                        db.session.commit()
                
                return jsonify({'success': True, 'message': 'Post unliked', 'liked': False})
            
            # Like the post
            like = PostLike()
            like.post_id = post_id
            like.user_id = current_user.id
            db.session.add(like)
            
            # Create notification for post owner (like)
            if post.user_id != current_user.id:
                notification = Notification()
                notification.user_id = post.user_id
                notification.message = f"{current_user.full_name} liked your post"
                notification.type = 'like'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                # Emit notification to post owner with post ID
                socketio.emit('new_notification', {
                    'user_id': post.user_id,
                    'message': f"{current_user.full_name} liked your post",
                    'type': 'like',
                    'post_id': post_id
                }, room=f'user_{post.user_id}')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Post liked', 'liked': True})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error liking post: {e}")
            return jsonify({'success': False, 'error': 'Failed to like post'}), 500

    @app.route('/api/post/<int:post_id>/comment', methods=['POST'])
    @require_login
    def comment_on_post(post_id):
        """API endpoint to comment on a post"""
        try:
            data = request.get_json()
            content = data.get('content', '').strip()
            
            if not content:
                return jsonify({'success': False, 'error': 'Comment content is required'}), 400
            
            # Get the post
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'success': False, 'error': 'Post not found'}), 404
            
            # Create comment
            comment = Comment()
            comment.post_id = post_id
            comment.user_id = current_user.id
            comment.content = content
            db.session.add(comment)
            
            # Create notification for post owner (comment)
            if post.user_id != current_user.id:
                notification = Notification()
                notification.user_id = post.user_id
                notification.message = f"{current_user.full_name} commented on your post: '{content[:50]}{'...' if len(content) > 50 else ''}"
                notification.type = 'comment'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                # Emit notification to post owner with post ID
                socketio.emit('new_notification', {
                    'user_id': post.user_id,
                    'message': f"{current_user.full_name} commented on your post: '{content[:50]}{'...' if len(content) > 50 else ''}",
                    'type': 'comment',
                    'post_id': post_id
                }, room=f'user_{post.user_id}')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Comment added'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error commenting on post: {e}")
            return jsonify({'success': False, 'error': 'Failed to comment on post'}), 500

    @app.route('/api/comment/<int:comment_id>/reply', methods=['POST'])
    @require_login
    def reply_to_comment(comment_id):
        """API endpoint to reply to a comment"""
        try:
            data = request.get_json()
            content = data.get('content', '').strip()
            
            if not content:
                return jsonify({'success': False, 'error': 'Reply content is required'}), 400
            
            # Get the comment
            comment = Comment.query.get(comment_id)
            if not comment:
                return jsonify({'success': False, 'error': 'Comment not found'}), 404
            
            # Get the post
            post = Post.query.get(comment.post_id)
            if not post:
                return jsonify({'success': False, 'error': 'Post not found'}), 404
            
            # Create reply (as a new comment)
            reply = Comment()
            reply.post_id = comment.post_id
            reply.user_id = current_user.id
            reply.content = content
            db.session.add(reply)
            
            # Create notification for comment owner (reply)
            if comment.user_id != current_user.id:
                notification = Notification()
                notification.user_id = comment.user_id
                notification.message = f"{current_user.full_name} replied to your comment: '{content[:50]}{'...' if len(content) > 50 else ''}"
                notification.type = 'comment_reply'
                notification.from_user_id = current_user.id
                db.session.add(notification)
                
                # Emit notification to comment owner with post ID
                socketio.emit('new_notification', {
                    'user_id': comment.user_id,
                    'message': f"{current_user.full_name} replied to your comment: '{content[:50]}{'...' if len(content) > 50 else ''}",
                    'type': 'comment_reply',
                    'post_id': comment.post_id
                }, room=f'user_{comment.user_id}')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Reply added'})
                
        except Exception as e:
            db.session.rollback()
            print(f"Error replying to comment: {e}")
            return jsonify({'success': False, 'error': 'Failed to reply to comment'}), 500
