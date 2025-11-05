# Quick Deployment Steps

## ✅ Step 1: Edit .env File

Open `.env` in your editor and add your API keys:

```env
GROQ_API_KEY=your_actual_groq_key_here
GOOGLE_API_KEY=your_actual_google_key_here
```

## ✅ Step 2: Deploy

You have two options:

### Option A: Use the Deployment Script (Recommended)
```powershell
.\deploy.ps1
```

### Option B: Manual Deployment
```powershell
# Build and start services
docker-compose up --build -d

# View logs to see progress
docker-compose logs -f server
```

## ✅ Step 3: Verify Deployment

1. **Health Check:**
   ```powershell
   curl http://localhost:8000/
   ```
   Or open in browser: http://localhost:8000/

2. **API Documentation:**
   Open in browser: http://localhost:8000/docs

## ✅ Step 4: Check Status

```powershell
# View service status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f server
docker-compose logs -f db
```

## Troubleshooting

If you see errors:
- Check that API keys are correct in `.env`
- Check logs: `docker-compose logs -f`
- Verify ports 8000 and 5432 are not in use
- Make sure Docker Desktop is running

## Stop Services

When you want to stop:
```powershell
docker-compose down
```

## Restart Services

```powershell
docker-compose restart
```

