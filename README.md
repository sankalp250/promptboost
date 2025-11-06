# PromptBoost

An AI-powered prompt enhancement tool that helps users improve their prompts for better AI interactions.

## Features

- 🤖 **AI-Powered Enhancement** - Uses Groq/Gemini to enhance prompts
- 📋 **Clipboard Integration** - Trigger enhancement with `!!e` suffix
- ✅ **Feedback System** - Accept/reject enhancements to improve quality
- 🎯 **Quality Filter** - ML model predicts enhancement acceptance probability
- 🔄 **Retry Mechanism** - Automatically retries if quality is low
- 📊 **Analytics** - Tracks usage and feedback for continuous improvement

## Quick Start

### Local Deployment

1. **Copy environment template:**
   ```bash
   # Linux/Mac
   cp env.template .env
   
   # Windows
   Copy-Item env.template .env
   ```

2. **Edit `.env` and add your API keys**

3. **Deploy:**
   ```bash
   # Linux/Mac
   ./deploy.sh
   
   # Windows
   .\deploy.ps1
   
   # Or manually
   docker-compose up --build -d
   ```

4. **Verify:**
   - Health check: http://localhost:8000/
   - API docs: http://localhost:8000/docs

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

### Deploy to Fly.io (Public Access) ⭐ Recommended - FREE!

Deploy your API to Fly.io - **100% free** with PostgreSQL included:

1. **Follow the [Fly.io Quick Start Guide](FLY_QUICK_START.md)** (5 minutes)
2. **Get your public API URL** (e.g., `https://your-app.fly.dev`)
3. **Update client configuration** (see [CLIENT_SETUP.md](CLIENT_SETUP.md))

**Quick Fly.io Steps:**
- Install Fly CLI
- Create PostgreSQL database
- Launch your app
- Set environment variables
- Deploy!

**Why Fly.io?**
- ✅ **100% Free** - No credit card required
- ✅ **PostgreSQL Included** - Free database
- ✅ **Docker Support** - Uses your existing Dockerfile
- ✅ **Automatic HTTPS** - SSL included
- ✅ **3 Shared VMs** - Generous free tier

See [FLY_DEPLOYMENT.md](FLY_DEPLOYMENT.md) for complete instructions.

### Alternative Hosting Options

See [FREE_HOSTING_OPTIONS.md](FREE_HOSTING_OPTIONS.md) for other free alternatives.

## Architecture

### Server (FastAPI)
- RESTful API for prompt enhancement
- LangGraph workflow for LLM integration
- PostgreSQL database for caching and analytics
- ML model for quality prediction

### Client (Windows Desktop App)
- System tray application
- Clipboard monitoring
- Dialog-based feedback system
- Hotkey support

## Project Structure

```
promptboost/
├── server/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration
│   │   ├── database/      # Database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Business logic
│   │   └── ml_models/     # Trained ML models
│   ├── alembic/           # Database migrations
│   └── main.py            # FastAPI app
├── enhancer_client/        # Windows desktop client
├── scripts/                # Utility scripts
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── .env                    # Environment variables
```

## API Endpoints

- `GET /` - Health check
- `POST /api/v1/enhance` - Enhance a prompt
- `POST /api/v1/feedback` - Submit feedback

See full documentation at `/docs` when server is running.

## Development

### Local Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r server/requirements.txt
   pip install -r enhancer_client/requirements.txt
   ```

3. **Set up database:**
   ```bash
   # Create .env file with DATABASE_URL
   python scripts/create_db.py
   alembic upgrade head
   ```

4. **Train ML models:**
   ```bash
   python scripts/train_preference_model.py
   ```

5. **Run server:**
   ```bash
   cd server
   uvicorn main:app --reload
   ```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:
- Docker deployment
- Production considerations
- Cloud platform deployment
- Troubleshooting

## Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Project Summary](PROJECT_SUMMARY.md) - Detailed feature overview

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
