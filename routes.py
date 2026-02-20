from flask import render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
from flask_login import current_user, login_user, logout_user
from flask_socketio import emit, join_room
from database import db
from models import (
    User,
    Friendship,
    FollowRequest,
    Follower,
    Notification,
    Message,    
    CodeHistory,
    Post,
    PostLike,
    Comment,
    PostSave,
    TimeSpent,
    Conversation,
)
from datetime import datetime, date, timedelta
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
import re
import sys

# Global variables to hold app and socketio instances
app = None
socketio = None

# Dictionary to store running processes
running_processes = {}
# Per-session metadata for idle timeout (last_activity from output or input)
running_process_meta = {}

# Global Runner instance
code_runner_instance = None
from code_runner import CodeRunner


def init_app(flask_app, flask_socketio):
    """Initialize the routes with the Flask app and SocketIO instances"""
    global app, socketio, code_runner_instance
    app = flask_app
    socketio = flask_socketio
    code_runner_instance = CodeRunner(socketio)
    register_routes()
    register_socketio_events()

def get_or_create_conversation(user1_id, user2_id):
    """Helper to get or create a conversation between two users"""
    # Sort IDs to ensure consistency
    ids = sorted([user1_id, user2_id])
    u1, u2 = ids[0], ids[1]
    
    conversation = Conversation.query.filter_by(user1_id=u1, user2_id=u2).first()
    if not conversation:
        conversation = Conversation(user1_id=u1, user2_id=u2)
        db.session.add(conversation)
        db.session.commit()
    return conversation

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
        """Search users by username, email, or full name for Explore page."""
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({'users': []})

        # Build case-insensitive search across username, email, first/last name and full name
        like_pattern = f'%{query}%'
        full_name_expr = db.func.concat(
            db.func.coalesce(User.first_name, ''),
            ' ',
            db.func.coalesce(User.last_name, ''),
        )

        users = (
            User.query.filter(
                (User.username.ilike(like_pattern))
                | (User.email.ilike(like_pattern))
                | (User.first_name.ilike(like_pattern))
                | (User.last_name.ilike(like_pattern))
                | (full_name_expr.ilike(like_pattern))
            )
            .limit(20)
            .all()
        )

        user_list = []
        for user in users:
            # Check if current user already follows this user
            is_following = (
                Follower.query.filter_by(
                    user_id=user.id, follower_id=current_user.id
                ).first()
                is not None
            )
            # Check if there's a pending follow request from current user to this user
            pending_request = FollowRequest.query.filter_by(
                from_user_id=current_user.id,
                to_user_id=user.id,
                status='pending'
            ).first()

            if is_following:
                follow_status = 'following'
            elif pending_request:
                follow_status = 'pending'
            else:
                follow_status = 'none'

            user_list.append(
                {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'profile_image_url': user.profile_image_url,
                    'is_following': is_following,
                    'follow_status': follow_status,
                }
            )

        return jsonify({'users': user_list})

    @app.route('/user/<user_id>')
    @require_login
    def user_profile(user_id):
        """Display user profile page"""
        user = User.query.get(user_id)
        if not user:
            return "User not found", 404
        
        # Check if current user is following this user
        is_following = Follower.query.filter_by(
            user_id=user_id,
            follower_id=current_user.id
        ).first() is not None

        # Check if target user is following current user (for follow back functionality)
        is_following_me = Follower.query.filter_by(
            user_id=current_user.id,
            follower_id=user_id
        ).first() is not None

        # Check if there is a pending follow request from current user to target user
        has_pending_request = FollowRequest.query.filter_by(
            from_user_id=current_user.id,
            to_user_id=user_id,
            status='pending'
        ).first() is not None

        # Check if current user is viewing their own profile
        is_current_user = (current_user.id == user_id)
        
        # Calculate post count
        post_count = Post.query.filter_by(user_id=user_id).count()
        posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
        
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
                             has_pending_request=has_pending_request,
                             is_current_user=is_current_user,
                             post_count=post_count,
                             follower_count=follower_count,
                             following_count=following_count,
                             posts=posts)

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

            # Create notification for the target user
            try:
                follow_req = (
                    existing_request if 'existing_request' in locals() and existing_request
                    else new_request
                )
                notif = Notification(
                    user_id=to_user_id,
                    from_user_id=current_user.id,
                    message=f"{current_user.full_name} requested to follow you",
                    type='follow_request',
                    follow_request_id=follow_req.id,
                )
                db.session.add(notif)
                db.session.commit()

                # Emit real-time notification
                socketio.emit(
                    'new_notification',
                    {
                        'id': notif.id,
                        'user_id': notif.user_id,
                        'from_user': {
                            'id': current_user.id,
                            'first_name': current_user.first_name,
                            'last_name': current_user.last_name,
                            'username': current_user.username,
                            'profile_image_url': current_user.profile_image_url,
                        },
                        'message': notif.message,
                        'type': notif.type,
                        'created_at': notif.created_at.isoformat(),
                        'read_status': notif.read_status,
                    },
                    room=f'user_{notif.user_id}',
                )
            except Exception as notify_error:
                db.session.rollback()
                print(f"Error creating follow request notification: {notify_error}")

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

                # Update post likes count
                post.likes = PostLike.query.filter_by(post_id=post_id).count()
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Post unliked', 'liked': False, 'likes': post.likes})

            

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
                notification.post_id = post_id
                db.session.add(notification)

                # Emit notification to post owner with post ID
                socketio.emit(
                    'new_notification',
                    {
                        'user_id': post.user_id,
                        'message': f"{current_user.full_name} liked your post",
                        'type': 'like',
                        'post_id': post_id,
                        'link': f'/post/{post_id}'
                    },
                    room=f'user_{post.user_id}',
                )

            

            db.session.commit()
            
            # Update post likes count after commit to be sure
            post.likes = PostLike.query.filter_by(post_id=post_id).count()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Post liked', 'liked': True, 'likes': post.likes})

                

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
                notification.message = f"{current_user.full_name} commented on your post: '{content[:50]}{'...' if len(content) > 50 else ''}'"
                notification.type = 'comment'
                notification.from_user_id = current_user.id
                notification.post_id = post_id
                db.session.add(notification)

                # Emit notification to post owner with post ID
                socketio.emit(
                    'new_notification',
                    {
                        'user_id': post.user_id,
                        'message': f"{current_user.full_name} commented on your post: '{content[:50]}{'...' if len(content) > 50 else ''}'",
                        'type': 'comment',
                        'post_id': post_id,
                        'link': f'/post/{post_id}'
                    },
                    room=f'user_{post.user_id}',
                )

            

            db.session.commit()
            
            # Get updated comment count
            comments_count = Comment.query.filter_by(post_id=post_id).count()
            
            return jsonify({'success': True, 'message': 'Comment added', 'comments_count': comments_count})

                

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



    @app.route('/api/chat/conversations')
    @require_login
    def api_get_conversations():
        """Get all conversations for the current user with latest message and unread count"""
        try:
            # Get all conversations where the user is a participant
            conversations = Conversation.query.filter(
                (Conversation.user1_id == current_user.id) | 
                (Conversation.user2_id == current_user.id)
            ).order_by(Conversation.updated_at.desc()).all()
            
            result = []
            for conv in conversations:
                other_user_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
                other_user = User.query.get(other_user_id)
                
                if not other_user:
                    continue
                
                # Get latest message
                latest_msg = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.desc()).first()
                
                # Get unread count
                unread_count = Message.query.filter_by(
                    conversation_id=conv.id, 
                    receiver_id=current_user.id, 
                    is_read=False
                ).count()
                
                result.append({
                    'id': conv.id,
                    'other_user': {
                        'id': other_user.id,
                        'name': other_user.full_name,
                        'username': other_user.username,
                        'image': other_user.profile_image_url,
                        'is_online': other_user.is_online,
                        'last_seen': other_user.last_seen.isoformat() if other_user.last_seen else None
                    },
                    'last_message': {
                        'content': latest_msg.content if latest_msg else '',
                        'type': latest_msg.message_type if latest_msg else 'text',
                        'timestamp': latest_msg.created_at.isoformat() if latest_msg else None
                    },
                    'unread_count': unread_count,
                    'updated_at': conv.updated_at.isoformat()
                })
            
            return jsonify(result)
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return jsonify([]), 500

    @app.route('/api/messages/<user_id>')
    @require_login
    def api_get_messages(user_id):
        """API endpoint to get messages with a specific user"""
        try:
            conv = get_or_create_conversation(current_user.id, user_id)
            
            # Mark messages as read
            Message.query.filter_by(
                conversation_id=conv.id, 
                receiver_id=current_user.id, 
                is_read=False
            ).update({'is_read': True})
            db.session.commit()
            
            # Emit unread count update for the user
            emit_unread_count(current_user.id)
            
            messages = Message.query.filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
            
            message_list = []
            for message in messages:
                # Use cached sender info if possible
                sender = User.query.get(message.sender_id)
                message_list.append({
                    'id': message.id,
                    'sender_id': message.sender_id,
                    'receiver_id': message.receiver_id,
                    'content': message.content,
                    'message_type': message.message_type,
                    'code_snippet': message.code_snippet,
                    'file_attachment': message.file_attachment,
                    'file_type': message.file_type,
                    'is_read': message.is_read,
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
            if request.is_json:
                data = request.get_json()
                receiver_id = data.get('receiver_id')
                content = data.get('content', '').strip()
                message_type = data.get('message_type', 'text')
                code_snippet = data.get('code_snippet')
                file_attachment = data.get('file_attachment')
                file_type = data.get('file_type')
            else:
                receiver_id = request.form.get('receiver_id')
                content = request.form.get('content', '').strip()
                message_type = request.form.get('message_type', 'text')
                code_snippet = request.form.get('code_snippet')
                file_attachment = request.form.get('file_attachment')
                file_type = request.form.get('file_type')
            
            if not receiver_id:
                return jsonify({'success': False, 'error': 'Receiver is required'}), 400
            
            receiver = User.query.get(receiver_id)
            if not receiver:
                return jsonify({'success': False, 'error': 'Receiver not found'}), 404

            # Get conversation
            conv = get_or_create_conversation(current_user.id, receiver_id)
            conv.updated_at = datetime.now()
            
            # Create new message
            message = Message()
            message.conversation_id = conv.id
            message.sender_id = current_user.id
            message.receiver_id = receiver_id
            message.content = content
            message.message_type = message_type
            message.code_snippet = code_snippet
            message.file_attachment = file_attachment
            message.file_type = file_type
            message.is_read = False
            
            db.session.add(message)
            db.session.commit()
            
            # Prepare message data for Socket.IO
            message_data = {
                'id': message.id,
                'conversation_id': conv.id,
                'sender_id': current_user.id,
                'receiver_id': receiver_id,
                'content': content,
                'message': content, 
                'message_type': message_type,
                'code_snippet': code_snippet,
                'file_attachment': file_attachment,
                'file_type': file_type,
                'timestamp': message.created_at.isoformat(),
                'created_at': message.created_at.isoformat(),
                'sender_name': current_user.full_name,
                'sender_image': current_user.profile_image_url
            }
            
            # Emit to both sender and receiver rooms
            socketio.emit('new_message', message_data, room=f'user_{receiver_id}')
            socketio.emit('new_message', message_data, room=f'user_{current_user.id}')
            
            # Sync unread counts
            emit_unread_count(receiver_id)
            
            return jsonify({'success': True, 'message_id': message.id, 'conversation_id': conv.id})
        except Exception as e:
            db.session.rollback()
            print(f"Error sending message: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    def emit_unread_count(user_id):
        """Helper to emit unread count update for a user"""
        try:
            total_unread = Message.query.filter_by(
                receiver_id=user_id,
                is_read=False
            ).count()
            # For chat interface unread counts
            socketio.emit('unread_count_update', {
                'unread_count': total_unread
            }, room=f'user_{user_id}')
            # For general navbar badge update
            socketio.emit('unread_badge_update', {
                'count': total_unread
            }, room=f'user_{user_id}')
        except Exception as e:
            print(f"Error emitting unread count: {e}")



    @app.route('/api/upload-file', methods=['POST'])
    @require_login
    def api_upload_file():
        """Final fix for file uploads using absolute paths and secure filenames"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file segment found'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Absolute directory management
            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(base_dir, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Secure filename with unique prefix
            original_name = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{original_name}"
            save_path = os.path.join(upload_dir, unique_filename)
            
            file.save(save_path)
            
            # File type detection
            ext = original_name.lower()
            if ext.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_type = 'image'
            elif ext.endswith(('.mp4', '.webm', '.mov')):
                file_type = 'video'
            elif ext.endswith('.pdf'):
                file_type = 'pdf'
            else:
                file_type = 'file'
            
            return jsonify({
                'success': True,
                'file_path': f'/static/uploads/{unique_filename}',
                'file_type': file_type
            })
        except Exception as e:
            print(f"CRITICAL UPLOAD ERROR: {e}")
            return jsonify({'success': False, 'error': f"Server error: {str(e)}"}), 500

    @app.route('/api/user-status/<user_id>')
    @require_login
    def api_user_status(user_id):
        """API endpoint to get user's online status"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Return UTC time with 'Z' suffix so client handles timezone conversion
            last_seen_iso = None
            if user.last_seen:
                # Ensure it's treated as UTC
                last_seen_iso = user.last_seen.isoformat()
                if not last_seen_iso.endswith('Z') and not '+' in last_seen_iso:
                    last_seen_iso += 'Z'
            
            print(f"API User Status for {user.id}: online={user.is_online}, last_seen={last_seen_iso}")

            return jsonify({
                'success': True,
                'is_online': user.is_online,
                'last_seen': last_seen_iso,
                'last_seen_formatted': None # Client handles formatting
            })
        except Exception as e:
            print(f"Error getting user status: {e}")
            return jsonify({'success': False, 'error': 'Failed to get user status'}), 500

    # ---------------------------------------------------------
    # AI Features & Compiler Routes
    # ---------------------------------------------------------

    @app.route('/api/test-gemini', methods=['GET'])
    @require_login
    def api_test_gemini():
        """Test the Gemini AI connection"""
        from ai_helper import test_ai_connection
        result = test_ai_connection()
        return jsonify({'success': True, 'result': result})

    @app.route('/api/dictionary', methods=['POST'])
    @require_login
    def api_dictionary():
        """Generate code snippet from dictionary search"""
        try:
            data = request.get_json()
            # Frontend sends 'term', backend was expecting 'prompt'
            prompt = data.get('term') or data.get('prompt')
            language = data.get('language', 'python')
            
            if not prompt:
                return jsonify({'success': False, 'result': 'Search term is required'}), 400
                
            from ai_models import generate_code
            code = generate_code(prompt, language)
            
            # Frontend expects 'result', backend was returning 'code'
            return jsonify({'success': True, 'result': code})
        except Exception as e:
            print(f"Error in dictionary: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/detect-language', methods=['POST'])
    @require_login
    def api_detect_language():
        """Detect programming language of code"""
        try:
            data = request.get_json()
            code = data.get('code')
            
            if not code:
                return jsonify({'success': False, 'result': 'Code is required'}), 400
                
            from ai_models import detect_language
            language = detect_language(code)
            
            return jsonify({'success': True, 'language': language})
        except Exception as e:
            print(f"Error in detection: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/extract-code-from-image', methods=['POST'])
    @require_login
    def api_extract_code_from_image():
        """Extract code from uploaded image using OCR with smart code detection"""
        try:
            import pytesseract
            from PIL import Image
            import io
            import cv2
            import numpy as np
            from code_detector import is_code, detect_primary_language, calculate_code_score
            
            if 'image' not in request.files:
                return jsonify({'success': False, 'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Read and process image
            image_bytes = file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'success': False, 'error': 'Invalid image format'}), 400
            
            # IMPROVED PREPROCESSING for OCR
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Increase contrast/Denoise
            gray = cv2.threshold(cv2.medianBlur(gray, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Perform OCR on processed image
            extracted_text = pytesseract.image_to_string(gray)
            
            if not extracted_text or not extracted_text.strip():
                return jsonify({
                    'success': False, 
                    'error': 'No text could be extracted from the image. Please use a clearer image.'
                }), 400
            
            extracted_text = extracted_text.strip()
            
            # LOWER THRESHOLD for OCR (0.45) as OCR is often "noisy"
            is_valid_code, confidence = is_code(extracted_text, threshold=0.45)
            
            if not is_valid_code:
                # Log score for debugging
                score, breakdown = calculate_code_score(extracted_text)
                print(f"OCR Detection Fail. Text: {extracted_text[:100]}... Score: {score:.2f}, Breakdown: {breakdown}")
                return jsonify({
                    'success': False,
                    'error': 'Recognizable code was not found in this image. Ensure the code is clear and not blurry.',
                    'confidence': confidence
                }), 400
            
            # Detect language
            language = detect_primary_language(extracted_text)
            
            return jsonify({
                'success': True,
                'code': extracted_text,
                'language': language,
                'confidence': confidence
            })
            
        except ImportError as e:
            print(f"Import error in OCR: {e}")
            return jsonify({
                'success': False, 
                'error': 'OCR dependencies not installed. Please install pytesseract and Pillow.'
            }), 500
        except Exception as e:
            print(f"Error extracting code from image: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/extract-code-from-pdf', methods=['POST'])
    @require_login
    def api_extract_code_from_pdf():
        """Extract code from uploaded PDF with smart code detection"""
        try:
            import pdfplumber
            import io
            from code_detector import is_code, detect_primary_language, calculate_code_score
            
            if 'pdf' not in request.files:
                return jsonify({'success': False, 'error': 'No PDF file provided'}), 400
            
            file = request.files['pdf']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Read and process PDF
            pdf_bytes = file.read()
            
            extracted_text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            
            if not extracted_text or not extracted_text.strip():
                return jsonify({
                    'success': False, 
                    'error': 'No text could be extracted from the PDF'
                }), 400
            
            extracted_text = extracted_text.strip()
            
            # Check if extracted text is code (using 60% threshold)
            is_valid_code, confidence = is_code(extracted_text, threshold=0.6)
            
            if not is_valid_code:
                # Get score for debugging
                score, breakdown = calculate_code_score(extracted_text)
                print(f"Code detection failed for PDF. Score: {score:.2f}, Breakdown: {breakdown}")
                return jsonify({
                    'success': False,
                    'error': 'The PDF does not contain recognizable programming code',
                    'confidence': confidence
                }), 400
            
            # Detect language
            language = detect_primary_language(extracted_text)
            
            return jsonify({
                'success': True,
                'code': extracted_text,
                'language': language,
                'confidence': confidence
            })
            
        except ImportError as e:
            print(f"Import error in PDF processing: {e}")
            return jsonify({
                'success': False, 
                'error': 'PDF processing dependencies not installed. Please install pdfplumber.'
            }), 500
        except Exception as e:
            print(f"Error extracting code from PDF: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/validate-code', methods=['POST'])
    @require_login
    def api_validate_code():
        """Validate if text content is programming code"""
        try:
            from code_detector import is_code, detect_primary_language, calculate_code_score
            
            data = request.get_json()
            code = data.get('code', '')
            threshold = data.get('threshold', 0.6)  # Default 60%
            
            if not code or not code.strip():
                return jsonify({
                    'success': False,
                    'is_code': False,
                    'error': 'No content provided'
                }), 400
            
            is_valid_code, confidence = is_code(code, threshold=threshold)
            score, breakdown = calculate_code_score(code)
            language = detect_primary_language(code) if is_valid_code else 'text'
            
            return jsonify({
                'success': True,
                'is_code': is_valid_code,
                'confidence': confidence,
                'score': score,
                'language': language,
                'breakdown': breakdown
            })
            
        except Exception as e:
            print(f"Error validating code: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/translate', methods=['POST'])
    @require_login
    def api_translate():
        """Translate code between languages"""
        try:
            data = request.get_json()
            code = data.get('code')
            target_lang = data.get('to_lang') or data.get('target_lang')
            source_lang = data.get('from_lang') or data.get('source_lang') # Optional, will auto-detect if None
            
            if not code or not target_lang:
                return jsonify({'success': False, 'result': 'Code and target language are required'}), 400
                
            from ai_models import translate_code
            translated = translate_code(code, target_lang, source_lang)
            
            # Frontend expects 'result', backend was returning 'code'
            return jsonify({'success': True, 'result': translated})
        except Exception as e:
            print(f"Error in translation: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/review', methods=['POST'])
    @require_login
    def api_review():
        """Review code for errors and improvements"""
        try:
            data = request.get_json()
            code = data.get('code')
            language = data.get('language', 'python')
            
            if not code:
                return jsonify({'success': False, 'result': 'Code is required'}), 400
                
            from ai_models import review_code
            review = review_code(code, language)
            
            # Frontend expects 'result', backend was returning 'review'
            return jsonify({'success': True, 'result': review})
        except Exception as e:
            print(f"Error in review: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/explain', methods=['POST'])
    @require_login
    def api_explain():
        """Explain code based on persona"""
        try:
            data = request.get_json()
            code = data.get('code')
            language = data.get('language', 'python')
            role = data.get('role') or data.get('profession', 'student')
            
            if not code:
                return jsonify({'success': False, 'result': 'Code is required'}), 400
                
            from ai_models import explain_code
            explanation = explain_code(code, language, role)
            
            # Frontend expects 'result', backend was returning 'explanation'
            return jsonify({'success': True, 'result': explanation})
        except Exception as e:
            print(f"Error in explanation: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/question', methods=['POST'])
    @require_login
    def api_question():
        """Answer coding questions (AI Agent)"""
        try:
            data = request.get_json()
            question = data.get('question')
            code = data.get('code')
            language = data.get('language', 'python')
            
            if not question:
                return jsonify({'success': False, 'result': 'Question is required'}), 400
                
            from ai_models import ask_question
            answer = ask_question(question, code, language)
            
            # Frontend expects 'result', backend was returning 'answer'
            return jsonify({'success': True, 'result': answer})
        except Exception as e:
            print(f"Error in question: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    @app.route('/api/execute', methods=['POST'])
    @require_login
    def api_execute():
        """Execute code locally or prepare for web view"""
        try:
            data = request.get_json()
            code = data.get('code')
            language = data.get('language', 'python').lower()
            
            if not code:
                return jsonify({'success': False, 'result': 'Code is required'}), 400

            # HTML/JSP fix: if code starts with <!DOCTYPE or <html, render in iframe directly
            s = code.strip()
            if s and (s.upper().startswith('<!DOCTYPE') or s.lower().startswith('<html')):
                os.makedirs('static/temp', exist_ok=True)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir='static/temp') as f:
                    f.write(code)
                    temp_path = f.name
                return jsonify({
                    'success': True,
                    'result': 'Web content ready',
                    'type': 'web',
                    'url': f'/static/temp/{os.path.basename(temp_path)}'
                })

            # Web Languages (HTML, CSS, JS) - Return content for browser/iframe
            if language in ['html', 'css', 'javascript', 'js']:
                # Create a temporary file for the web content
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir='static/temp') as f:
                    if language == 'html':
                        f.write(code)
                    elif language == 'css':
                        f.write(f"<style>{code}</style>")
                    elif language in ['javascript', 'js']:
                        f.write(f"<script>{code}</script>")
                    temp_path = f.name
                
                # Return the relative path for the frontend to open
                relative_path = temp_path.replace(os.sep, '/').split('static/')[-1]
                return jsonify({
                    'success': True,
                    'result': 'Web content ready',
                    'type': 'web',
                    'url': f'/static/temp/{os.path.basename(temp_path)}'
                })

            # Interactive Execution for Standard Languages
            import uuid
            session_id = str(uuid.uuid4())
            
            # Start background thread for execution
            thread = threading.Thread(
                target=run_interactive_process,
                args=(code, language, session_id, current_user.id),
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'type': 'interactive',
                'session_id': session_id,
                'result': 'Interactive session started'
            })

        except Exception as e:
            print(f"Error in execution: {e}")
            return jsonify({'success': False, 'result': str(e)}), 500

    # ---------------------------------------------------------
    # Time Tracking Routes (Strict Implementation)
    # ---------------------------------------------------------

    @app.route('/api/track-time', methods=['POST'])
    @require_login
    def api_track_time():
        """
        Heartbeat endpoint: called every 30s by the frontend ONLY when
        the tab is visible and the user is logged in.
        - Caps at 60 seconds per call to prevent abuse.
        - Updates TimeSpent.total_seconds and .minutes.
        - Maintains current_streak and longest_streak on User.
        """
        try:
            data = request.get_json() or {}
            seconds = int(data.get('seconds', 30))
            # Safety cap: max 60s per heartbeat
            if seconds <= 0:
                seconds = 30
            if seconds > 60:
                seconds = 60

            today = datetime.now().date()

            # --- Update daily time record ---
            record = TimeSpent.query.filter_by(
                user_id=current_user.id, date=today
            ).first()
            if not record:
                record = TimeSpent(
                    user_id=current_user.id, date=today,
                    total_seconds=0, minutes=0
                )
                db.session.add(record)

            record.total_seconds += seconds
            record.minutes = record.total_seconds // 60

            # --- Update user presence ---
            user = current_user._get_current_object()
            user.last_active = datetime.now()
            user.is_online = True

            # --- Update streak (only once per day) ---
            if user.last_streak_date != today:
                yesterday = today - timedelta(days=1)
                if user.last_streak_date == yesterday:
                    user.current_streak = (user.current_streak or 0) + 1
                elif user.last_streak_date is None:
                    user.current_streak = 1
                else:
                    # Streak broken - restart
                    user.current_streak = 1

                user.last_streak_date = today

                if (user.current_streak or 0) > (user.longest_streak or 0):
                    user.longest_streak = user.current_streak

            db.session.commit()

            return jsonify({
                'success': True,
                'today_seconds': record.total_seconds,
                'current_streak': user.current_streak or 0,
                'longest_streak': user.longest_streak or 0
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/time-stats', methods=['GET'])
    @require_login
    def api_time_stats():
        """
        Production-level aggregation logic strictly from total_seconds.
        """
        try:
            now = datetime.now()
            today = now.date()
            
            q = TimeSpent.query.filter_by(user_id=current_user.id)
            
            # Today
            today_total = q.filter(TimeSpent.date == today).with_entities(db.func.sum(TimeSpent.total_seconds)).scalar() or 0
            
            # This Week (Monday to today)
            start_of_week = today - timedelta(days=today.weekday())
            week_total = q.filter(TimeSpent.date >= start_of_week).with_entities(db.func.sum(TimeSpent.total_seconds)).scalar() or 0
            
            # This Month (1st to today)
            start_of_month = today.replace(day=1)
            month_total = q.filter(TimeSpent.date >= start_of_month).with_entities(db.func.sum(TimeSpent.total_seconds)).scalar() or 0
            
            # This Year (Jan 1st to today)
            start_of_year = today.replace(month=1, day=1)
            year_total = q.filter(TimeSpent.date >= start_of_year).with_entities(db.func.sum(TimeSpent.total_seconds)).scalar() or 0

            # Instagram Weekly Bars (Last 7 days: today-6 to today)
            weekly_bars = []
            days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                entry = q.filter(TimeSpent.date == d).first()
                secs = entry.total_seconds if entry else 0
                weekly_bars.append({
                    'label': days_labels[d.weekday()] if d != today else "Today",
                    'seconds': secs,
                    'is_today': d == today,
                    'date': d.isoformat()
                })

            # Daily average of this week
            avg_seconds = week_total / 7
            
            # Streak Logic
            all_active_dates = [r.date for r in q.filter(TimeSpent.total_seconds > 0).order_by(TimeSpent.date.desc()).all()]
            current_streak = 0
            check_date = today
            while check_date in all_active_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
            
            longest_streak = 0
            if all_active_dates:
                sorted_dates = sorted(all_active_dates)
                temp_longest = 0
                temp_curr = 0
                prev_active = None
                for d in sorted_dates:
                    if prev_active and (d - prev_active).days == 1:
                        temp_curr += 1
                    else:
                        temp_curr = 1
                    temp_longest = max(temp_longest, temp_curr)
                    prev_active = d
                longest_streak = temp_longest

            daily_map = {r.date.isoformat(): r.total_seconds for r in q.all()}

            def fmt(ts):
                h = ts // 3600
                m = (ts % 3600) // 60
                return f"{h}h {m}m"

            return jsonify({
                'success': True,
                'stats': {
                    'today_seconds': int(today_total),
                    'today_summary': fmt(today_total),
                    'week_summary': fmt(week_total),
                    'month_summary': fmt(month_total),
                    'year_summary': fmt(year_total),
                    'daily_average': f"{int(avg_seconds // 3600)}h {int((avg_seconds % 3600) // 60)}m",
                    'current_streak': current_streak,
                    'longest_streak': longest_streak
                },
                'weekly_bars': weekly_bars,
                'daily_map': daily_map
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ---------------------------------------------------------
    # End Time Tracking
    # ---------------------------------------------------------
        """
        Run process and stream output via Socket.IO, using unbuffered,
        byte-by-byte streaming so prompts without newlines appear immediately.
        """
        temp_dir = os.path.join(os.getcwd(), 'temp_exec')
        os.makedirs(temp_dir, exist_ok=True)
        
        process = None
        script_path = None
        exe_path = None
        
        try:
            # Setup process based on language
            if language == 'python':
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=temp_dir) as f:
                    f.write(code)
                    script_path = f.name
                # Use the same interpreter that runs the server, unbuffered
                command = [sys.executable, '-u', script_path]
                
            elif language == 'java':
                class_name = "Main"
                match = re.search(r'public\s+class\s+(\w+)', code)
                if match:
                    class_name = match.group(1)
                
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                with open(java_file, 'w') as f:
                    f.write(code)
                script_path = java_file
                
                # Compile with a reasonable timeout
                compile_proc = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if compile_proc.returncode != 0:
                    socketio.emit(
                        'execution_output',
                        {
                            'output': f"Compilation Error:\n{compile_proc.stderr}",
                            'session_id': session_id,
                        },
                        room=f'user_{user_id}',
                    )
                    return
                
                command = ['java', '-cp', temp_dir, class_name]
                exe_path = os.path.join(temp_dir, f"{class_name}.class")
                
            elif language in ['cpp', 'c++']:
                cpp_file = os.path.join(temp_dir, f"prog_{session_id}.cpp")
                exe_file = os.path.join(temp_dir, f"prog_{session_id}.exe")
                with open(cpp_file, 'w') as f:
                    f.write(code)
                script_path = cpp_file
                exe_path = exe_file
                
                # Compile with a reasonable timeout
                compile_proc = subprocess.run(
                    ['g++', cpp_file, '-o', exe_file],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if compile_proc.returncode != 0:
                    socketio.emit(
                        'execution_output',
                        {
                            'output': f"Compilation Error:\n{compile_proc.stderr}",
                            'session_id': session_id,
                        },
                        room=f'user_{user_id}',
                    )
                    return
                
                # Use full absolute path for Windows WinError 2
                exe_path = os.path.abspath(exe_file)
                command = [exe_path]
            
            else:
                socketio.emit(
                    'execution_output',
                    {
                        'output': f"Language {language} not supported",
                        'session_id': session_id,
                    },
                    room=f'user_{user_id}',
                )
                return

            # Environment (ensure Python is unbuffered)
            env = os.environ.copy()
            if language == 'python':
                env['PYTHONUNBUFFERED'] = '1'

            # Start Process – binary mode, OS-level unbuffered pipes
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
                text=False,
                env=env,
            )
            
            # Store process for input handling
            running_processes[session_id] = process
            running_process_meta[session_id] = {'last_activity': time.time()}

            def stream_output(pipe, type_):
                """Byte-wise streaming so prompts without newlines appear instantly."""
                try:
                    while True:
                        ch = pipe.read(1)
                        if not ch:
                            break
                        try:
                            text = ch.decode('utf-8', errors='replace')
                        except Exception:
                            text = '?'
                        if session_id in running_process_meta:
                            running_process_meta[session_id]['last_activity'] = time.time()
                        socketio.emit(
                            'execution_output',
                            {'output': text, 'session_id': session_id, 'type': type_},
                            room=f'user_{user_id}',
                        )
                finally:
                    try:
                        pipe.close()
                    except Exception:
                        pass
            
            stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, 'stdout'))
            stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, 'stderr'))
            stdout_thread.start()
            stderr_thread.start()

            # Idle timeout: only kill when no output AND no input for 2–3 min
            IDLE_TIMEOUT_SECONDS = 150
            while True:
                if process.poll() is not None:
                    break
                now = time.time()
                last_activity = running_process_meta.get(session_id, {}).get('last_activity', now)
                if now - last_activity > IDLE_TIMEOUT_SECONDS:
                    try:
                        process.kill()
                    except Exception:
                        pass
                    socketio.emit(
                        'execution_output',
                        {
                            'output': f"\nExecution idle timed out after {IDLE_TIMEOUT_SECONDS} seconds (no output, no input).\n",
                            'session_id': session_id,
                            'type': 'stderr',
                        },
                        room=f'user_{user_id}',
                    )
                    break
                time.sleep(0.1)
            
            stdout_thread.join()
            stderr_thread.join()
            
            socketio.emit('execution_finished', {'session_id': session_id}, room=f'user_{user_id}')
            
        except Exception as e:
            socketio.emit(
                'execution_output',
                {
                    'output': f"Execution Error: {str(e)}",
                    'session_id': session_id,
                },
                room=f'user_{user_id}',
            )
        finally:
            if session_id in running_processes:
                del running_processes[session_id]
            if session_id in running_process_meta:
                del running_process_meta[session_id]
            # Cleanup files
            try:
                if script_path and os.path.exists(script_path):
                    os.remove(script_path)
                if exe_path and os.path.exists(exe_path):
                    os.remove(exe_path)
            except Exception:
                pass

def register_socketio_events():
    """Register Socket.IO event handlers"""
    
    @socketio.on('connect')
    def on_connect():
        """Handle user connection - strict personal room join"""
        if current_user.is_authenticated:
            room = f"user_{current_user.id}"
            join_room(room)
            current_user.is_online = True
            db.session.commit()
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': True,
                'last_seen': datetime.utcnow().isoformat()
            })
            print(f"Socket Connected: User {current_user.id} joined {room}")

    @socketio.on('disconnect')
    def on_disconnect():
        """Handle user disconnection"""
        if current_user.is_authenticated:
            current_user.is_online = False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': False,
                'last_seen': current_user.last_seen.isoformat()
            })
            print(f"Socket Disconnected: User {current_user.id}")

    @socketio.on('join')
    def on_join(data):
        """Allow manual room joining (for individual chats if needed)"""
        room = data.get('room')
        if room:
            join_room(room)
            print(f"User joined room: {room}")
    
    @socketio.on('chat_window_opened')
    def on_chat_window_opened(data):
        if current_user.is_authenticated:
            current_user.is_online = True
            db.session.commit()
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': True
            })

    @socketio.on('execution_input')
    def handle_execution_input(data):
        """Handle input for interactive execution - accept stdin anytime while process alive"""
        session_id = data.get('session_id')
        user_input = data.get('input')
        if session_id in running_processes:
            process = running_processes[session_id]
            if process.poll() is None and process.stdin:
                try:
                    process.stdin.write((user_input or '') + '\n')
                    process.stdin.flush()
                    if session_id in running_process_meta:
                        running_process_meta[session_id]['last_activity'] = time.time()
                except Exception as e:
                    print(f"Error writing to stdin: {e}")

    # New Code Runner Socket Events
    @socketio.on('run_code_socket')
    def handle_run_code_socket(data):
        print(f"[ROUTES] run_code_socket received, sid={request.sid}")
        join_room(request.sid)
        code = data.get('code')
        language = data.get('language')
        if code_runner_instance:
            code_runner_instance.run_code(request.sid, language, code)
        else:
            print("Error: code_runner_instance is None!")

    @socketio.on('submit_input_socket')
    def handle_submit_input_socket(data):
        print(f"Socket received submit_input_socket: {data}")
        user_input = data.get('input')
        if code_runner_instance:
            code_runner_instance.send_input(request.sid, user_input)
    # ---------------------------------------------------------

    # Code History Routes
    # ---------------------------------------------------------

    @app.route('/api/history/save', methods=['POST'])
    @require_login
    def api_history_save():
        """Save code interaction to history with smart grouping"""
        try:
            data = request.get_json()
            code = data.get('code')
            language = data.get('language')
            action = data.get('action') # e.g., "Compile", "Review"
            result = data.get('result')
            
            if not code or not action:
                return jsonify({'success': False, 'error': 'Code and action required'}), 400

            # Check for existing recent entry for this code
            last_entry = CodeHistory.query.filter_by(user_id=current_user.id).order_by(CodeHistory.created_at.desc()).first()
            
            # If same code (ignoring whitespace) and recent
            if last_entry and last_entry.code.strip() == code.strip():
                # Update existing entry
                if action not in last_entry.action:
                    last_entry.action = f"{last_entry.action}, {action}"
                last_entry.created_at = datetime.now() # Bump timestamp
                last_entry.result = result # Update result to latest
                db.session.commit()
                return jsonify({'success': True, 'message': 'History updated', 'id': last_entry.id})
            
            # Create new entry
            # Generate Title
            title = "Untitled Code"
            lines = code.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                # Remove comments
                first_line = re.sub(r'^[#///*]+', '', first_line).strip()
                if len(first_line) > 30:
                    title = first_line[:27] + "..."
                elif first_line:
                    title = first_line
            
            # Try to find class/function name
            match = re.search(r'(class|def|function|func)\s+(\w+)', code)
            if match:
                title = match.group(2)
            
            new_entry = CodeHistory(
                user_id=current_user.id,
                code=code,
                language=language,
                action=action,
                result=result,
                title=title
            )
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'History saved', 'id': new_entry.id})

        except Exception as e:
            print(f"Error saving history: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/history/list', methods=['GET'])
    @require_login
    def api_history_list():
        """Get user's code history"""
        try:
            history = CodeHistory.query.filter_by(user_id=current_user.id).order_by(CodeHistory.created_at.desc()).limit(50).all()
            
            history_list = []
            for item in history:
                # Format actions for display
                actions = item.action.split(',')
                display_action = item.action
                if len(actions) > 1:
                    display_action = f"{actions[0].strip()} and more..."
                
                history_list.append({
                    'id': item.id,
                    'title': item.title or "Untitled",
                    'code': item.code,
                    'language': item.language,
                    'action': display_action,
                    'full_action': item.action,
                    'date': item.created_at.strftime('%d:%m:%Y (%I:%M%p)'),
                    'result': item.result
                })
            
            return jsonify({'success': True, 'history': history_list})
        except Exception as e:
            print(f"Error listing history: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ---------------------------------------------------------
    # Posts & Explore Routes
    # ---------------------------------------------------------

    @app.route('/api/posts', methods=['GET', 'POST'])
    @require_login
    def api_posts():
        """Create a new post or list current user's posts.

        IMPORTANT: If a language is provided explicitly, we always trust it.
        Auto-detection is only used as a fallback when language is missing
        or explicitly set to 'Other', so manual selection always wins.
        """
        try:
            if request.method == 'POST':
                data = request.get_json() or {}
                code = (data.get('code') or '').strip()
                language = (data.get('language') or '').strip()
                description = (data.get('description') or '').strip()

                if not code:
                    return jsonify({'success': False, 'error': 'Code is required'}), 400

                # If user didn't choose a language at all, try to auto-detect
                if not language:
                    try:
                        from ai_models import detect_language
                        detected = detect_language(code)
                        language = detected or 'text'
                    except Exception as e:
                        print(f"Language auto-detect failed: {e}")
                        language = 'text'

                # Create post
                post = Post(
                    user_id=current_user.id,
                    code=code,
                    language=language,
                    description=description,
                )
                db.session.add(post)
                db.session.commit()

                # Notify followers about new post
                try:
                    followers = Follower.query.filter_by(user_id=current_user.id).all()
                    for f in followers:
                        notif = Notification(
                            user_id=f.follower_id,
                            from_user_id=current_user.id,
                            message=f"{current_user.full_name} created a new post",
                            type='post',
                            post_id=post.id
                        )
                        db.session.add(notif)
                        db.session.flush()
                        # Real-time notification
                        socketio.emit(
                            'new_notification',
                            {
                                'id': notif.id,
                                'user_id': notif.user_id,
                                'from_user': {
                                    'id': current_user.id,
                                    'first_name': current_user.first_name,
                                    'last_name': current_user.last_name,
                                    'username': current_user.username,
                                    'profile_image_url': current_user.profile_image_url,
                                },
                                'message': notif.message,
                                'type': notif.type,
                                'link': f'/post/{post.id}',
                                'created_at': notif.created_at.isoformat(),
                                'read_status': notif.read_status,
                            },
                            room=f'user_{notif.user_id}',
                        )
                    db.session.commit()
                except Exception as e:
                    # Don't fail post creation if notification fan-out has issues
                    db.session.rollback()
                    print(f"Error sending post notifications: {e}")

                return jsonify({'success': True, 'post_id': post.id})

            # GET: list current user's posts
            posts = (
                Post.query.filter_by(user_id=current_user.id)
                .order_by(Post.created_at.desc())
                .all()
            )

            result = []
            for p in posts:
                result.append(
                    {
                        'id': p.id,
                        'user_id': p.user_id,
                        'author_name': p.author.full_name if p.author else 'Unknown',
                        'author_image': (
                            p.author.profile_image_url if p.author else None
                        ),
                        'code': p.code,
                        'language': p.language,
                        'description': p.description or '',
                        'likes': p.likes or 0,
                        'comments_count': len(p.comments or []),
                        'created_at': p.created_at.isoformat(),
                    }
                )

            return jsonify(result)
        except Exception as e:
            db.session.rollback()
            print(f"Error in /api/posts: {e}")
            return jsonify({'success': False, 'error': 'Failed to process posts'}), 500

    @app.route('/api/posts/<int:post_id>/like', methods=['POST'])
    @require_login
    def api_posts_like(post_id):
        """Wrapper for liking a post using the plural URL used in templates."""
        return like_post(post_id)

    @app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
    @require_login
    def api_posts_comment(post_id):
        """Wrapper for commenting on a post using the plural URL."""
        return comment_on_post(post_id)

    @app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
    @require_login
    def api_posts_get_comments(post_id):
        """Return comments for a post in the format expected by templates."""
        try:
            post = Post.query.get(post_id)
            if not post:
                return jsonify([])

            result = []
            for c in post.comments:
                author = c.user
                result.append(
                    {
                        'id': c.id,
                        'user_id': c.user_id,
                        'author_name': author.full_name if author else 'User',
                        'user_image': (
                            author.profile_image_url if author else None
                        ),
                        'content': c.content,
                        'created_at': c.created_at.isoformat(),
                    }
                )

            return jsonify(result)
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            return jsonify([]), 500

    @app.route('/api/posts/<int:post_id>/save', methods=['POST'])
    @require_login
    def api_posts_save(post_id):
        """Save/unsave a post for the current user."""
        try:
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'success': False, 'error': 'Post not found'}), 404

            existing = PostSave.query.filter_by(
                post_id=post_id, user_id=current_user.id
            ).first()

            if existing:
                db.session.delete(existing)
                db.session.commit()
                return jsonify({'success': True, 'saved': False})

            save = PostSave(post_id=post_id, user_id=current_user.id)
            db.session.add(save)
            db.session.commit()
            return jsonify({'success': True, 'saved': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error saving post {post_id}: {e}")
            return jsonify({'success': False, 'error': 'Failed to save post'}), 500

    @app.route('/api/explore-posts', methods=['GET'])
    @require_login
    def api_explore_posts():
        """Return explore feed: followed users' posts first, then suggested posts."""
        try:
            # Users the current user follows
            following = Follower.query.filter_by(
                follower_id=current_user.id
            ).all()
            following_ids = [f.user_id for f in following]
            if current_user.id not in following_ids:
                following_ids.append(current_user.id)

            # Posts from followed users
            followed_posts = (
                Post.query.filter(Post.user_id.in_(following_ids))
                .order_by(Post.created_at.desc())
                .all()
            )

            # Suggested posts from others
            if following_ids:
                suggested_posts = (
                    Post.query.filter(~Post.user_id.in_(following_ids))
                    .order_by(Post.created_at.desc())
                    .limit(50)
                    .all()
                )
            else:
                suggested_posts = (
                    Post.query.order_by(Post.created_at.desc()).limit(50).all()
                )

            def serialize_post(post, is_friend_post):
                author = post.author
                # Check if current user already follows this author
                is_following_author = post.user_id in following_ids
                
                # Check if current user liked this post
                liked = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None
                # Check if current user saved this post
                saved = PostSave.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None

                return {
                    'id': post.id,
                    'user_id': post.user_id,
                    'author_name': author.full_name if author else 'User',
                    'author_image': (
                        author.profile_image_url if author else None
                    ),
                    'code': post.code,
                    'language': post.language,
                    'description': post.description or '',
                    'likes': post.likes or 0,
                    'comments_count': len(post.comments or []),
                    'created_at': post.created_at.isoformat(),
                    'is_friend_post': is_friend_post,
                    'liked': liked,
                    'saved': saved,
                    'is_following_author': is_following_author,
                }

            payload = {
                'following_posts': [
                    serialize_post(p, True) for p in followed_posts
                ],
                'suggested_posts': [
                    serialize_post(p, False) for p in suggested_posts
                ],
            }

            return jsonify(payload)
        except Exception as e:
            print(f"Error building explore feed: {e}")
            return jsonify({'following_posts': [], 'suggested_posts': []}), 500

    # ---------------------------------------------------------
    # Follow Request Actions & Notifications
    # ---------------------------------------------------------

    @app.route('/api/follow/accept', methods=['POST'])
    @require_login
    def api_follow_accept():
        """Accept a follow request and create follower link + notifications."""
        try:
            data = request.get_json() or {}
            request_id = data.get('request_id')
            if not request_id:
                return jsonify({'success': False, 'error': 'request_id is required'}), 400

            follow_req = FollowRequest.query.get(request_id)
            if not follow_req or follow_req.to_user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Request not found'}), 404

            follow_req.status = 'accepted'

            # Create follower entry: requester now follows the current user
            existing = Follower.query.filter_by(
                user_id=current_user.id,
                follower_id=follow_req.from_user_id,
            ).first()
            if not existing:
                follower = Follower(
                    user_id=current_user.id,
                    follower_id=follow_req.from_user_id,
                )
                db.session.add(follower)

            # Update the original follow-request notification for the receiver
            original_notif = Notification.query.filter_by(
                follow_request_id=follow_req.id,
                user_id=current_user.id,
                type='follow_request',
            ).first()
            from_user = User.query.get(follow_req.from_user_id)
            if original_notif and from_user:
                # Change message so UI shows "View" instead of Accept/Delete
                original_notif.message = f"{from_user.full_name} started following you"
                original_notif.read_status = True

            # Notification to requester: request accepted
            from_user = User.query.get(follow_req.from_user_id)
            notif = Notification(
                user_id=follow_req.from_user_id,
                from_user_id=current_user.id,
                message=f"{current_user.full_name} accepted your follow request",
                type='accepted',
                follow_request_id=follow_req.id,
            )
            db.session.add(notif)

            db.session.commit()

            # Emit real-time notification
            socketio.emit(
                'new_notification',
                {
                    'id': notif.id,
                    'user_id': notif.user_id,
                    'from_user': {
                        'id': current_user.id,
                        'first_name': current_user.first_name,
                        'last_name': current_user.last_name,
                        'username': current_user.username,
                        'profile_image_url': current_user.profile_image_url,
                    },
                    'message': notif.message,
                    'type': notif.type,
                    'created_at': notif.created_at.isoformat(),
                    'read_status': notif.read_status,
                },
                room=f'user_{notif.user_id}',
            )

            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error accepting follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to accept request'}), 500

    @app.route('/api/follow/reject', methods=['POST'])
    @require_login
    def api_follow_reject():
        """Reject a follow request."""
        try:
            data = request.get_json() or {}
            request_id = data.get('request_id')
            if not request_id:
                return jsonify({'success': False, 'error': 'request_id is required'}), 400

            follow_req = FollowRequest.query.get(request_id)
            if not follow_req or follow_req.to_user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Request not found'}), 404

            follow_req.status = 'rejected'
            # Remove the original follow-request notification for the receiver
            notif = Notification.query.filter_by(
                follow_request_id=follow_req.id,
                user_id=current_user.id,
                type='follow_request',
            ).first()
            if notif:
                db.session.delete(notif)

            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error rejecting follow request: {e}")
            return jsonify({'success': False, 'error': 'Failed to reject request'}), 500

    # ---------------------------------------------------------
    # Notifications API
    # ---------------------------------------------------------

    @app.route('/api/notifications', methods=['GET'])
    @require_login
    def api_notifications():
        """Return all notifications for the current user."""
        try:
            notifications = (
                Notification.query.filter_by(user_id=current_user.id)
                .order_by(Notification.created_at.desc())
                .all()
            )

            result = []
            for n in notifications:
                from_user = n.from_user
                result.append(
                    {
                        'id': n.id,
                        'user_id': n.user_id,
                        'message': n.message,
                        'type': n.type,
                        'created_at': n.created_at.isoformat(),
                        'read_status': n.read_status,
                        'follow_request_id': n.follow_request_id,
                        'post_id': n.post_id,
                        'from_user': {
                            'id': from_user.id if from_user else None,
                            'first_name': getattr(from_user, 'first_name', None),
                            'last_name': getattr(from_user, 'last_name', None),
                            'username': getattr(from_user, 'username', None),
                            'profile_image_url': getattr(
                                from_user, 'profile_image_url', None
                            ),
                        }
                        if from_user
                        else None,
                    }
                )

            return jsonify({'success': True, 'notifications': result})
        except Exception as e:
            print(f"Error listing notifications: {e}")
            return jsonify({'success': False, 'error': 'Failed to load notifications'}), 500

    @app.route('/api/notifications/unread-count', methods=['GET'])
    @require_login
    def api_notifications_unread_count():
        """Return unread notification count for badge updates."""
        try:
            count = Notification.query.filter_by(
                user_id=current_user.id, read_status=False
            ).count()
            return jsonify({'count': count})
        except Exception as e:
            print(f"Error getting unread notification count: {e}")
            return jsonify({'count': 0}), 500

    @app.route('/api/notifications/read-all', methods=['POST'])
    @require_login
    def api_notifications_read_all():
        """Mark all notifications as read for the current user."""
        try:
            Notification.query.filter_by(
                user_id=current_user.id, read_status=False
            ).update({'read_status': True})
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error marking notifications as read: {e}")
            return jsonify({'success': False, 'error': 'Failed to mark as read'}), 500

    # ---------------------------------------------------------
    # Time Tracker API
    # ---------------------------------------------------------

    @app.route('/api/time-tracker/stats', methods=['GET'])
    @require_login
    def api_time_tracker_stats():
        """Return aggregated time-spent stats for the current user."""
        try:
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)

            q = TimeSpent.query.filter_by(user_id=current_user.id)

            # Today
            today_entry = q.filter(TimeSpent.date == today).first()
            today_minutes = today_entry.minutes if today_entry else 0

            # This week
            week_minutes = (
                q.filter(TimeSpent.date >= start_of_week)
                .with_entities(db.func.coalesce(db.func.sum(TimeSpent.minutes), 0))
                .scalar()
            )

            # This month
            month_minutes = (
                q.filter(TimeSpent.date >= start_of_month)
                .with_entities(db.func.coalesce(db.func.sum(TimeSpent.minutes), 0))
                .scalar()
            )

            # Total
            total_minutes = (
                q.with_entities(db.func.coalesce(db.func.sum(TimeSpent.minutes), 0))
                .scalar()
            )

            # Days active & streaks
            days = (
                q.order_by(TimeSpent.date.asc()).with_entities(TimeSpent.date).all()
            )
            day_list = [d[0] for d in days]
            total_days_active = len(day_list)

            longest_streak = 0
            current_streak = 0
            prev_day = None
            for d in day_list:
                if prev_day is None or d == prev_day + timedelta(days=1):
                    current_streak = current_streak + 1 if prev_day else 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1
                prev_day = d
            longest_streak = max(longest_streak, current_streak)

            # If last active day isn't today, current streak is 0
            if not day_list or day_list[-1] != today:
                current_streak = 0

            return jsonify(
                {
                    'today_minutes': today_minutes,
                    'week_minutes': int(week_minutes or 0),
                    'month_minutes': int(month_minutes or 0),
                    'total_minutes': int(total_minutes or 0),
                    'total_days_active': total_days_active,
                    'current_streak_days': current_streak,
                    'longest_streak_days': longest_streak,
                }
            )
        except Exception as e:
            print(f"Error computing time-tracker stats: {e}")
            return jsonify({'error': 'Failed to load stats'}), 500

    @app.route('/api/time-tracker/contributions', methods=['GET'])
    @require_login
    def api_time_tracker_contributions():
        """Return per-day minutes for the last year for contribution graph."""
        try:
            today = date.today()
            one_year_ago = today - timedelta(days=365)

            entries = (
                TimeSpent.query.filter(
                    TimeSpent.user_id == current_user.id,
                    TimeSpent.date >= one_year_ago,
                    TimeSpent.date <= today,
                )
                .order_by(TimeSpent.date.asc())
                .all()
            )

            days = [
                {'date': ts.date.isoformat(), 'minutes': ts.minutes}
                for ts in entries
            ]

            return jsonify({'days': days})
        except Exception as e:
            print(f"Error loading time-tracker contributions: {e}")
            return jsonify({'days': []}), 500

    @app.route('/api/user/<user_id>/posts', methods=['GET'])
    @require_login
    def api_user_posts(user_id):
        """Get posts by a specific user"""
        try:
            # Verify the user exists
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
            
            posts_data = []
            for post in posts:
                author = post.author
                # Check if current user liked this post
                liked = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None
                
                posts_data.append({
                    'id': post.id,
                    'user_id': post.user_id,
                    'author_name': author.full_name if author else 'Unknown',
                    'author_image': author.profile_image_url if author else None,
                    'code': post.code,
                    'language': post.language,
                    'description': post.description or '',
                    'likes': post.likes or 0,
                    'comments_count': len(post.comments or []),
                    'created_at': post.created_at.isoformat(),
                    'liked': liked
                })
            
            return jsonify({'success': True, 'posts': posts_data})
        except Exception as e:
            print(f"Error getting user posts: {e}")
            return jsonify({'success': False, 'error': 'Failed to get posts'}), 500

    @app.route('/api/user/<user_id>/saved-posts', methods=['GET'])
    @require_login
    def api_user_saved_posts(user_id):
        """Get saved posts by a specific user"""
        try:
            # Verify the user exists and it's the current user
            if user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            
            saved_posts = PostSave.query.filter_by(user_id=user_id).all()
            
            posts_data = []
            for saved in saved_posts:
                post = saved.post
                if post:
                    author = post.author
                    # Check if current user liked this post
                    liked = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None
                    
                    posts_data.append({
                        'id': post.id,
                        'user_id': post.user_id,
                        'author_name': author.full_name if author else 'Unknown',
                        'author_image': author.profile_image_url if author else None,
                        'code': post.code,
                        'language': post.language,
                        'description': post.description or '',
                        'likes': post.likes or 0,
                        'comments_count': len(post.comments or []),
                        'created_at': post.created_at.isoformat(),
                        'liked': liked
                    })
            
            return jsonify({'success': True, 'posts': posts_data})
        except Exception as e:
            print(f"Error getting saved posts: {e}")
            return jsonify({'success': False, 'error': 'Failed to get saved posts'}), 500

    @app.route('/api/user/<user_id>/liked-posts', methods=['GET'])
    @require_login
    def api_user_liked_posts(user_id):
        """Get liked posts by a specific user"""
        try:
            # Verify the user exists and it's the current user
            if user_id != current_user.id:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            
            liked_posts = PostLike.query.filter_by(user_id=user_id).all()
            
            posts_data = []
            for liked in liked_posts:
                post = liked.post
                if post:
                    author = post.author
                    # Check if current user liked this post (should be true, but just in case)
                    liked_status = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first() is not None
                    
                    posts_data.append({
                        'id': post.id,
                        'user_id': post.user_id,
                        'author_name': author.full_name if author else 'Unknown',
                        'author_image': author.profile_image_url if author else None,
                        'code': post.code,
                        'language': post.language,
                        'description': post.description or '',
                        'likes': post.likes or 0,
                        'comments_count': len(post.comments or []),
                        'created_at': post.created_at.isoformat(),
                        'liked': liked_status
                    })
            
            return jsonify({'success': True, 'posts': posts_data})
        except Exception as e:
            print(f"Error getting liked posts: {e}")
            return jsonify({'success': False, 'error': 'Failed to get liked posts'}), 500

    @app.route('/api/user/<user_id>/followers', methods=['GET'])
    @require_login
    def api_user_followers(user_id):
        """Get followers for a specific user"""
        try:
            # Verify the user exists
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            followers = Follower.query.filter_by(user_id=user_id).all()
            
            followers_data = []
            for follower in followers:
                user = follower.follower
                if user:
                    followers_data.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'profile_image_url': user.profile_image_url,
                        'followed_at': follower.created_at.isoformat() if follower.created_at else None
                    })
            
            return jsonify({'success': True, 'followers': followers_data})
        except Exception as e:
            print(f"Error getting followers: {e}")
            return jsonify({'success': False, 'error': 'Failed to get followers'}), 500

    @app.route('/api/user/<user_id>/following', methods=['GET'])
    @require_login
    def api_user_following(user_id):
        """Get users that a specific user is following"""
        try:
            # Verify the user exists
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            following = Follower.query.filter_by(follower_id=user_id).all()
            
            following_data = []
            for follow in following:
                user = follow.user
                if user:
                    following_data.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'profile_image_url': user.profile_image_url,
                        'followed_at': follow.created_at.isoformat() if follow.created_at else None
                    })
            
            return jsonify({'success': True, 'following': following_data})
        except Exception as e:
            print(f"Error getting following: {e}")
            return jsonify({'success': False, 'error': 'Failed to get following'}), 500

    @app.route('/api/user-stats')
    @require_login
    def api_user_stats():
        """Get current user stats including time tracking"""
        try:
            # Post count
            post_count = Post.query.filter_by(user_id=current_user.id).count()
            
            # Follower/Following counts
            follower_count = Follower.query.filter_by(user_id=current_user.id).count()
            following_count = Follower.query.filter_by(follower_id=current_user.id).count()
            
            # Time tracking stats
            today = date.today()
            
            # 1. Today's time
            today_time = TimeSpent.query.filter_by(user_id=current_user.id, date=today).first()
            today_minutes = today_time.minutes if today_time else 0
            
            # 2. Last 7 days
            last_7_days = []
            for i in range(7):
                day = today - timedelta(days=i)
                time_record = TimeSpent.query.filter_by(user_id=current_user.id, date=day).first()
                minutes = time_record.minutes if time_record else 0
                last_7_days.append({
                    'date': day.isoformat(),
                    'day_name': day.strftime('%a'),
                    'minutes': minutes
                })
            last_7_days.reverse() # Show oldest to newest
            
            # 3. Last month total
            thirty_days_ago = today - timedelta(days=30)
            last_month_total = db.session.query(db.func.sum(TimeSpent.minutes)).filter(
                TimeSpent.user_id == current_user.id,
                TimeSpent.date >= thirty_days_ago
            ).scalar() or 0
            
            # 4. Total active days
            total_active_days = TimeSpent.query.filter_by(user_id=current_user.id).count()
            
            # 5. Streaks
            current_streak = current_user.current_streak or 0
            
            if current_user.last_streak_date and current_user.last_streak_date < (today - timedelta(days=1)):
                 current_streak = 0
                 
            longest_streak = current_user.longest_streak or 0

            # Format time for display (e.g. "2h 35m")
            def format_minutes(mins):
                h = mins // 60
                m = mins % 60
                if h > 0:
                    return f"{h}h {m}m"
                return f"{m}m"

            return jsonify({
                'post_count': post_count,
                'follower_count': follower_count,
                'following_count': following_count,
                'today_minutes': today_minutes,
                'today_time_display': format_minutes(today_minutes),
                'last_7_days': last_7_days,
                'last_month_total': last_month_total,
                'last_month_display': format_minutes(last_month_total),
                'total_active_days': total_active_days,
                'current_streak': current_streak,
                'longest_streak': longest_streak
            })
            
        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return jsonify({'error': 'Failed to fetch stats'}), 500

