# Quick Start Guide

Get PromptBoost up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- API keys for Groq and Google (for Gemini fallback)

## Step 1: Set Up Environment

Copy the environment template and fill in your API keys:

**On Linux/Mac:**
```bash
cp env.template .env
```

**On Windows (PowerShell):**
```powershell
Copy-Item env.template .env
```

Then edit `.env` and add your API keys:
- `GROQ_API_KEY` - Get from https://console.groq.com/
- `GOOGLE_API_KEY` - Get from https://makersuite.google.com/app/apikey

## Step 2: Deploy

### Option A: Using the Deployment Script (Linux/Mac)

```bash
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual Deployment

```bash
# Build and start services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f server
```

## Step 3: Verify

1. **Health Check:**
   ```bash
   curl http://localhost:8000/
   ```
   Should return: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. **API Documentation:**
   Open http://localhost:8000/docs in your browser

## That's It! 🎉

Your server is now running. The API is available at:
- **Base URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up --build -d
```

## Troubleshooting

### Port Already in Use
Change `SERVER_PORT` in `.env` to a different port (e.g., 8001)

### Database Connection Issues
Check database logs: `docker-compose logs db`

### API Key Errors
Verify your API keys in `.env` are correct and have proper permissions

For more details, see [DEPLOYMENT.md](DEPLOYMENT.md)
