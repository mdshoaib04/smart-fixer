import os
import uuid
from functools import wraps
from urllib.parse import urlencode
import logging

from flask import g, session, redirect, request, render_template, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

# Enable logging for OAuth debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import app and db later to avoid circular import
app = None
db = None

def init_oauth(flask_app, database):
    """Initialize OAuth with Flask app and database"""
    global app, db
    app = flask_app
    db = database
    
    # Log OAuth configuration for debugging
    google_client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    github_client_id = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
    github_client_secret = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
    
    logger.debug(f"Google Client ID: {google_client_id}")
    logger.debug(f"Google Client Secret length: {len(google_client_secret) if google_client_secret else 0}")
    logger.debug(f"GitHub Client ID: {github_client_id}")
    logger.debug(f"GitHub Client Secret length: {len(github_client_secret) if github_client_secret else 0}")
    
    # Validate that we have the required credentials
    if not google_client_id or not google_client_secret:
        logger.error("Google OAuth credentials are not properly configured in environment variables")
    
    # Create Google OAuth blueprint with proper callback URL
    google_bp = make_google_blueprint(
        client_id=google_client_id,
        client_secret=google_client_secret,
        scope=["openid", "profile", "email"],
        redirect_url="/auth/google/callback"
    )

    # Create GitHub OAuth blueprint
    github_bp = make_github_blueprint(
        client_id=github_client_id,
        client_secret=github_client_secret,
        scope=["user:email"],
        redirect_url="/auth/github/callback"
    )
    
    return google_bp, github_bp

login_manager = None

def init_login_manager(flask_app):
    global login_manager
    login_manager = LoginManager(flask_app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)

class UserSessionStorage(BaseStorage):
    def get(self, blueprint):
        try:
            token = db.session.query(OAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()

def create_or_update_user(provider, provider_user_id, user_info):
    """
    Create or update user based on OAuth provider info
    """
    # First, try to find user by provider and provider_user_id
    user = db.session.query(User).filter_by(oauth_provider=provider, oauth_id=provider_user_id).first()
    
    if user:
        # Update user info if it has changed
        user.email = user_info.get('email', user.email)
        user.first_name = user_info.get('first_name', user.first_name)
        user.last_name = user_info.get('last_name', user.last_name)
        user.profile_image_url = user_info.get('picture', user.profile_image_url) or user_info.get('avatar_url', user.profile_image_url)
        if not user.username:
            user.username = user_info.get('username', user_info.get('name', '').replace(' ', '_').lower())
    else:
        # Check if user exists by email
        email = user_info.get('email')
        if email:
            user = db.session.query(User).filter_by(email=email).first()
        
        if user:
            # Update existing user with OAuth info
            user.oauth_provider = provider
            user.oauth_id = provider_user_id
        else:
            # Create new user
            username = user_info.get('username', user_info.get('name', '').replace(' ', '_').lower())
            # Ensure username is unique
            counter = 1
            original_username = username
            while db.session.query(User).filter_by(username=username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=email,
                first_name=user_info.get('given_name', user_info.get('name', '').split()[0] if user_info.get('name') else ''),
                last_name=' '.join(user_info.get('name', '').split()[1:]) if user_info.get('name') else '',
                profile_image_url=user_info.get('picture') or user_info.get('avatar_url'),
                oauth_provider=provider,
                oauth_id=provider_user_id
            )
    
    db.session.add(user)
    db.session.commit()
    return user

def setup_oauth_handlers(google_bp, github_bp):
    """Set up OAuth authorized handlers"""
    
    @oauth_authorized.connect_via(google_bp)
    def google_logged_in(blueprint, token):
        logger.debug(f"Google OAuth authorized. Token: {token}")
        if not token:
            logger.error("No token received from Google OAuth")
            return False
        
        # Get user info from Google
        resp = google.get("/oauth2/v2/userinfo")
        logger.debug(f"Google userinfo response: {resp.status_code} - {resp.text}")
        if not resp.ok:
            logger.error(f"Failed to get user info from Google: {resp.text}")
            return False
        
        user_info = resp.json()
        logger.debug(f"Google user info: {user_info}")
        
        # Create or update user
        user = create_or_update_user('google', user_info['id'], user_info)
        
        # Log in the user
        login_user(user)
        
        # Store the token
        blueprint.token = token
        
        # Redirect to the next URL or home
        next_url = session.pop("next_url", "/")
        return redirect(next_url)

    @oauth_authorized.connect_via(github_bp)
    def github_logged_in(blueprint, token):
        logger.debug(f"GitHub OAuth authorized. Token: {token}")
        if not token:
            logger.error("No token received from GitHub OAuth")
            return False
        
        # Get user info from GitHub
        resp = github.get("/user")
        logger.debug(f"GitHub user response: {resp.status_code} - {resp.text}")
        if not resp.ok:
            logger.error(f"Failed to get user info from GitHub: {resp.text}")
            return False
        
        user_info = resp.json()
        logger.debug(f"GitHub user info: {user_info}")
        
        # Get email if not public
        if not user_info.get('email'):
            email_resp = github.get("/user/emails")
            logger.debug(f"GitHub emails response: {email_resp.status_code} - {email_resp.text}")
            if email_resp.ok:
                emails = email_resp.json()
                primary_email = next((email for email in emails if email['primary']), None)
                if primary_email:
                    user_info['email'] = primary_email['email']
        
        # Create or update user
        user = create_or_update_user('github', str(user_info['id']), user_info)
        
        # Log in the user
        login_user(user)
        
        # Store the token
        blueprint.token = token
        
        # Redirect to the next URL or home
        next_url = session.pop("next_url", "/")
        return redirect(next_url)

    @oauth_error.connect
    def google_error(blueprint, error, error_description=None, error_uri=None):
        msg = f"OAuth error: {error} - {error_description} - {error_uri}"
        logger.error(msg)
        print(msg)  # Also print to console
        return redirect(url_for('auth_page'))

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('auth_page'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_next_navigation_url(request):
    is_navigation_url = request.headers.get('Sec-Fetch-Mode') == 'navigate' and request.headers.get('Sec-Fetch-Dest') == 'document'
    if is_navigation_url:
        return request.url
    return request.referrer or request.url

oauth_session = LocalProxy(lambda: g.flask_dance_oauth)