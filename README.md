# 🤖 Chatbot Backend - FastAPI & LangChain

> A modern, production-ready baseline for building conversational AI backends

## 🎯 Project Objective

Hey there! 👋 This project was born out of the need for a solid, no-nonsense foundation to build conversational agents. Whether you're creating a customer support bot, a personal assistant, or the next ChatGPT competitor, this codebase gives you everything you need to hit the ground running.

Think of this as your "batteries included" starter kit for AI chatbots - complete with user authentication, conversation persistence, and all the modern bells and whistles you'd expect from a professional-grade backend.

## ✨ What Makes This Special?

- **🚀 Ready to Deploy**: Built with FastAPI for lightning-fast performance
- **🧠 AI-Powered**: Integrated with Google's Gemini AI and LangChain for intelligent conversations
- **🔐 Secure by Design**: JWT authentication, email verification, and proper session management
- **💾 Persistent Memory**: Your bot remembers conversations using PostgreSQL and LangGraph checkpoints
- **📧 Email Magic**: Built-in email services for user verification and notifications
- **🏗️ Production-Ready**: Complete with logging, database migrations, and AWS deployment guide
- **🔄 Real-Time**: Async support for handling multiple conversations simultaneously

## 🛠️ Tech Stack

| Component | Technology | Why We Chose It |
|-----------|------------|-----------------|
| **API Framework** | FastAPI | Blazing fast, automatic API docs, type hints |
| **AI Engine** | LangChain + Google Gemini | Flexible AI orchestration with state-of-the-art LLM |
| **Database** | PostgreSQL + SQLAlchemy | Reliable, scalable, with proper ORM |
| **Authentication** | JWT + Email OTP | Secure and user-friendly |
| **State Management** | LangGraph | Persistent conversation memory |
| **Background Tasks** | FastAPI Background Tasks | Email sending and data processing |
| **Deployment** | AWS (EC2 + API Gateway) | Scalable cloud infrastructure |

## 🚀 Quick Start

### Prerequisites

Make sure you have these installed:
- Python 3.8+ 
- PostgreSQL
- A Google Cloud account (for Gemini API)
- SMTP email credentials

### 1. Clone & Setup

```bash
git clone https://github.com/mazumdarabhishek/chatbot-backend-fastapi-ouath.git
cd chatbot_fastapi
cp .env.example .env  # Create your environment file
```

### 2. Configure Environment

Edit your `.env` file with your credentials:

```env
# Database
database_url=postgresql://username:password@localhost:5432/your_db

# JWT Security
secret_key=your-super-secret-key
algorithm=HS256

# Google Gemini AI
gemini_api_key=your-gemini-api-key
gemini_model=gemini-flash-latest

# Email Configuration
email_host=your-smtp-host
email_port=587
email_from=your-email@domain.com
app_password=your-app-password
```

### 3. Install Dependencies

```bash
cd src
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 5. Launch! 🎉

```bash
uvicorn app.main:app --reload
```

Your API will be running at `http://localhost:8000`

## 📖 API Documentation

Once your server is running, check out:
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
src/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # User authentication & registration
│   │   └── chatbot.py    # Chat endpoints
│   ├── core/             # Core application logic
│   │   ├── config.py     # Configuration management
│   │   ├── database.py   # Database connection
│   │   └── app_logger.py # Logging setup
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Helper functions
├── alembic/              # Database migrations
└── docs/                 # Documentation
```

## 🔧 Key Features Deep Dive

### 🤖 Intelligent Conversations
- **Persistent Context**: Conversations are saved and can be resumed
- **Memory Management**: Smart compression of long conversation histories
- **Multi-User Support**: Each user has isolated conversation threads

### 🔐 Authentication System
- **Email-based Registration**: Users sign up with email verification
- **OTP Security**: Time-limited one-time passwords for secure login
- **JWT Tokens**: Stateless authentication with configurable expiration

### 📊 Session Management
- **Thread-based Conversations**: Each chat session has a unique thread
- **Full Transcript Storage**: Every message is saved with timestamps
- **Session CRUD**: Create, read, update, delete chat sessions

### 🚀 Production Features
- **Async Architecture**: Handle thousands of concurrent users
- **Background Processing**: Email sending doesn't block API responses
- **Comprehensive Logging**: Track everything for debugging and analytics
- **Health Checks**: Monitor your application status

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration with email verification
- `POST /auth/verify-email` - Verify email with OTP
- `POST /auth/login` - User login
- `POST /auth/request-otp` - Request new OTP

### Chatbot
- `POST /chatbot/chat` - Send message to AI (creates new session if no thread_id)
- `POST /chatbot/get_sessions` - Get user's chat sessions (paginated)
- `POST /chatbot/get_transcripts` - Get conversation history
- `DELETE /chatbot/delete_session/{thread_id}` - Delete a chat session

### System
- `GET /health` - Health check endpoint

## 🚀 Deployment

We've included a comprehensive [AWS deployment guide](src/docs/setup_aws_infra.md) that walks you through:
- Setting up a free-tier EC2 instance
- Configuring API Gateway with HTTPS
- Proper security groups and networking
- Systemd service configuration

Perfect for getting your bot live without breaking the bank!

## 🤝 Contributing

Found a bug? Have a cool feature idea? We'd love your contributions!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source - feel free to use it as the foundation for your next big AI project!

## 🎉 What's Next?

This baseline gives you a solid foundation, but the sky's the limit! Here are some ideas for extending it:

- **Multi-modal Support**: Add image and voice message handling
- **Custom AI Models**: Integrate your own fine-tuned models
- **Real-time Chat**: WebSocket support for live conversations
- **Analytics Dashboard**: Track user engagement and conversation metrics
- **Plugin System**: Allow third-party integrations

## 🆘 Need Help?

- Check out the [API documentation](http://localhost:8000/docs) when your server is running
- Review the [AWS deployment guide](src/docs/setup_aws_infra.md) for production setup
- Look at the code - it's well-commented and easy to follow!

---

**Built with ❤️ by WannaBeAIops**

*Happy coding, and may your conversations be ever intelligent! 🤖✨*