# SmartFixer - AI-Powered Code Review Platform

🚀 **An intelligent code analysis and collaboration platform built with Flask and Google Gemini AI**

---

## 🌟 Overview

SmartFixer is a comprehensive AI-powered code review and social coding platform that helps developers improve their programming skills through intelligent analysis, real-time collaboration, and community interaction. Built with modern web technologies and powered by Google's Gemini AI, it provides professional-grade code analysis tailored to different skill levels and programming roles.

## ⚡ Quick Start

### 1. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or use the setup script
python setup.py
```

### 2. Configure Environment
Create a `.env` file with your configuration:

```env
# Database Configuration (SQLite by default)
DATABASE_URL=sqlite:///smartfixer.db

# Security
SESSION_SECRET=your-secure-random-key-here

# AI Integration (Choose one provider)
GEMINI_API_KEY=your-gemini-api-key
# OPENAI_API_KEY=your-openai-api-key
# HUGGINGFACE_API_KEY=your-huggingface-api-key
# DEEPSEEK_API_KEY=your-deepseek-api-key
# OPENROUTER_API_KEY=your-openrouter-api-key
```

### 3. Run Application
```bash
# Direct method
python app.py

# Or using the launcher
python main.py
```

Access SmartFixer at:
- **Local**: http://localhost:5000
- **Network**: http://[your-ip]:5000

## 🛠️ Technology Stack

### Backend Architecture
- **Flask**: Modern Python web framework with RESTful API design
- **SQLAlchemy**: Advanced ORM with SQLite database integration
- **Flask-Login**: Secure user session management
- **Flask-SocketIO**: Real-time WebSocket communication for instant messaging and presence updates
- **Google Gemini AI**: State-of-the-art AI model for code analysis
- **OAuth Integration**: Secure authentication with Google and GitHub

### Frontend Technologies
- **CodeMirror**: Professional code editor with syntax highlighting
- **Socket.IO**: Real-time bidirectional communication
- **Responsive CSS**: Mobile-first design with modern styling

## 📁 Project Structure

```
SmartFixer/
├── app.py                 # Main Flask application
├── database.py           # Database configuration and models
├── models.py             # SQLAlchemy database models
├── oauth_auth.py         # OAuth authentication system
├── gemini_helper.py      # Google Gemini AI integration
├── ai_helper.py          # AI abstraction layer
├── routes.py             # API routes and endpoints
├── main.py               # Application entry point
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
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

## 🔧 Getting Your API Keys

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new project or select existing one
3. Generate API key and add to your `.env` file
4. **Free tier**: 60 requests per minute

## 🎯 Key Features

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
