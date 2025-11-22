# SmartFixer API Endpoints Documentation

## Complete List of API Endpoints

### Authentication Endpoints
- `POST /api/login` - Login with email/username and password
- `POST /api/signup` - Create new user account
- `GET /auth/google` - Initiate Google OAuth login
- `GET /auth/github` - Initiate GitHub OAuth login
- `GET /auth/google/callback` - Google OAuth callback handler
- `GET /auth/github/callback` - GitHub OAuth callback handler
- `GET /logout` - Logout current user

### AI-Powered Endpoints
- `POST /api/detect-language` - Detect programming language from code
- `POST /api/dictionary` - Get code templates/dictionary for a term
- `POST /api/translate` - Translate code from one language to another
- `POST /api/review` - Review code for errors, warnings, and suggestions
- `POST /api/explain` - Explain code based on user role (student, professor, developer, etc.)
- `POST /api/question` - Answer questions about code using AI
- `POST /api/execute` - Compile and execute code (Python, JavaScript, Java, C, C++)

### Post Endpoints
- `GET /api/posts` - Get user's posts
- `POST /api/posts` - Create a new post
- `POST /api/posts/<post_id>/like` - Like/unlike a post
- `POST /api/posts/<post_id>/save` - Save/unsave a post
- `GET /api/posts/<post_id>/comments` - Get comments for a post
- `POST /api/posts/<post_id>/comment` - Comment on a post
- `POST /api/share-post` - Share a post with another user

### Notification Endpoints
- `GET /api/notifications` - Get user notifications
- `GET /api/notifications/unread-count` - Get unread notification count
- `POST /api/notifications/read-all` - Mark all notifications as read

### Follow System Endpoints
- `POST /api/follow/request` - Send a follow request
- `POST /api/follow/accept` - Accept a follow request
- `POST /api/follow/reject` - Reject a follow request
- `POST /api/follow-user` - Follow/unfollow a user

### Profile Endpoints
- `POST /api/update-profile` - Update user profile (name, bio, profession)
- `POST /api/update-location` - Update user location
- `POST /api/update-location-display` - Update location display preference
- `POST /api/upload-profile-pic` - Upload profile picture
- `GET /api/user-stats` - Get user statistics (posts, followers, following)
- `GET /api/user/<user_id>/posts` - Get posts by a specific user
- `GET /api/user/<user_id>/saved-posts` - Get saved posts by a user
- `GET /api/user/<user_id>/liked-posts` - Get liked posts by a user
- `GET /api/user/<user_id>/stats` - Get detailed user statistics
- `GET /api/user/<user_id>/time-spent` - Get user time spent statistics

### Chat Endpoints
- `GET /api/messages/<user_id>` - Get messages with a specific user
- `POST /api/send-message` - Send a message (supports text, code, files)
- `POST /api/upload-file` - Upload file for chat (images, videos, documents)
- `GET /api/chats/unread-count` - Get unread chat message count
- `GET /api/friends` - Get list of friends/followed users for chat

### User Search Endpoints
- `GET /api/search-users` - Search users by username/name
- `GET /api/search-users-chat` - Search users for chat

### Presence/Status Endpoints
- `GET /api/user-presence/<user_id>` - Get user online status
- `GET /api/user-status/<user_id>` - Get user status (alias for presence)

### Explore Endpoints
- `GET /api/explore-posts` - Get posts from followed users for explore page

### Time Tracker Endpoints
- `POST /api/time-tracker/update` - Update time spent on the platform
- `GET /api/time-tracker/stats` - Get time tracker statistics (total time, streaks)

### Call Endpoints
- `POST /api/call/voice` - Initiate voice call
- `POST /api/call/video` - Initiate video call
- `POST /api/call/accept` - Accept a call
- `POST /api/call/reject` - Reject a call

### File Extraction Endpoints
- `POST /api/extract-code-from-image` - Extract code from uploaded image using OCR
- `POST /api/extract-code-from-pdf` - Extract code from uploaded PDF

## WebSocket Events

### Client → Server
- `join` - Join a room (user room, chat room)
- `user_activity` - Update user activity/presence
- `disconnect` - User disconnects

### Server → Client
- `receive_message` - New message received
- `new_notification` - New notification received
- `user_presence_update` - User presence status updated
- `user_joined` - User joined a room
- `call_request` - Incoming call request
- `call_accepted` - Call was accepted
- `call_rejected` - Call was rejected

## Summary of Fixes

### 1. Authentication ✅
- Fixed Google OAuth routes and callback handlers
- Fixed GitHub OAuth routes and callback handlers
- Added proper error handling for OAuth failures

### 2. Dictionary Feature ✅
- Implemented `/api/dictionary` endpoint
- Integrated with AI code generation for code templates
- Returns code snippets based on search terms

### 3. Translator Feature ✅
- Fixed `/api/translate` endpoint
- Implemented automatic language detection
- Integrated with CodeT5 for code translation
- Fallback to pattern-based translation if AI models unavailable

### 4. Review and Explain Code ✅
- Fixed `/api/review` endpoint with AI integration
- Fixed `/api/explain` endpoint with role-based explanations
- Integrated CodeBERT and CodeT5 for code review
- Added fallback pattern-based review

### 5. Compile Code ✅
- Fixed `/api/execute` endpoint
- Added support for Python, JavaScript, Java, C, C++
- Proper error handling and timeout management
- Returns both output and error messages

### 6. Chat System ✅
- Implemented real-time chat with Socket.IO
- Fixed file upload endpoint (`/api/upload-file`)
- Enabled code, image, video, and document sharing
- Real-time message delivery via WebSocket
- Proper room management for chat

### 7. Online Status ✅
- Implemented 5-minute grace period for offline status
- Real-time presence updates via WebSocket
- Status indicators show "Online" or "was online X min ago"

### 8. Calls in Chat ✅
- Implemented voice and video call endpoints
- Real-time call requests via WebSocket
- Call accept/reject functionality
- Proper call ID management

### 9. Notifications ✅
- Fixed real-time notification system
- Follow request notifications with accept/reject
- Like, comment, and reply notifications
- Real-time delivery via WebSocket
- Unread count tracking

### 10. Profile and Personal Details ✅
- Fixed profile update endpoint (`/api/update-profile`)
- Fixed location update and display (`/api/update-location`)
- Profile picture upload (`/api/upload-profile-pic`)
- Location display on user profile

### 11. My Posts ✅
- Fixed post creation API (`POST /api/posts`)
- Posts display correctly under "My Posts"
- Posts linked to user ID properly

### 12. Time Tracker System ✅
- Implemented time tracking endpoints
- Real-time time updates
- Streak calculations (current, longest, shortest)
- Total time tracking

## AI Models Integration

All AI features use open-source models that run locally:

1. **GPT4All** - Code generation and explanation
2. **fastText** - Language detection (with pattern-based fallback)
3. **CodeT5** - Code translation
4. **CodeBERT** - Code review and analysis
5. **FAISS** - Semantic search (with keyword fallback)

All models have fallback mechanisms if models are not available, ensuring the platform works even without AI models installed.

## Testing Recommendations

1. Test OAuth login with Google and GitHub
2. Test code compilation for all supported languages
3. Test real-time chat with file sharing
4. Test notification system with follow requests
5. Test time tracker with real-time updates
6. Test voice/video call initiation
7. Test profile updates and location display
8. Test post creation and display

## Notes

- All endpoints require authentication except OAuth callbacks
- WebSocket connections require authentication
- File uploads are limited to reasonable sizes
- Code execution has a 10-second timeout
- Online status has a 5-minute grace period before showing offline

