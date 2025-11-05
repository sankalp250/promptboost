# Deploy PromptBoost on Render

This guide will help you deploy PromptBoost on Render.com so it's accessible to everyone.

## Prerequisites

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub/GitLab Repository** - Your code should be in a Git repository
3. **API Keys** ready:
   - Groq API Key: https://console.groq.com/
   - Google API Key: https://makersuite.google.com/app/apikey

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub/GitLab

Make sure your code is pushed to a Git repository:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `promptboost-db`
   - **Database**: `promptboost`
   - **User**: `promptboost`
   - **Plan**: Choose based on your needs (Free tier available for testing)
4. Click **"Create Database"**
5. **Important**: Copy the **Internal Database URL** - you'll need this

### Step 3: Create Web Service on Render

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your Git repository
3. Configure the service:

#### Basic Settings:
- **Name**: `promptboost-server`
- **Environment**: Select **"Docker"**
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or `./` if needed)

#### Build & Deploy:
- **Dockerfile Path**: `Dockerfile` (should be in root)
- **Docker Context**: `.` (root directory)

#### Environment Variables:
Add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `[From PostgreSQL service]` | Use the Internal Database URL from Step 2 |
| `GROQ_API_KEY` | `your_groq_api_key` | Your actual Groq API key |
| `GOOGLE_API_KEY` | `your_google_api_key` | Your actual Google API key |
| `PROJECT_NAME` | `PromptBoost` | (Optional) |
| `PROJECT_DESCRIPTION` | `Prompt Enhancement Service` | (Optional) |

**To get DATABASE_URL:**
1. Go to your PostgreSQL service
2. Under "Connections", find "Internal Database URL"
3. Copy it and paste as `DATABASE_URL` value

#### Advanced Settings:
- **Health Check Path**: `/`
- **Auto-Deploy**: `Yes` (deploys on every push)

4. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- Render will build your Docker image (first build takes 5-10 minutes)
- It will automatically run migrations
- You can watch the build logs in real-time

### Step 5: Verify Deployment

Once deployed, your service will have a URL like:
```
https://promptboost-server.onrender.com
```

1. **Health Check**: Visit `https://your-app-name.onrender.com/`
   - Should return: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. **API Documentation**: Visit `https://your-app-name.onrender.com/docs`
   - Interactive Swagger UI should be available

3. **Test API**: Try the enhance endpoint via the docs

## Using render.yaml (Alternative Method)

If you prefer infrastructure-as-code, you can use the `render.yaml` file:

1. Push `render.yaml` to your repository
2. In Render Dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will automatically detect `render.yaml` and create both services

**Note**: You'll still need to set environment variables manually in the dashboard.

## Important Notes

### Free Tier Limitations

⚠️ **Render Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds (cold start)
- Limited to 750 hours/month
- 100GB bandwidth/month

**For Production Use:**
- Consider upgrading to a paid plan ($7/month for Starter)
- Ensures 24/7 availability
- No spin-down delays
- More resources

### Database Connection

- Render provides `DATABASE_URL` automatically for PostgreSQL services
- Use the **Internal Database URL** (not External)
- The entrypoint script automatically detects Render environment

### ML Models

Make sure your ML models are committed to the repository:
- `server/app/ml_models/preference_model.joblib`
- `server/app/ml_models/tfidf_vectorizer.joblib`

If they're in `.gitignore`, remove them temporarily or use Git LFS.

### Environment Variables Security

- Never commit `.env` files
- All secrets should be set in Render dashboard
- Use Render's environment variable management

## Updating Your Deployment

### Automatic Updates
If Auto-Deploy is enabled, push to your repository:
```bash
git push origin main
```
Render will automatically rebuild and redeploy.

### Manual Updates
1. Go to your service in Render Dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

## Monitoring

### View Logs
1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. View real-time logs

### Check Metrics
- View CPU, Memory, and Request metrics in the dashboard
- Set up alerts for errors

## Troubleshooting

### Build Failures

1. **Check Build Logs:**
   - Go to your service → "Logs" tab
   - Look for error messages

2. **Common Issues:**
   - Missing ML models: Make sure they're committed to Git
   - Database connection: Verify DATABASE_URL is correct
   - API keys: Ensure they're set correctly

### Migration Failures

If migrations fail:
1. Check database logs
2. Verify DATABASE_URL format
3. Try running migrations manually (SSH into service if available)

### Service Not Starting

1. Check logs for errors
2. Verify all environment variables are set
3. Check health check endpoint
4. Verify port binding (Render uses PORT env var)

### Database Connection Issues

1. Verify DATABASE_URL uses Internal Database URL
2. Check database service is running
3. Verify database credentials

## Making It Public

Once deployed, your API will be accessible at:
```
https://your-app-name.onrender.com
```

### Update Client Application

Update your client application's API URL:
```python
# In enhancer_client/enhancer/config.py or .env
API_BASE_URL=https://your-app-name.onrender.com/api/v1
```

### CORS Configuration (if needed)

If you need to allow requests from specific domains, add CORS middleware to `server/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Cost Estimation

### Free Tier
- **Web Service**: Free (with limitations)
- **PostgreSQL**: Free (with limitations)
- **Total**: $0/month

### Starter Plan (Recommended for Production)
- **Web Service**: $7/month
- **PostgreSQL**: $7/month
- **Total**: $14/month

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test the API endpoints
3. ✅ Update client application with new API URL
4. ✅ Share the API URL with users
5. ✅ Monitor usage and performance

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Check Render status: https://status.render.com

---

**Your PromptBoost API will be live and accessible to everyone!** 🚀
