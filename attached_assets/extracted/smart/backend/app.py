# Main Python application file
# We will use Flask for the web framework

from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

# Load environment variables from .env file
load_dotenv()

# App configuration
app = Flask(__name__, static_folder='../frontend', static_url_path='', template_folder='../frontend')

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash',
                                  safety_settings={
                                      HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                  })
else:
    model = None # Set model to None if API key is not found

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "a_very_secret_key") # Use environment variable or a default
db = SQLAlchemy(app)

# OAuth Configuration
oauth = OAuth(app)

google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")

if google_client_id and google_client_secret:
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        access_token_url='https://oauth2.googleapis.com/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid email profile'},
    )

if github_client_id and github_client_secret:
    oauth.register(
        name='github',
        client_id=github_client_id,
        client_secret=github_client_secret,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    auth_provider = db.Column(db.String(20))
    provider_id = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Code Snippet Model
class CodeSnippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Snippet Version Model
class SnippetVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snippet_id = db.Column(db.Integer, db.ForeignKey('code_snippet.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    review_output = db.Column(db.Text)
    explain_output = db.Column(db.Text)
    compile_output = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Dictionary Entry Model
class DictionaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    term = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    snippet_id = db.Column(db.Integer, db.ForeignKey('code_snippet.id'))
    caption = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Friend Model
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'pending', 'accepted', 'declined'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'friend_request', 'new_like', 'new_comment'
    related_id = db.Column(db.Integer) # ID of the related item (e.g., user_id, post_id)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_code_snippet = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# TimeSpent Model
class TimeSpent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature = db.Column(db.String(50), nullable=False) # e.g., 'code_review', 'chat', 'dictionary'
    duration_seconds = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, default=db.func.current_date())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print(f"Signup attempt with data: {data}") # Log incoming data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        print(f"Signup failed: Username {username} already exists")
        return jsonify({'message': 'Username already exists'}), 409
    if User.query.filter_by(email=email).first():
        print(f"Signup failed: Email {email} already registered")
        return jsonify({'message': 'Email already registered'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} created successfully")
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        print(f"User {username} created successfully")
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id, 'username': new_user.username}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during signup for user {username}: {e}")
        return jsonify({'message': f'An error occurred during signup: {str(e)}'}), 500

@app.route('/login/google')
def login_google():
    if 'google' not in oauth.clients:
        return jsonify({'message': 'Google OAuth not configured. Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env'}), 500
    redirect_uri = url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/github')
def login_github():
    if 'github' not in oauth.clients:
        return jsonify({'message': 'GitHub OAuth not configured. Check GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env'}), 500
    redirect_uri = url_for('authorize_github', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    if 'google' not in oauth.clients:
        return jsonify({'message': 'Google OAuth not configured. Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env'}), 500
    try:
        token = oauth.google.authorize_access_token()
        userinfo = oauth.google.parse_id_token(token)
        
        username = userinfo['name']
        email = userinfo['email']
        provider_id = userinfo['id']

        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if not exists
            user = User(username=username, email=email, auth_provider='google', provider_id=provider_id)
            user.set_password(os.urandom(16).hex()) # Set a random password for OAuth users
            db.session.add(user)
            db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('main_page'))
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return jsonify({'message': f'Google login failed: {str(e)}'}), 500

@app.route('/authorize/github')
def authorize_github():
    if 'github' not in oauth.clients:
        return jsonify({'message': 'GitHub OAuth not configured. Check GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env'}), 500
    try:
        token = oauth.github.authorize_access_token()
        resp = oauth.github.get('user', token=token)
        profile = resp.json()
        
        username = profile['login']
        email = profile.get('email')
        provider_id = str(profile['id'])

        if not email:
            # GitHub's user endpoint might not always return email, fetch from emails endpoint
            emails_resp = oauth.github.get('user/emails', token=token)
            emails = emails_resp.json()
            for e in emails:
                if e['primary'] and e['verified']:
                    email = e['email']
                    break
            if not email:
                return jsonify({'message': 'GitHub email not found or verified'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if not exists
            user = User(username=username, email=email, auth_provider='github', provider_id=provider_id)
            user.set_password(os.urandom(16).hex()) # Set a random password for OAuth users
            db.session.add(user)
            db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('main_page'))
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        return jsonify({'message': f'GitHub login failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"Login attempt with data: {data}") # Log incoming data
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        print(f"Login successful for user: {username}")
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'username': user.username}), 200
    
    print(f"Login failed for user: {username}. Invalid credentials.")
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/main')
def main_page():
    return render_template('main.html')

@app.route('/analyze', methods=['POST'])
def analyze_code():
    data = request.get_json()
    code = data.get('code')
    action = data.get('action') # 'review', 'explain', or 'compile'
    profession = data.get('profession', 'software engineer') # Default profession

    prompt = f"As a {profession}, {action} the following code:\n\n```\n{code}\n```"

    if not model:
        return jsonify({'error': 'Gemini API key not configured. Please set GEMINI_API_KEY in your .env file.'}), 500
    try:
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': f"Gemini API Error: {str(e)}"}), 500

@app.route('/qna', methods=['POST'])
def handle_qna():
    data = request.get_json()
    code = data.get('code')
    question = data.get('question')

    prompt = f"Regarding the following code:\n\n```\n{code}\n```\n\nQuestion: {question}\nAnswer:"

    if not model:
        return jsonify({'error': 'Gemini API key not configured. Please set GEMINI_API_KEY in your .env file.'}), 500
    try:
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': f"Gemini API Error: {str(e)}"}), 500

@app.route('/dictionary')
def dictionary_page():
    return render_template('dictionary.html')

@app.route('/api/dictionary/<string:language>', methods=['GET'])
def get_dictionary_entries(language):
    entries = DictionaryEntry.query.filter_by(language=language).all()
    output = []
    for entry in entries:
        output.append({
            'id': entry.id,
            'language': entry.language,
            'term': entry.term,
            'definition': entry.definition,
            'created_at': entry.created_at,
            'updated_at': entry.updated_at
        })
    return jsonify(output), 200

@app.route('/translate_page')
def translate_page():
    return render_template('translate.html')

@app.route('/translate', methods=['POST'])
def translate_code():
    data = request.get_json()
    code = data.get('code')
    source_lang = data.get('sourceLang')
    target_lang = data.get('targetLang')

    prompt = f"Translate the following {source_lang} code to {target_lang}:\n\n```\n{code}\n```"

    if not model:
        return jsonify({'error': 'Gemini API key not configured. Please set GEMINI_API_KEY in your .env file.'}), 500
    try:
        response = model.generate_content(prompt)
        return jsonify({'translated_code': response.text})
    except Exception as e:
        return jsonify({'error': f"Gemini API Error: {str(e)}"}), 500

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/snippets', methods=['POST'])
def save_snippet():
    data = request.get_json()
    user_id = 1 # Placeholder for actual user ID
    title = data.get('title')
    language = data.get('language')
    code_content = data.get('code_content')
    review_output = data.get('review_output')
    explain_output = data.get('explain_output')
    compile_output = data.get('compile_output')

    new_snippet = CodeSnippet(user_id=user_id, title=title, language=language)
    db.session.add(new_snippet)
    db.session.commit()

    new_version = SnippetVersion(
        snippet_id=new_snippet.id,
        version_number=1,
        code_content=code_content,
        review_output=review_output,
        explain_output=explain_output,
        compile_output=compile_output
    )
    db.session.add(new_version)
    db.session.commit()

    return jsonify({'message': 'Snippet saved successfully', 'snippet_id': new_snippet.id}), 201

@app.route('/snippets', methods=['GET'])
def get_snippets():
    user_id = 1 # Placeholder for actual user ID
    snippets = CodeSnippet.query.filter_by(user_id=user_id).all()
    output = []
    for snippet in snippets:
        latest_version = SnippetVersion.query.filter_by(snippet_id=snippet.id).order_by(SnippetVersion.version_number.desc()).first()
        output.append({
            'id': snippet.id,
            'title': snippet.title,
            'language': snippet.language,
            'created_at': snippet.created_at,
            'latest_code': latest_version.code_content if latest_version else None
        })
    return jsonify(output), 200

@app.route('/snippets/<int:snippet_id>/versions', methods=['GET'])
def get_snippet_versions(snippet_id):
    versions = SnippetVersion.query.filter_by(snippet_id=snippet_id).order_by(SnippetVersion.version_number.asc()).all()
    output = []
    for version in versions:
        output.append({
            'id': version.id,
            'snippet_id': version.snippet_id,
            'version_number': version.version_number,
            'code_content': version.code_content,
            'review_output': version.review_output,
            'explain_output': version.explain_output,
            'compile_output': version.compile_output,
            'created_at': version.created_at
        })
    return jsonify(output), 200

@app.route('/snippets/<int:snippet_id>/versions', methods=['POST'])
def add_snippet_version(snippet_id):
    data = request.get_json()
    code_content = data.get('code_content')
    review_output = data.get('review_output')
    explain_output = data.get('explain_output')
    compile_output = data.get('compile_output')

    latest_version = SnippetVersion.query.filter_by(snippet_id=snippet_id).order_by(SnippetVersion.version_number.desc()).first()
    new_version_number = (latest_version.version_number + 1) if latest_version else 1

    new_version = SnippetVersion(
        snippet_id=snippet_id,
        version_number=new_version_number,
        code_content=code_content,
        review_output=review_output,
        explain_output=explain_output,
        compile_output=compile_output
    )
    db.session.add(new_version)
    db.session.commit()

    return jsonify({'message': 'New version added successfully', 'version_id': new_version.id}), 201

@app.route('/api/dictionary', methods=['POST'])
def add_dictionary_entry():
    data = request.get_json()
    user_id = 1 # Placeholder for actual admin user ID
    language = data.get('language')
    term = data.get('term')
    definition = data.get('definition')

    if not all([language, term, definition]):
        return jsonify({'message': 'Missing data for dictionary entry'}), 400

    new_entry = DictionaryEntry(user_id=user_id, language=language, term=term, definition=definition)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Dictionary entry added successfully', 'entry_id': new_entry.id}), 201

@app.route('/api/dictionary/<int:entry_id>', methods=['PUT'])
def update_dictionary_entry(entry_id):
    data = request.get_json()
    entry = DictionaryEntry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Dictionary entry not found'}), 404

    entry.language = data.get('language', entry.language)
    entry.term = data.get('term', entry.term)
    entry.definition = data.get('definition', entry.definition)
    db.session.commit()
    return jsonify({'message': 'Dictionary entry updated successfully'}), 200

@app.route('/api/dictionary/<int:entry_id>', methods=['DELETE'])
def delete_dictionary_entry(entry_id):
    entry = DictionaryEntry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Dictionary entry not found'}), 404
    
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Dictionary entry deleted successfully'}), 200

# --- Post Routes ---
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    user_id = 1 # Placeholder for actual user ID
    snippet_id = data.get('snippet_id')
    caption = data.get('caption')

    new_post = Post(user_id=user_id, snippet_id=snippet_id, caption=caption)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully', 'post_id': new_post.id}), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    output = []
    for post in posts:
        user = User.query.get(post.user_id)
        snippet = CodeSnippet.query.get(post.snippet_id)
        latest_version = None
        if snippet:
            latest_version = SnippetVersion.query.filter_by(snippet_id=snippet.id).order_by(SnippetVersion.version_number.desc()).first()

        output.append({
            'id': post.id,
            'user_id': post.user_id,
            'username': user.username if user else 'Unknown',
            'snippet_id': post.snippet_id,
            'snippet_title': snippet.title if snippet else None,
            'code_content': latest_version.code_content if latest_version else None,
            'language': snippet.language if snippet else None,
            'caption': post.caption,
            'created_at': post.created_at,
            'likes_count': Like.query.filter_by(post_id=post.id).count(),
            'comments_count': Comment.query.filter_by(post_id=post.id).count()
        })
    return jsonify(output), 200

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    user = User.query.get(post.user_id)
    snippet = CodeSnippet.query.get(post.snippet_id)
    latest_version = None
    if snippet:
        latest_version = SnippetVersion.query.filter_by(snippet_id=snippet.id).order_by(SnippetVersion.version_number.desc()).first()

    return jsonify({
        'id': post.id,
        'user_id': post.user_id,
        'username': user.username if user else 'Unknown',
        'snippet_id': post.snippet_id,
        'snippet_title': snippet.title if snippet else None,
        'code_content': latest_version.code_content if latest_version else None,
        'language': snippet.language if snippet else None,
        'caption': post.caption,
        'created_at': post.created_at,
        'likes_count': Like.query.filter_by(post_id=post.id).count(),
        'comments_count': Comment.query.filter_by(post_id=post.id).count()
    }), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200

# --- Like Routes ---
@app.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    user_id = 1 # Placeholder for actual user ID
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_like:
        return jsonify({'message': 'Post already liked'}), 409
    
    new_like = Like(user_id=user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()

    # Create notification for the post owner
    post = Post.query.get(post_id)
    if post and post.user_id != user_id: # Don't notify if user likes their own post
        notification = Notification(user_id=post.user_id, type='new_like', related_id=post_id)
        db.session.add(notification)
        db.session.commit()

    return jsonify({'message': 'Post liked successfully'}), 201

@app.route('/posts/<int:post_id>/unlike', methods=['POST'])
def unlike_post(post_id):
    user_id = 1 # Placeholder for actual user ID
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if not existing_like:
        return jsonify({'message': 'Post not liked yet'}), 409
    
    db.session.delete(existing_like)
    db.session.commit()
    return jsonify({'message': 'Post unliked successfully'}), 200

# --- Comment Routes ---
@app.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    user_id = 1 # Placeholder for actual user ID
    content = data.get('content')

    if not content:
        return jsonify({'message': 'Comment content cannot be empty'}), 400

    new_comment = Comment(user_id=user_id, post_id=post_id, content=content)
    db.session.add(new_comment)
    db.session.commit()

    # Create notification for the post owner
    post = Post.query.get(post_id)
    if post and post.user_id != user_id: # Don't notify if user comments on their own post
        notification = Notification(user_id=post.user_id, type='new_comment', related_id=post_id)
        db.session.add(notification)
        db.session.commit()

    return jsonify({'message': 'Comment added successfully', 'comment_id': new_comment.id}), 201

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    output = []
    for comment in comments:
        user = User.query.get(comment.user_id)
        output.append({
            'id': comment.id,
            'user_id': comment.user_id,
            'username': user.username if user else 'Unknown',
            'content': comment.content,
            'created_at': comment.created_at
        })
    return jsonify(output), 200

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200

# --- Notification Routes ---
@app.route('/notifications', methods=['GET'])
def get_notifications():
    user_id = 1 # Placeholder for actual user ID
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    output = []
    for notification in notifications:
        output.append({
            'id': notification.id,
            'user_id': notification.user_id,
            'type': notification.type,
            'related_id': notification.related_id,
            'is_read': notification.is_read,
            'created_at': notification.created_at
        })
    return jsonify(output), 200

@app.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'message': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200

# --- Friend Routes ---
@app.route('/friends/request/<int:receiver_id>', methods=['POST'])
def send_friend_request(receiver_id):
    sender_id = 1 # Placeholder for actual user ID
    if sender_id == receiver_id:
        return jsonify({'message': 'Cannot send friend request to yourself'}), 400

    existing_request = Friend.query.filter(
        ((Friend.user1_id == sender_id) & (Friend.user2_id == receiver_id)) |
        ((Friend.user1_id == receiver_id) & (Friend.user2_id == sender_id))
    ).first()

    if existing_request:
        return jsonify({'message': 'Friend request already sent or friendship already exists'}), 409
    
    new_friend_request = Friend(user1_id=sender_id, user2_id=receiver_id, status='pending')
    db.session.add(new_friend_request)
    db.session.commit()

    # Create notification for the receiver
    notification = Notification(user_id=receiver_id, type='friend_request', related_id=sender_id)
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Friend request sent'}), 201

@app.route('/friends/accept/<int:sender_id>', methods=['POST'])
def accept_friend_request(sender_id):
    receiver_id = 1 # Placeholder for actual user ID
    friend_request = Friend.query.filter_by(user1_id=sender_id, user2_id=receiver_id, status='pending').first()
    if not friend_request:
        return jsonify({'message': 'Friend request not found'}), 404
    
    friend_request.status = 'accepted'
    db.session.commit()

    # Create notification for the sender
    notification = Notification(user_id=sender_id, type='friend_request_accepted', related_id=receiver_id)
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Friend request accepted'}), 200

@app.route('/friends/decline/<int:sender_id>', methods=['POST'])
def decline_friend_request(sender_id):
    receiver_id = 1 # Placeholder for actual user ID
    friend_request = Friend.query.filter_by(user1_id=sender_id, user2_id=receiver_id, status='pending').first()
    if not friend_request:
        return jsonify({'message': 'Friend request not found'}), 404
    
    friend_request.status = 'declined'
    db.session.commit()
    return jsonify({'message': 'Friend request declined'}), 200

@app.route('/friends', methods=['GET'])
def get_user_friends():
    user_id = 1 # Placeholder for actual user ID
    friends = Friend.query.filter(
        ((Friend.user1_id == user_id) | (Friend.user2_id == user_id)) &
        (Friend.status == 'accepted')
    ).all()
    
    output = []
    for friend_rel in friends:
        friend_id = friend_rel.user2_id if friend_rel.user1_id == user_id else friend_rel.user1_id
        friend_user = User.query.get(friend_id)
        if friend_user:
            output.append({'id': friend_user.id, 'username': friend_user.username})
    return jsonify(output), 200

# --- Chat Routes ---
@app.route('/api/messages/<int:friend_id>', methods=['GET'])
def get_messages(friend_id):
    user_id = 1 # Placeholder for actual user ID
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.asc()).all()

    output = []
    for message in messages:
        output.append({
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'is_code_snippet': message.is_code_snippet,
            'created_at': message.created_at
        })
    return jsonify(output), 200

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = 1 # Placeholder for actual logged-in user ID
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    is_code_snippet = data.get('is_code_snippet', False)

    if not content:
        return jsonify({'message': 'Message content cannot be empty'}), 400

    new_message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content, is_code_snippet=is_code_snippet)
    db.session.add(new_message)
    db.session.commit()

    # Create notification for the receiver
    notification = Notification(user_id=receiver_id, type='new_message', related_id=sender_id)
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully', 'message_id': new_message.id}), 201

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    posts_count = Post.query.filter_by(user_id=user_id).count()
    friends_count = Friend.query.filter(
        ((Friend.user1_id == user_id) | (Friend.user2_id == user_id)) &
        (Friend.status == 'accepted')
    ).count()

    return jsonify({
        'name': user.username,
        'email': user.email,
        'bio': user.bio,
        'posts_count': posts_count,
        'friends_count': friends_count
    }), 200

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/api/friends', methods=['GET'])
def get_friends():
    user_id = 1 # Placeholder for actual user ID
    friends = Friend.query.filter(
        ((Friend.user1_id == user_id) | (Friend.user2_id == user_id)) &
        (Friend.status == 'accepted')
    ).all()
    
    output = []
    for friend_rel in friends:
        friend_id = friend_rel.user2_id if friend_rel.user1_id == user_id else friend_rel.user1_id
        friend_user = User.query.get(friend_id)
        if friend_user:
            output.append({'id': friend_user.id, 'username': friend_user.username})
    return jsonify(output), 200

# --- Time Spent Routes ---
@app.route('/api/time_spent', methods=['POST'])
def add_time_spent():
    data = request.get_json()
    user_id = 1 # Placeholder for actual user ID
    feature = data.get('feature')
    duration_seconds = data.get('duration_seconds')

    if not all([feature, duration_seconds]):
        return jsonify({'message': 'Missing data for time spent entry'}), 400
    
    new_time_spent = TimeSpent(user_id=user_id, feature=feature, duration_seconds=duration_seconds)
    db.session.add(new_time_spent)
    db.session.commit()
    return jsonify({'message': 'Time spent entry added successfully', 'id': new_time_spent.id}), 201

@app.route('/api/time_spent', methods=['GET'])
def get_time_spent():
    user_id = 1 # Placeholder for actual user ID
    time_spent_entries = TimeSpent.query.filter_by(user_id=user_id).order_by(TimeSpent.date.desc(), TimeSpent.created_at.desc()).all()
    
    output = []
    for entry in time_spent_entries:
        output.append({
            'id': entry.id,
            'user_id': entry.user_id,
            'feature': entry.feature,
            'duration_seconds': entry.duration_seconds,
            'date': entry.date.isoformat(),
            'created_at': entry.created_at.isoformat()
        })
    return jsonify(output), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
