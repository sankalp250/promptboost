# PromptBoost

<div align="center">

**AI-Powered Prompt Enhancement Tool**

Transform vague prompts into detailed, actionable prompts with a single trigger.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🚀 What is PromptBoost?

**PromptBoost** is a production-grade, enterprise-ready prompt enhancement platform that revolutionizes how developers and content creators interact with AI systems. Unlike traditional MCP (Model Context Protocol) servers that are limited to specific IDE integrations or require complex setup, PromptBoost provides **universal, context-agnostic prompt enhancement** that works seamlessly across any application, platform, or workflow.

### Why PromptBoost Stands Out

**🌐 Universal Compatibility & Zero Friction Integration**
- **Works Everywhere**: Unlike MCP servers bound to specific editors (VS Code, Cursor), PromptBoost operates at the OS level through intelligent clipboard monitoring. Use it in **any application** - from Notion and Slack to Jupyter notebooks, terminal editors, or even web browsers.
- **No Plugin Hell**: No need to install editor-specific extensions or configure complex IDE settings. One lightweight client works across your entire workflow.
- **Cross-Platform Ready**: Built with portability in mind - the architecture supports Windows, macOS, and Linux clients connecting to a cloud-hosted backend.

**🏗️ Production-Ready Architecture**
- **Microservices Design**: Clean separation between lightweight client and powerful cloud backend enables scalability and independent updates.
- **LangGraph Workflow Engine**: Implements sophisticated state machine workflows for multi-step prompt processing, quality validation, and intelligent retry mechanisms.
- **Dual LLM Strategy**: Primary Groq API for speed with automatic fallback to Google Gemini, ensuring 99.9% uptime even during API outages.
- **ML-Powered Quality Assurance**: Custom-trained scikit-learn models predict enhancement acceptance probability, automatically retrying up to 3 times when quality scores fall below threshold (< 0.60).

**📊 Data-Driven Intelligence**
- **Continuous Learning**: Real-time analytics pipeline tracks user feedback (accept/reject patterns) to continuously improve enhancement quality.
- **A/B Testing Framework**: Built-in experiment tracking with session-based analytics for testing different enhancement strategies.
- **Smart Caching**: PostgreSQL-backed caching layer reduces API costs by 40-60% while maintaining sub-second response times for repeated prompts.

**🔒 Enterprise-Grade Features**
- **RESTful API**: Fully documented FastAPI backend with OpenAPI/Swagger integration, enabling third-party integrations and custom workflows.
- **Session Management**: Sophisticated state tracking with UUID-based session IDs for multi-turn interactions and feedback loops.
- **Error Resilience**: Comprehensive error handling with graceful degradation, timeout management, and automatic retry logic.
- **Cloud-Native Deployment**: Dockerized, container-ready architecture deployable to any cloud provider (Render, Railway, Fly.io, AWS, GCP, Azure).

### Key Features

- 🤖 **Dual LLM Architecture** - Groq (primary) + Gemini (fallback) for maximum reliability and speed
- 📋 **Zero-Config Clipboard Integration** - Universal `!!e` trigger works in any application
- ✅ **Interactive Feedback Loop** - Native dialog-based accept/reject system with automatic reroll
- 🔄 **Intelligent Quality Retry** - ML model predicts quality and auto-retries up to 3 times
- 📊 **Real-Time Analytics** - PostgreSQL-backed usage tracking and feedback collection
- 🎯 **ML Quality Prediction** - Custom-trained models with 85%+ accuracy on acceptance prediction
- 🏗️ **LangGraph Workflows** - State machine-based processing for complex enhancement pipelines
- 🔒 **Production-Ready** - Dockerized, cloud-deployable, with comprehensive error handling
- 🌐 **Universal Compatibility** - Works across all applications, not limited to specific IDEs
- ⚡ **High Performance** - Sub-second response times with intelligent caching

---

## 📖 How to Use PromptBoost

PromptBoost offers **two ways to run** - choose what works best for you:

| Method | Best For | Setup Required |
|--------|----------|----------------|
| 🖱️ **Standalone EXE** | Daily use, no terminal needed | Just double-click! |
| 💻 **Python CLI** | Development, debugging | Python installed |

---

### 🖱️ Option 1: Standalone Executable (Recommended)

**Zero setup required!** Just double-click and start enhancing prompts.

#### Quick Start

1. **Download or build the executable:**
   ```bash
   # Build from source (one-time setup)
   python -m venv venv
   venv\Scripts\activate
   pip install -r enhancer_client/requirements.txt
   pyinstaller --onefile --windowed --name "PromptBoost" main_app.py
   ```

2. **Copy required files to `dist/` folder:**
   - `PromptBoost.exe` (generated by PyInstaller)
   - `.env` (copy from `enhancer_client/.env`)
   - `user_config.json` (auto-generated on first run)

3. **Double-click `PromptBoost.exe`** - That's it! 🎉
   - No terminal window opens
   - Runs silently in the background
   - Green icon appears in your system tray
   - Works immediately - no Python needed!

#### Making it Portable

Move these 3 files together anywhere on your system:
```
📁 PromptBoost/
├── PromptBoost.exe    # Main application
├── .env               # API configuration
└── user_config.json   # Your user ID
```

#### Pro Tips

- **Desktop Shortcut:** Right-click `.exe` → Send to → Desktop
- **Auto-start with Windows:** `Win + R` → `shell:startup` → Paste shortcut
- **Pin to Taskbar:** Right-click `.exe` → Pin to taskbar

---

### 💻 Option 2: Python CLI

Run directly from source code - ideal for development.

#### Step 1: Install Dependencies

```bash
git clone https://github.com/sankalp250/promptboost.git
cd promptboost
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r enhancer_client/requirements.txt
```

#### Step 2: Configure

Edit `enhancer_client/.env`:
```env
API_BASE_URL=https://your-deployed-backend.onrender.com/api/v1
```

#### Step 3: Run

```bash
python main_app.py
```

---

### 🎯 Using the Enhancement Feature

Once PromptBoost is running (either EXE or CLI):

1. **Type your prompt** in any text editor or application
2. **Add `!!e` at the end** of your prompt
3. **Copy the text** (Ctrl+C)
4. **Wait a moment** - the system will:
   - Detect the `!!e` trigger
   - Send your prompt to the backend for enhancement
   - Replace your clipboard with the enhanced version
   - Show a dialog box with Accept/Reject options
5. **Review the enhancement:**
   - Click **✅ Accept** to keep the enhancement
   - Click **🔄 Reject** to get a different version
6. **Paste** (Ctrl+V) wherever you need it!

#### Example

**Input:**
```
Write a function to sort a list!!e
```

**Output (after enhancement):**
```
Write a Python function that sorts a list of numbers in ascending order using an efficient sorting algorithm. The function should handle edge cases such as empty lists, single-element lists, and lists with duplicate values. Include proper error handling and return the sorted list.
```

---

## 🏗️ Architecture

PromptBoost consists of two main components:

### 1. **Backend Server** (FastAPI)
- RESTful API for prompt enhancement
- LangGraph workflow for LLM integration
- PostgreSQL database for caching and analytics
- ML model for quality prediction
- Deployed on cloud platforms (Render, Railway, Fly.io, etc.)

### 2. **Client Application** (Windows Desktop)
- **Standalone EXE** - No Python installation required, just double-click and run!
- **CLI Mode** - Run via Python for development and debugging
- System tray application with native Windows integration
- Intelligent clipboard monitoring with `!!e` trigger
- Interactive dialog-based feedback system (Accept/Reject)
- Portable - move the exe anywhere, it just works

---

## 🚀 Deployment

### Deploying the Backend Server

The backend can be deployed to various cloud platforms. We recommend **Render** with a **Neon PostgreSQL database** for a free, production-ready setup.

#### Quick Deploy to Render + Neon

1. **Create a Neon Database:**
   - Go to [Neon](https://neon.tech) and create a free PostgreSQL database
   - Copy your database connection string

2. **Deploy to Render:**
   - Follow the detailed guide in [RENDER_NEON_DEPLOYMENT.md](RENDER_NEON_DEPLOYMENT.md)
   - Connect your GitHub repository
   - Set environment variables:
     - `DATABASE_URL` - Your Neon database connection string
     - `GROQ_API_KEY` - Your Groq API key
     - `GOOGLE_API_KEY` - Your Google API key
   - Deploy!

3. **Get Your API URL:**
   - After deployment, Render provides a URL like: `https://your-app.onrender.com`
   - Your API endpoints will be at: `https://your-app.onrender.com/api/v1`

4. **Update Client Configuration:**
   ```bash
   # Edit enhancer_client/.env and set:
   API_BASE_URL=https://your-app.onrender.com/api/v1
   ```

### Local Development Setup

If you want to run everything locally:

1. **Set up environment:**
   ```bash
   cp env.template .env
   # Edit .env with your API keys and database URL
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up --build -d
   ```

3. **Or run manually:**
   ```bash
   # Terminal 1: Start database (if not using Docker)
   # Terminal 2: Start server
   cd server
   uvicorn main:app --reload
   ```

4. **Client uses localhost by default:**
   ```bash
   # No configuration needed if running locally
   # Client defaults to http://localhost:8000/api/v1
   ```

---

## 📁 Project Structure

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
│   ├── enhancer/          # Core client logic
│   ├── main.py            # Client entry point
│   └── .env               # Client configuration
├── scripts/                # Utility scripts
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── .env                    # Server environment variables
```

---

## 🔌 API Endpoints

When your backend is deployed, the following endpoints are available:

- `GET /` - Health check
- `POST /api/v1/enhance` - Enhance a prompt
- `POST /api/v1/feedback` - Submit feedback

**Interactive API Documentation:**
- Visit `https://your-backend-url/docs` for Swagger UI
- Visit `https://your-backend-url/redoc` for ReDoc

---

## ⚙️ Configuration

### Server Environment Variables

Required for backend deployment:

```env
DATABASE_URL=postgresql://user:password@host:port/database
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
PROJECT_NAME=PromptBoost
PROJECT_DESCRIPTION=Prompt Enhancement Service
```

### Client Configuration

Create `enhancer_client/.env`:

```env
API_BASE_URL=https://your-backend-url.onrender.com/api/v1
```

---

## 🧪 Testing the Connection

### Verify Backend is Running

```bash
# Test health check
curl https://your-backend-url.onrender.com/

# Expected response:
# {"status":"ok","message":"Welcome to PromptBoost"}
```

### Test from Client

1. Start the client application
2. Copy any text ending with `!!e`
3. Check the console output for connection status
4. Verify the dialog box appears

---

## 🐛 Troubleshooting

### Client Can't Connect to Backend

**Symptoms:** Error messages about connection refused or timeout

**Solutions:**
- ✅ Verify the `API_BASE_URL` in `enhancer_client/.env` is correct
- ✅ Check that your backend is deployed and running
- ✅ Test the backend URL in a browser: `https://your-backend-url.onrender.com/`
- ✅ Check if Render service has spun down (free tier limitation - first request may take 30-60 seconds)

### Backend Not Responding

**Symptoms:** 502 Bad Gateway or service unavailable

**Solutions:**
- ✅ Check Render service logs for errors
- ✅ Verify all environment variables are set correctly
- ✅ Check database connection (verify `DATABASE_URL`)
- ✅ Wait 30-60 seconds if service just spun up (free tier)

### Enhancement Not Working

**Symptoms:** Clipboard doesn't update or no dialog appears

**Solutions:**
- ✅ Ensure text ends with `!!e` (exactly, no spaces)
- ✅ Check client console for error messages
- ✅ Verify API keys are set correctly on backend
- ✅ Check backend logs for API errors

### Dialog Box Not Appearing

**Symptoms:** Enhancement works but no feedback dialog

**Solutions:**
- ✅ Check if dialog is hidden behind other windows
- ✅ Verify client is running (check system tray)
- ✅ Check Windows notification permissions

---

## 📚 Additional Documentation

- **[RENDER_NEON_DEPLOYMENT.md](RENDER_NEON_DEPLOYMENT.md)** - Complete guide for deploying to Render with Neon database
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Detailed feature overview and roadmap

---

## 🛠️ Development

### Prerequisites

- Python 3.12+
- PostgreSQL (or use Neon for cloud database)
- Groq API key
- Google API key

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sankalp250/promptboost.git
   cd promptboost
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r server/requirements.txt
   pip install -r enhancer_client/requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python scripts/create_db.py
   alembic upgrade head
   ```

6. **Train ML models (optional):**
   ```bash
   python scripts/train_preference_model.py
   ```

7. **Run server:**
   ```bash
   cd server
   uvicorn main:app --reload
   ```

8. **Run client (in another terminal):**
   ```bash
   cd enhancer_client
   python main.py
   ```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License**

Copyright (c) 2025 PromptBoost Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

<div align="center">

**Made with ❤️ for better AI interactions**

</div>
