from datetime import datetime
from database import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profile_image_url = db.Column(db.String(255), nullable=True)
    profile_image_path = db.Column(db.String(255), nullable=True)  # For uploaded images
    bio = db.Column(db.Text, nullable=True)
    profession = db.Column(db.String(50), default='student')
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'google', 'github', or None
    oauth_id = db.Column(db.String(255), nullable=True)
    is_user_active = db.Column(db.Boolean, default=True, name='is_active')
    last_seen = db.Column(db.DateTime, default=datetime.now)
    is_online = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime, default=datetime.now)  # For presence tracking
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Location fields
    location = db.Column(db.String(255), nullable=True)
    location_enabled = db.Column(db.Boolean, default=False)
    
    # Streak tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_streak_date = db.Column(db.Date, nullable=True)
    
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    code_history = db.relationship('CodeHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return self.email or 'User'
    
    def __repr__(self):
        return f'<User {self.email or self.username}>'

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)
    __table_args__ = (UniqueConstraint('user_id', 'browser_session_key', 'provider', name='uq_user_browser_session_key_provider'),)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    liked_by = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')

class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='uq_post_user_like'),)

class PostSave(db.Model):
    __tablename__ = 'post_saves'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='uq_post_user_save'),)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='comments')

class FollowRequest(db.Model):
    __tablename__ = 'follow_requests'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String, default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_follow_requests')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='received_follow_requests')
    __table_args__ = (UniqueConstraint('from_user_id', 'to_user_id', name='uq_follow_request'),)

class Follower(db.Model):
    __tablename__ = 'followers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # The user being followed
    follower_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # The user who is following
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='followers_list')
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_list')
    __table_args__ = (UniqueConstraint('user_id', 'follower_id', name='uq_follower'),)

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='sent_requests')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='received_requests')
    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='uq_user_friend'),)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    sender_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    content = db.Column(db.Text, nullable=True)  # Allow empty content for file/code-only messages
    message_type = db.Column(db.String(50), default='text') # text, image, video, file, code
    code_snippet = db.Column(db.Text, nullable=True)
    file_attachment = db.Column(db.String(255), nullable=True)  # Path to attached file
    file_type = db.Column(db.String(50), nullable=True)  # Type of file (image, video, pdf, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    members = db.relationship('GroupMember', backref='group', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='group_rel', lazy=True, cascade='all, delete-orphan')

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='uq_group_user'),)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, nullable=False)  # follow_request, accepted, follow_back, like, comment, system_update, post
    from_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    follow_request_id = db.Column(db.Integer, db.ForeignKey('follow_requests.id'), nullable=True)  # Link to follow request
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True) # Link to post
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    from_user = db.relationship('User', foreign_keys=[from_user_id])
    follow_request = db.relationship('FollowRequest', foreign_keys=[follow_request_id])
    post = db.relationship('Post', foreign_keys=[post_id])

class CodeHistory(db.Model):
    __tablename__ = 'code_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class TimeSpent(db.Model):
    __tablename__ = 'time_spent'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    minutes = db.Column(db.Integer, default=0)
    total_seconds = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = (UniqueConstraint('user_id', 'date', name='uq_user_date'),)