from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profession = db.Column(db.String, default='student')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    code_history = db.relationship('CodeHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy=True, cascade='all, delete-orphan')

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

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='comments')

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

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    members = db.relationship('GroupMember', backref='group', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='group', lazy=True, cascade='all, delete-orphan')

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
    type = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    from_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    from_user = db.relationship('User', foreign_keys=[from_user_id])

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
    __table_args__ = (UniqueConstraint('user_id', 'date', name='uq_user_date'),)
