# SmartFixer - AI-Powered Code Review Platform

🚀 **An intelligent code analysis and collaboration platform built with Flask and Google Gemini AI**

---

## 🌟 Overview

SmartFixer is a comprehensive AI-powered code review and social coding platform that helps developers improve their programming skills through intelligent analysis, real-time collaboration, and community interaction. Built with modern web technologies and powered by Google's Gemini AI, it provides professional-grade code analysis tailored to different skill levels and programming roles.

## ✨ Key Features

### 🤖 AI-Powered Code Analysis
- **Smart Code Review**: Comprehensive analysis covering code quality, bugs, security vulnerabilities, and performance optimization
- **Intelligent Explanations**: Step-by-step code explanations adapted to your profession and skill level
- **Compilation Simulation**: Advanced error detection and runtime analysis
- **Multi-Language Support**: 20+ programming languages with automatic detection
- **Code Translation**: Convert code between different programming languages
- **Interactive Q&A**: Ask specific questions about your code and get instant AI responses

### 💻 Professional Code Editor
- **VS Code-Style Interface**: Full-featured editor with syntax highlighting and IntelliSense-like features
- **File Upload Support**: Direct upload for all major programming file types
- **Theme Toggle**: Seamless dark/light mode switching
- **Code Templates**: Built-in dictionary with templates for all supported languages
- **Real-time Collaboration**: Share code snippets instantly with team members

### 👥 Social Coding Platform
- **Developer Profiles**: Personalized profiles with bio, profession, and coding statistics
- **Code Sharing**: Post code snippets with descriptions and get community feedback
- **Social Interactions**: Like, comment, and discuss code with other developers
- **Friend System**: Connect with developers and build your coding network
- **Real-time Messaging**: Chat with friends and share code snippets instantly
- **Activity Notifications**: Stay updated with friend requests, comments, and interactions
- **Real-time Presence**: See when friends are online, recently active, or last seen

### 📊 Progress Tracking
- **GitHub-Style Activity Grid**: Visual representation of daily coding activity
- **Time Analytics**: Track time spent coding and platform engagement
- **Coding Streaks**: Monitor consistency and build productive habits
- **Code History**: Complete history of all your code analysis and submissions

### 🎯 Profession-Aware AI
- **Student Mode**: Educational explanations with learning-focused feedback
- **Professor Mode**: Academic insights and teaching-oriented analysis
- **Developer Specializations**: Frontend, Backend, Full-Stack, DevOps, Data Science
- **Competitive Programming**: Algorithm optimization and performance analysis

## 🛠️ Technology Stack

### Backend Architecture
- **Flask**: Modern Python web framework with RESTful API design
- **SQLAlchemy**: Advanced ORM with PostgreSQL database integration
- **Flask-Login**: Secure user session management
- **Flask-SocketIO**: Real-time WebSocket communication for instant messaging and presence updates
- **Google Gemini AI**: State-of-the-art AI model for code analysis (gemini-2.0-flash-exp)
- **OAuth Integration**: Secure authentication with Google and GitHub

### Frontend Technologies
- **CodeMirror**: Professional code editor with syntax highlighting for 20+ languages
- **Socket.IO**: Real-time bidirectional communication
- **Responsive CSS**: Mobile-first design with modern 3D animations
- **Theme System**: Dynamic dark/light mode with CSS custom properties

### Database Design
- **User Management**: Comprehensive profile and authentication system
- **Social Features**: Posts, comments, likes, and friend relationships
- **Real-time Messaging**: Scalable chat system with message history
- **Code Analytics**: Complete tracking of code submissions and AI analysis
- **Activity Monitoring**: Time tracking and progress analytics

## 📋 Prerequisites

Before setting up SmartFixer, ensure you have:

- **Python 3.11+** (Latest stable version recommended)
- **PostgreSQL Database** (Local or cloud-hosted)
- **Google Gemini API Key** (Free tier available)
- **OAuth Credentials** (Google/GitHub - optional but recommended)

## ⚡ Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/smartfixer.git
cd smartfixer
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/smartfixer

# Security
SESSION_SECRET=your-secure-random-key-here

# AI Integration
GEMINI_API_KEY=your-gemini-api-key

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 3. Database Setup
```bash
# Database tables are created automatically on first run
python app.py
```

### 4. Launch Application
```bash
python app.py
```

Access SmartFixer at:
- **Local**: http://localhost:5000
- **Network**: http://[your-ip]:5000

## 🎯 Getting Your API Keys

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new project or select existing one
3. Generate API key and add to your `.env` file
4. **Free tier**: 60 requests per minute

### OpenAI API (Alternative)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Add to your `.env` file as `OPENAI_API_KEY`

### Hugging Face API (Alternative)
1. Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens)
2. Create a new token with read access
3. Add to your `.env` file as `HUGGINGFACE_API_KEY`

### DeepSeek API (Alternative)
1. Visit [DeepSeek Platform](https://platform.deepseek.com/apiKeys)
2. Create an account and generate an API key
3. Add to your `.env` file as `DEEPSEEK_API_KEY`

### OpenRouter API (Alternative)
1. Visit [OpenRouter Settings](https://openrouter.ai/settings/keys)
2. Create an account and generate an API key
3. Add to your `.env` file as `OPENROUTER_API_KEY`

## 🔧 Multiple AI Provider Support

SmartFixer now supports multiple AI providers through a unified abstraction layer:

### Configuration
Configure your preferred AI provider in the `.env` file:

```env
# Choose ONE provider by uncommenting the appropriate key

# For Gemini (Google AI Studio) - Default
GEMINI_API_KEY=your_gemini_api_key_here

# For OpenAI (ChatGPT)
# OPENAI_API_KEY=your_openai_api_key_here

# For Hugging Face
# HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# For DeepSeek
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# For OpenRouter
# OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Provider Features
- **Gemini**: Google's most capable AI model, excellent for code analysis
- **OpenAI**: Industry-standard models with consistent performance
- **Hugging Face**: Access to thousands of open-source models
- **DeepSeek**: High-performance models with competitive pricing
- **OpenRouter**: Single API access to 100+ models from different providers

### Switching Providers
To switch between providers:
1. Comment out the current provider's API key
2. Uncomment and add your new provider's API key
3. Restart the application

All AI features will work seamlessly with any configured provider.

## 📁 Project Structure

```
SmartFixer/
├── app.py                 # Main Flask application
├── database.py           # Database configuration and models
├── models.py             # SQLAlchemy database models
├── oauth_auth.py         # OAuth authentication system
├── gemini_helper.py      # Google Gemini AI integration
├── routes.py             # API routes and endpoints
├── main.py               # Application entry point
├── templates/            # HTML templates
│   ├── welcome.html      # Landing page
│   ├── auth.html         # Authentication page
│   ├── upload_or_write.html  # Code input interface
│   ├── editor.html       # Main code editor
│   ├── profile.html      # User profiles
│   ├── posts.html        # Social feed
│   ├── explore.html      # Content discovery
│   ├── notifications.html # Activity notifications
│   ├── time_tracker.html # Progress tracking
│   └── chat.html         # Real-time messaging
├── static/
│   ├── css/
│   │   ├── style.css     # Main stylesheet
│   │   ├── posts.css     # Social features styling
│   │   ├── profile.css   # Profile page styling
│   │   ├── explore.css   # Discovery page styling
│   │   ├── chat.css      # Chat interface styling
│   │   └── time_tracker.css # Activity grid styling
│   └── js/
│       └── editor.js     # Frontend JavaScript
└── requirements.txt      # Python dependencies
```

## 🎨 User Interface Features

### Design Philosophy
- **Clean & Modern**: Minimalist interface focused on productivity
- **Responsive Design**: Seamless experience across all devices
- **3D Animations**: Engaging hover effects and smooth transitions
- **Theme Consistency**: Unified color scheme with instant theme switching
- **Professional Editor**: VS Code-inspired interface with keyboard shortcuts

### Supported Programming Languages

**Web Technologies:** HTML, CSS, JavaScript, TypeScript, PHP
**Backend Languages:** Python, Java, C#, Ruby, Go, Rust, Node.js
**Systems Programming:** C, C++, Objective-C
**Mobile Development:** Swift, Kotlin, Dart (Flutter)
**Data Science:** R, MATLAB, Scala
**Functional Programming:** Haskell, F#
**Scripting:** Shell/Bash, PowerShell, Perl
**Database:** SQL, MongoDB Query Language

## 🔧 API Documentation

### Authentication Endpoints
```
POST /api/login          # User authentication
POST /api/signup         # User registration
GET  /logout             # User logout
```

### AI Analysis Endpoints
```
POST /api/review         # Comprehensive code review
POST /api/explain        # Code explanation
POST /api/compile        # Compilation and error checking
POST /api/question       # Interactive Q&A
POST /api/detect-language # Automatic language detection
POST /api/translate      # Code translation between languages
```

### Social Platform Endpoints
```
GET  /api/posts          # Get user posts feed
POST /api/posts          # Create new code post
POST /api/posts/<id>/like # Like/unlike posts
GET  /api/posts/<id>/comments # Get post comments
POST /api/posts/<id>/comment  # Add comment to post
```

### User Management
```
GET  /api/profile        # Get user profile data
POST /api/update-profile # Update profile information
POST /api/update-profession # Change profession setting
POST /api/track-time     # Log activity time
```

### Friend System
```
GET  /api/friends        # Get friends list
POST /api/friend-request # Send friend request
POST /api/accept-friend  # Accept friend request
POST /api/remove-friend  # Remove friend
```

## 🚀 Advanced Usage

### Professional Code Review
1. **Upload or Write Code**: Use the integrated editor or upload files
2. **Select Your Profession**: Choose your role for tailored AI responses
3. **Get AI Analysis**: Click Review for comprehensive code analysis
4. **Interactive Learning**: Ask follow-up questions about your code
5. **Share & Collaborate**: Post interesting code snippets to the community

### Social Coding Features
1. **Build Your Network**: Connect with other developers
2. **Share Knowledge**: Post code snippets with explanations
3. **Real-time Chat**: Message friends and share code instantly
4. **Track Progress**: Monitor your coding activity and improvement

### Code Translation
1. **Multi-Language Support**: Convert code between any supported languages
2. **Smart Translation**: AI understands context and programming paradigms
3. **Learning Tool**: Compare implementations across different languages

## 🔒 Security Features

- **OAuth 2.0 Authentication**: Secure login with Google and GitHub
- **Session Management**: Secure user sessions with automatic timeout
- **API Key Protection**: Environment variable encryption for sensitive data
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy ORM
- **XSS Protection**: Input sanitization and output encoding
- **HTTPS Ready**: SSL/TLS support for production deployment

## 📱 Mobile Responsiveness

- **Adaptive Layout**: Automatically adjusts to screen size
- **Touch-Friendly Interface**: Optimized buttons and navigation
- **Mobile Code Editor**: Full-featured editing on mobile devices
- **Responsive Navigation**: Collapsible menus and touch gestures

## 🎯 Use Cases

### For Students
- **Learn Best Practices**: Get educational feedback on your code
- **Understand Algorithms**: Step-by-step explanations of complex logic
- **Practice Coding**: Safe environment to experiment and learn
- **Connect with Peers**: Build a network of fellow learning developers

### For Educators
- **Teaching Tool**: Use AI analysis to explain code to students
- **Assignment Review**: Quickly analyze student submissions
- **Code Examples**: Generate and share teaching materials
- **Student Progress**: Track learning progress and engagement

### For Professional Developers
- **Code Quality**: Improve code quality with AI-powered reviews
- **Debugging Assistant**: Identify bugs and performance issues
- **Knowledge Sharing**: Share expertise with the developer community
- **Team Collaboration**: Real-time code sharing and discussion

### For Teams
- **Code Reviews**: Streamline the review process with AI assistance
- **Documentation**: Generate explanations for complex code sections
- **Onboarding**: Help new team members understand existing codebases
- **Best Practices**: Maintain coding standards across the team

## 🔧 Deployment

### Development Environment
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Production Deployment

**Using Gunicorn:**
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

**Using Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

**Environment Considerations:**
- Use PostgreSQL for production database
- Configure Redis for session storage (optional)
- Set up SSL certificates for HTTPS
- Configure proper logging and monitoring

## 🤝 Contributing

We welcome contributions from the developer community!

### How to Contribute
1. **Fork the Repository**: Create your own copy of SmartFixer
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your feature or bug fix
4. **Test Thoroughly**: Ensure all existing functionality works
5. **Submit Pull Request**: Describe your changes and their benefits

### Contribution Guidelines
- Follow PEP 8 coding standards for Python
- Write clear, descriptive commit messages
- Include documentation for new features
- Add unit tests for new functionality
- Ensure mobile responsiveness for UI changes

## 📊 Performance & Analytics

### Built-in Analytics
- **User Activity Tracking**: Monitor engagement and usage patterns
- **Code Analysis Metrics**: Track review frequency and response times
- **Social Interaction Stats**: Measure community engagement
- **Performance Monitoring**: Real-time application performance metrics

### Optimization Features
- **Database Connection Pooling**: Efficient database resource management
- **Caching Strategy**: Redis integration for improved response times
- **CDN Integration**: Fast content delivery for static assets
- **Lazy Loading**: Optimized page load times

## 🎓 Learning Resources

### Getting Started
- **Interactive Tutorial**: Built-in guide for new users
- **Code Examples**: Sample projects in multiple languages
- **Best Practices Guide**: Industry-standard coding conventions
- **AI Prompting Tips**: How to get the best results from AI analysis

### Advanced Features
- **API Integration Guide**: Building applications with SmartFixer API
- **Custom Themes**: Creating and sharing custom editor themes
- **Plugin Development**: Extending SmartFixer functionality
- **Performance Optimization**: Advanced configuration tips

## 📈 Roadmap

### Upcoming Features
- **Team Workspaces**: Collaborative coding environments
- **Code Challenges**: Gamified programming exercises
- **Integration APIs**: Connect with popular development tools
- **Mobile Apps**: Native iOS and Android applications
- **Advanced AI Models**: Support for multiple AI providers
- **Code Review Automation**: Automated pull request analysis

### Long-term Vision
- **AI Pair Programming**: Real-time coding assistance
- **Code Generation**: AI-powered code scaffolding
- **Learning Paths**: Structured programming curricula
- **Enterprise Features**: Advanced team management and analytics

## 🆘 Support & Community

### Get Help
- **Documentation**: Comprehensive guides and API reference
- **Community Forum**: Connect with other SmartFixer users
- **Issue Tracker**: Report bugs and request features
- **Email Support**: Direct assistance for critical issues

### Stay Connected
- **GitHub**: Follow development progress and contribute
- **Blog**: Latest updates and development insights
- **Newsletter**: Monthly updates and feature announcements
- **Social Media**: Join our developer community

## 📄 License

SmartFixer is released under the MIT License. See [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 SmartFixer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **Google Gemini AI**: For providing advanced AI capabilities
- **CodeMirror Team**: For the excellent code editor component
- **Flask Community**: For the robust and flexible web framework
- **Open Source Contributors**: For their valuable contributions and feedback

---

**SmartFixer** - Revolutionizing code review and developer collaboration with AI-powered intelligence. 🚀✨

*Built with passion for the developer community. Happy coding!* 💻❤️
