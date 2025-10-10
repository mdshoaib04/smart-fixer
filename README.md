# Smart Code Reviewer 🚀

A comprehensive AI-powered code review platform with social features, built with Flask and Google Gemini AI.

## ✨ Features

### Page 1: Login/Signup
- **Authentication**: Sign in with Google or GitHub using Replit Auth
- **Beautiful UI**: Modern 3D animated background with gradient effects
- **Responsive Design**: Works perfectly on all devices

### Page 2: Upload or Write Code
- **Upload Code**: Support for all major programming languages (.py, .js, .java, .cpp, .cs, .ts, .rb, .php, .swift, .go, .rs, .kt, .scala, etc.)
- **Write Code**: VS Code-style inline editor with syntax highlighting
- **Auto Language Detection**: Automatically detects programming language from uploaded files or written code

### Page 3: Main Interface

#### Left Panel
- **Profession Selector**: Choose your role (Student, Professor, Frontend, Backend, Software Engineer, Data Scientist, DevOps, Competitive Programmer)
- **VS Code Editor**: Full-featured code editor with syntax highlighting for 20+ languages
- **Action Buttons**:
  - **Review**: Get AI-powered code review with quality assessment, bug detection, security concerns, and performance suggestions
  - **Explain**: Get detailed step-by-step explanation of your code
  - **Compile**: Check for syntax errors, logic errors, runtime errors, and expected output

#### Right Panel
- **AI Output Frame**: DeepSeek.ai-style typing animation showing AI responses line-by-line
- **Profile Logo**: Click to access your profile (shows initials in a circle)
- **Dark/Light Mode Toggle**: Instant theme switching for the entire website
- **Chat/Messenger Icon**: Real-time messaging with friends and code sharing

#### Top Menu (3-Dot Menu)
- **Dictionary**: Access coding templates for all languages
  - Logic Templates
  - Data Structures & Algorithms
  - Practical Code Snippets
- **Translate Code**: Convert code between any programming languages with search functionality
- **Code History**: View all your past code reviews, explanations, and compilations

#### Profile Features
- **Personal Details**: Name, email, profile picture, bio, profession
- **Posts**: Share your code with the community, get likes and comments
- **Friends**: Add friends by email, manage friend requests
- **Notifications**: Accept/deny friend requests, view activity
- **Time Spent**: GitHub-style contribution grid showing daily activity with purple blocks

#### Chat/Messenger
- **Direct Messaging**: Chat with friends
- **Code Sharing**: Send code snippets in messages
- **Group Chat**: Create and join group conversations
- **Real-time Updates**: Powered by Socket.IO

#### Quick Q&A
- **Ask Questions**: Get instant answers about your code from AI
- **Context-Aware**: Questions are answered based on your current code

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **Google Gemini AI**: AI-powered code analysis (gemini-2.0-flash-exp model)
- **PostgreSQL**: Database for users, posts, friends, messages, code history
- **Flask-SocketIO**: Real-time communication
- **Replit Auth**: OAuth authentication with Google/GitHub
- **Pygments**: Syntax highlighting and language detection

### Frontend
- **HTML5/CSS3/JavaScript**
- **CodeMirror**: Professional code editor
- **Socket.IO**: Real-time messaging
- **Custom CSS**: 3D animations, responsive design, smooth transitions

## 🎨 Design Features

- **3D Animated Cards**: Hover effects with realistic depth
- **Smooth Transitions**: All interactions are animated
- **Responsive Layout**: Mobile-friendly vertical layout
- **Dark/Light Theme**: Instant theme switching
- **Modern UI**: Clean, minimal, futuristic design
- **Professional Editor**: VS Code-style interface with keyboard shortcuts

## 📦 Installation & Setup

### Prerequisites
- Python 3.11
- PostgreSQL database (automatically configured in Replit)
- Google Gemini API Key

### Required Packages
All packages are already installed:
- flask
- flask-sqlalchemy
- flask-dance
- flask-login
- flask-socketio
- python-socketio
- gunicorn
- pygments
- werkzeug
- pyjwt
- oauthlib
- google-genai
- eventlet
- psycopg2-binary

### Environment Variables
The following are already configured:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session encryption key
- `REPL_ID`: Replit project ID (for OAuth)

## 🚀 Running the Application

The application is already running! Just click the "Run" button or execute:

```bash
python main.py
```

The server will start on `http://0.0.0.0:5000`

## 📝 How to Use

1. **Login**: Click "Sign in with Google" or "Sign in with GitHub"
2. **Choose Option**: Upload a code file OR write code in the editor
3. **Select Profession**: Choose your role to get context-aware AI responses
4. **Analyze Code**: Use Review, Explain, or Compile buttons
5. **View Results**: Watch AI responses appear with typing animation
6. **Ask Questions**: Use the Q&A box for specific questions
7. **Share Code**: Post your code to the community
8. **Connect**: Add friends and chat with code snippets
9. **Translate**: Convert code between any programming languages
10. **Track Progress**: View your contribution grid

## 🌐 Supported Languages

Python, JavaScript, Java, C++, C, C#, Ruby, PHP, Swift, TypeScript, Go, Kotlin, Rust, Scala, Perl, Dart, Haskell, MATLAB, R, SQL, Shell, Objective-C, and more!

## 🎯 Key Features

- ✅ AI-powered code review and explanation
- ✅ Automatic language detection
- ✅ Code translation between languages
- ✅ Social features (posts, likes, comments)
- ✅ Friend system with real-time chat
- ✅ Code sharing and collaboration
- ✅ GitHub-style contribution tracking
- ✅ Professional code editor
- ✅ Dark/Light mode
- ✅ Fully responsive design
- ✅ 3D animations and transitions
- ✅ Comprehensive code dictionary
- ✅ Code history tracking

## 🔒 Security

- OAuth authentication with Google/GitHub
- Secure session management
- Environment variable protection for API keys
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with HTML escaping

## 📱 Mobile Support

The application is fully responsive with:
- Vertical layout on mobile devices
- Touch-friendly buttons
- Optimized editor for mobile screens
- Adaptive navigation

## 🎨 Customization

- **Theme**: Toggle between dark and light modes
- **Profession**: Select your role for personalized AI responses
- **Editor Theme**: Monokai (dark) or Eclipse (light)

## 📊 Database Schema

- **Users**: Profile information, profession, bio
- **Posts**: User-shared code with likes and comments
- **Friendships**: User connections and friend requests
- **Messages**: Direct and group messaging
- **CodeHistory**: Track all code operations
- **TimeSpent**: Daily activity tracking
- **Notifications**: Friend requests and activity updates

## 🔮 Future Enhancements

The platform is designed to be future-ready with support for:
- Additional AI models
- More programming languages
- Advanced code analytics
- Team collaboration features
- Code playground integration

## 📄 License

This project is ready for deployment and production use!

---

**Built with ❤️ using Flask, Google Gemini AI, and modern web technologies**
