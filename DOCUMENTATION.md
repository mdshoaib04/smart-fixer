# SmartFixer - Technical Documentation

## Overview

SmartFixer is a Flask-based web application that leverages Google's Gemini AI to provide intelligent code review, explanation, and analysis services. The platform features a modern, interactive code editor with real-time collaboration capabilities, allowing users to upload or write code and receive AI-powered feedback tailored to their profession (student, professor, software engineer, etc.). The application includes social features like code sharing, posts, comments, and messaging between users.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Problem**: Need a modern, responsive code editing interface with syntax highlighting and real-time collaboration.

**Solution**: CodeMirror-based editor with Socket.IO for real-time features, supporting multiple programming languages with automatic detection.

**Key Components**:
- CodeMirror editor with VS Code-style interface
- Multi-language syntax highlighting (Python, JavaScript, Java, C++, etc.)
- Real-time WebSocket communication via Socket.IO
- Theme toggle (dark/light mode) with CSS custom properties
- Responsive design with 3D card animations
- Client-side language detection for uploaded files

**Design Patterns**:
- Session storage for temporary code/language data transfer between pages
- Event-driven architecture for real-time messaging
- CSS variable theming for instant theme switching

### Backend Architecture

**Problem**: Need robust user authentication, database management, and AI integration for code analysis.

**Solution**: Flask application with SQLAlchemy ORM, Flask-Login/Flask-Dance for OAuth, and Google Gemini AI integration.

**Core Components**:

1. **Application Structure** (`app.py`):
   - Flask app with SQLAlchemy integration
   - ProxyFix middleware for handling proxy headers
   - Database connection pooling with pre-ping health checks
   - Automatic table creation on startup

2. **Authentication System** (`oauth_auth.py`):
   - Custom OAuth2 consumer blueprint for SmartFixer authentication
   - Session-based storage with browser session key tracking
   - Flask-Login integration for user session management
   - Support for Google and GitHub OAuth providers

3. **Routing & Real-time** (`routes.py`):
   - RESTful API endpoints for code operations
   - Socket.IO integration for real-time messaging and notifications
   - Protected routes with `@require_login` decorator
   - Pygments integration for server-side syntax highlighting

4. **AI Integration** (`gemini_helper.py`):
   - Google Gemini 2.0 Flash model for code review and explanation
   - Profession-aware context adjustment (student, professor, engineer, etc.)
   - Structured prompts for consistent AI responses

**Alternatives Considered**:
- OpenAI API was specifically excluded per requirements
- Chose Gemini for cost-effectiveness and latest model features

### Data Storage

**Problem**: Need to persist user data, OAuth tokens, code history, social interactions, and messages.

**Solution**: SQLAlchemy with relational database schema supporting users, posts, comments, likes, messages, and code history.

**Database Schema**:

1. **Users Table**:
   - UUID-based primary keys
   - Profile information (name, email, image, bio)
   - Profession field for context-aware AI responses
   - Timestamps for account tracking

2. **OAuth Table**:
   - Token storage per user/browser session/provider
   - Unique constraint on user_id + browser_session_key + provider
   - Supports multiple OAuth providers per user

3. **Posts & Social Features**:
   - Posts with code snippets, language, and descriptions
   - PostLike junction table with unique constraints
   - Comments with post relationships
   - Cascade deletes for data integrity

4. **Code History**:
   - Version tracking for user code submissions
   - Linked to user accounts

5. **Messaging System**:
   - Messages with sender/receiver relationships
   - Notifications for user updates

**Database Configuration**:
- Connection pooling with 300-second recycle
- Pre-ping enabled for connection health checks
- Track modifications disabled for performance

**Pros**:
- Relational integrity with foreign keys and cascades
- Flexible OAuth storage supporting multiple providers
- Scalable social features architecture

**Cons**:
- No database migrations system currently implemented
- May need optimization for high-volume messaging

### Authentication & Authorization

**Problem**: Secure user authentication with OAuth support and session management across browser sessions.

**Solution**: Flask-Dance OAuth integration with custom session storage tracking browser-specific tokens.

**Implementation**:
- OAuth tokens stored per user AND browser session
- Unique constraint prevents token conflicts
- LoginManager handles user session lifecycle
- Session made permanent for persistence

**Security Considerations**:
- Session secret from environment variable
- ProxyFix for proper HTTPS header handling
- OAuth token isolation by browser session

## External Dependencies

### Third-party Services

1. **Google Gemini API** (Required):
   - Model: `gemini-2.0-flash-exp`
   - Purpose: Code review, explanation, and AI-powered features
   - Configuration: `GEMINI_API_KEY` environment variable
   - Integration: `google.genai` client library

2. **OAuth Providers**:
   - Replit OAuth (primary authentication)
   - Google OAuth (secondary option)
   - GitHub OAuth (secondary option)

### Python Libraries

**Core Framework**:
- Flask: Web framework
- Flask-SQLAlchemy: ORM integration
- Flask-Login: Session management
- Flask-Dance: OAuth consumer framework
- Flask-SocketIO: WebSocket support

**Database**:
- SQLAlchemy: ORM and database toolkit
- Database driver (PostgreSQL recommended based on DATABASE_URL pattern)

**AI & Processing**:
- google-genai: Gemini API client
- Pygments: Syntax highlighting

**Utilities**:
- Werkzeug: WSGI utilities including ProxyFix
- python-socketio: WebSocket implementation
- PyJWT: Token handling

### Frontend Libraries (CDN-based)

- CodeMirror 5.65.2: Code editor with language modes
- Socket.IO 4.5.4: Client-side WebSocket library
- Multiple CodeMirror language modes (Python, JavaScript, C-like, HTML, CSS, Ruby, PHP, Swift, Go, Rust, SQL, R, Shell)

### Environment Variables

Required configuration:
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string
- `GEMINI_API_KEY`: Google Gemini API authentication
- OAuth credentials for authentication providers

### Database Requirements

- PostgreSQL (or compatible SQL database)
- SQLAlchemy-compatible connection string format
- Support for connection pooling and health checks

## Recent Changes

### Project Completion (October 10, 2025)

**Status**: ✅ Fully functional and ready for deployment

**Implemented Features**:
1. ✅ Complete login/signup page with Google and GitHub authentication
2. ✅ Upload or Write Code page with file upload support and VS Code-style editor
3. ✅ Main editor interface with all features:
   - VS Code-style code editor with syntax highlighting for 20+ languages
   - AI-powered Review, Explain, and Compile functions
   - Automatic language detection
   - Profession-based context switching
   - Dark/Light mode toggle
   - Real-time chat and messaging
   - Profile system with posts, friends, notifications
   - Code history tracking
   - Code translation between languages
   - Comprehensive code dictionary
   - GitHub-style time contribution grid
4. ✅ Social features: posts, likes, comments, friend system
5. ✅ Real-time messaging with code snippet sharing
6. ✅ 3D animations and responsive design
7. ✅ Full mobile optimization

**All Files Created**:
- Backend: `app.py`, `main.py`, `routes.py`, `replit_auth.py`, `gemini_helper.py`, `models.py`
- Templates: `login.html`, `upload_or_write.html`, `editor.html`, `403.html`
- Static: `static/css/style.css`, `static/js/editor.js`
- Documentation: `README.md`, `.gitignore`

**Database**: All tables created successfully (Users, OAuth, Posts, Comments, Friendships, Messages, Groups, Notifications, CodeHistory, TimeSpent)

**Server**: Running successfully on port 5000 with SocketIO support

**Styling**: No changes to original design - all colors, positions, and styling maintained as specified