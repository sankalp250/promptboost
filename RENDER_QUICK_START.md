# Render Deployment - Quick Start

Get your PromptBoost API live on Render in 10 minutes!

## Prerequisites ✅

- [ ] Render account (sign up at [render.com](https://render.com))
- [ ] Code pushed to GitHub/GitLab
- [ ] Groq API key
- [ ] Google API key

## Step 1: Create PostgreSQL Database (2 min)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Settings:
   - Name: `promptboost-db`
   - Database: `promptboost`
   - Plan: `Free` (or paid for production)
4. Click **"Create Database"**
5. **Copy the Internal Database URL** (you'll need it in Step 3)

## Step 2: Create Web Service (3 min)

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your Git repository
3. Configure:
   - **Name**: `promptboost-server` (or any name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`

## Step 3: Set Environment Variables (2 min)

In the Web Service settings, add these:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | [Paste Internal Database URL from Step 1] |
| `GROQ_API_KEY` | `your_actual_groq_key` |
| `GOOGLE_API_KEY` | `your_actual_google_key` |
| `PROJECT_NAME` | `PromptBoost` |
| `PROJECT_DESCRIPTION` | `Prompt Enhancement Service` |

## Step 4: Deploy (3 min)

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes first time)
3. Your API will be live at: `https://your-app-name.onrender.com`

## Step 5: Verify ✅

1. Visit `https://your-app-name.onrender.com/`
   - Should see: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. Visit `https://your-app-name.onrender.com/docs`
   - Interactive API documentation

## Step 6: Update Client

Edit `enhancer_client/.env` or `enhancer_client/enhancer/config.py`:
```
API_BASE_URL=https://your-app-name.onrender.com/api/v1
```

## That's It! 🎉

Your API is now publicly accessible!

### Your API URL
```
https://your-app-name.onrender.com
```

### API Endpoints
- Health: `https://your-app-name.onrender.com/`
- Docs: `https://your-app-name.onrender.com/docs`
- Enhance: `https://your-app-name.onrender.com/api/v1/enhance`
- Feedback: `https://your-app-name.onrender.com/api/v1/feedback`

## Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Verify ML models are committed to Git
- Check environment variables are set

**Can't connect?**
- Wait for first deployment to complete (can take 5-10 min)
- Check service is running (not paused)
- Verify DATABASE_URL is correct

**Migrations fail?**
- Check DATABASE_URL format
- Verify database service is running
- Check logs for specific error

## Next Steps

- [ ] Test all API endpoints
- [ ] Update client application
- [ ] Share API URL with users
- [ ] Monitor usage in Render dashboard

For detailed guide, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
