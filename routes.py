from flask import render_template, request, jsonify, redirect, url_for
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
            else:
                # Create new follow request
                new_request = FollowRequest()
                new_request.from_user_id = current_user.id
                new_request.to_user_id = to_user_id
                new_request.status = 'pending'
                db.session.add(new_request)
                db.session.commit()
            
            return jsonify({'success': True, 'message': 'Follow request sent'})
        except Exception as e:
            db.session.rollback()
            print(f"Error sending follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to send follow request'}), 500

    @app.route('/api/search-users-chat', methods=['GET'])
    @require_login
    def api_search_users_chat():
        """API endpoint to search users for chat"""
        try:
            query = request.args.get('q', '').strip()
            
            if not query:
                # Return all followed users if no query
                return api_get_friends()
            
            # Search for users by username, first name, or last name
            users = User.query.filter(
                (User.username.ilike(f'%{query}%')) |
                (User.first_name.ilike(f'%{query}%')) |
                (User.last_name.ilike(f'%{query}%'))
            ).limit(20).all()
            
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.full_name,
                    'username': user.username,
                    'image': user.profile_image_url
                })
            
            return jsonify(user_list)
        except Exception as e:
            print(f"Error searching users: {e}")
            return jsonify([]), 500

    @app.route('/api/friends')
    @require_login
    def api_get_friends():
        """API endpoint to get user's friends and followed users"""
        try:
            # Get all users that the current user is following (using Follower model)
            followed_users = db.session.query(User).join(
                Follower, 
                (Follower.user_id == User.id) & (Follower.follower_id == current_user.id)
            ).all()
            
            # Also get users who are following the current user (for mutual follows)
            followers = db.session.query(User).join(
                Follower,
                (Follower.follower_id == User.id) & (Follower.user_id == current_user.id)
            ).all()
            
            # Combine both lists and remove duplicates
            all_users = {}
            for user in followed_users:
                all_users[user.id] = user
                
            for user in followers:
                all_users[user.id] = user
            
            # Convert to list format
            user_list = []
            for user in all_users.values():
                user_list.append({
                    'id': user.id,
                    'name': user.full_name,
                    'username': user.username,
                    'image': user.profile_image_url
                })
            
            return jsonify(user_list)
        except Exception as e:
            print(f"Error getting friends: {e}")
            return jsonify([]), 500

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

    @app.route('/api/messages/<user_id>')
    @require_login
    def api_get_messages(user_id):
        """API endpoint to get messages with a specific user"""
        try:
            # Get messages between current user and specified user
            messages = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
                ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.asc()).all()
            
            message_list = []
            for message in messages:
                # Get sender info
                sender = User.query.get(message.sender_id)
                message_list.append({
                    'id': message.id,
                    'sender_id': message.sender_id,
                    'receiver_id': message.receiver_id,
                    'content': message.content,
                    'code_snippet': message.code_snippet,
                    'file_attachment': message.file_attachment,
                    'file_type': message.file_type,
                    'created_at': message.created_at.isoformat(),
                    'sender_image': sender.profile_image_url if sender else None
                })
            
            return jsonify(message_list)
        except Exception as e:
            print(f"Error getting messages: {e}")
            return jsonify([]), 500

    @app.route('/api/send-message', methods=['POST'])
    @require_login
    def api_send_message():
        """API endpoint to send a message with optional file attachment"""
        try:
            # Handle both JSON and form data
            if request.is_json:
                data = request.get_json()
                receiver_id = data.get('receiver_id')
                content = data.get('content', '').strip()
                code_snippet = data.get('code_snippet')
                file_attachment = data.get('file_attachment')
                file_type = data.get('file_type')
            else:
                receiver_id = request.form.get('receiver_id')
                content = request.form.get('content', '').strip()
                code_snippet = request.form.get('code_snippet')
                file_attachment = request.form.get('file_attachment')
                file_type = request.form.get('file_type')
            
            if not receiver_id:
                return jsonify({'success': False, 'error': 'Receiver is required'}), 400
            
            # Check if receiver exists
            receiver = User.query.get(receiver_id)
            if not receiver:
                return jsonify({'success': False, 'error': 'Receiver not found'}), 404
            
            # Check if user is following the receiver or vice versa
            is_following = Follower.query.filter_by(
                user_id=receiver_id, 
                follower_id=current_user.id
            ).first() is not None
            
            is_followed_by = Follower.query.filter_by(
                user_id=current_user.id, 
                follower_id=receiver_id
            ).first() is not None
            
            # Users can chat if they follow each other (mutual follow) or if one follows the other
            if not (is_following or is_followed_by):
                return jsonify({'success': False, 'error': 'You need to follow this user to chat'}), 403
            
            # Create new message
            message = Message()
            message.sender_id = current_user.id
            message.receiver_id = receiver_id
            message.content = content if content else ''
            message.code_snippet = code_snippet
            message.file_attachment = file_attachment
            message.file_type = file_type
            
            db.session.add(message)
            db.session.commit()
            
            # Prepare message data for Socket.IO
            message_data = {
                'id': message.id,
                'sender_id': current_user.id,
                'receiver_id': receiver_id,
                'content': content,
                'message': content,  # Keep both for compatibility
                'code_snippet': code_snippet,
                'file_attachment': file_attachment,
                'file_type': file_type,
                'timestamp': message.created_at.isoformat(),
                'sender_name': current_user.full_name,
                'sender_image': current_user.profile_image_url
            }
            
            # Emit message to BOTH sender and receiver's chat rooms for instant display
            socketio.emit('receive_message', message_data, room=f'chat_{receiver_id}')
            socketio.emit('receive_message', message_data, room=f'chat_{current_user.id}')
            
            return jsonify({'success': True, 'message_id': message.id})
        except Exception as e:
            db.session.rollback()
            print(f"Error sending message: {e}")
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500

    @app.route('/api/upload-file', methods=['POST'])
    @require_login
    def api_upload_file():
        """API endpoint to upload files for chat"""
        try:
            import uuid
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            if file:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '_' + file.filename
                file_path = os.path.join('static', 'uploads', filename)
                
                # Ensure upload directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save file
                file.save(file_path)
                
                # Determine file type
                file_type = 'other'
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_type = 'image'
                elif file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv')):
                    file_type = 'video'
                elif file.filename.lower().endswith('.pdf'):
                    file_type = 'pdf'
                elif file.filename.lower().endswith(('.doc', '.docx')):
                    file_type = 'document'
                
                return jsonify({
                    'success': True,
                    'file_path': f'/static/uploads/{filename}',
                    'file_type': file_type
                })
            
            return jsonify({'success': False, 'error': 'Failed to upload file'}), 500
        except Exception as e:
            print(f"Error uploading file: {e}")
            return jsonify({'success': False, 'error': 'Failed to upload file'}), 500
