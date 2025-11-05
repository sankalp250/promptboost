# Deploy PromptBoost on Railway

This guide will help you deploy PromptBoost on Railway.app so it's accessible to everyone.

## Why Railway?

- ✅ **Generous Free Tier** - $5/month credit, perfect for small projects
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Easy PostgreSQL** - One-click database setup
- ✅ **Simple Deployment** - Just connect your repo
- ✅ **No Credit Card Required** for free tier

## Prerequisites

1. **Railway Account** - Sign up at [railway.app](https://railway.app)
2. **GitHub/GitLab Repository** - Your code should be in a Git repository
3. **API Keys** ready:
   - Groq API Key: https://console.groq.com/
   - Google API Key: https://makersuite.google.com/app/apikey

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

Make sure your code is pushed to a Git repository:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create New Project on Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will automatically detect your Dockerfile

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically:
   - Create the database
   - Generate connection string
   - Link it to your service

### Step 4: Configure Environment Variables

1. Click on your **Web Service** in Railway
2. Go to **"Variables"** tab
3. Add these environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Railway automatically provides this! |
| `GROQ_API_KEY` | `your_groq_api_key` | Your actual Groq API key |
| `GOOGLE_API_KEY` | `your_google_api_key` | Your actual Google API key |
| `PROJECT_NAME` | `PromptBoost` | (Optional) |
| `PROJECT_DESCRIPTION` | `Prompt Enhancement Service` | (Optional) |

**Important**: For `DATABASE_URL`, Railway provides a reference variable:
- Click on the PostgreSQL service
- Copy the `DATABASE_URL` variable
- Or use `${{Postgres.DATABASE_URL}}` in your web service variables

### Step 5: Deploy

Railway will automatically:
- Build your Docker image
- Run database migrations (via entrypoint script)
- Start your service
- Assign a public URL

### Step 6: Get Your Public URL

1. Click on your **Web Service**
2. Go to **"Settings"** tab
3. Under **"Domains"**, you'll see your public URL
4. Or click **"Generate Domain"** to get a custom subdomain

Your API will be available at:
```
https://your-app-name.up.railway.app
```

### Step 7: Verify Deployment

1. **Health Check**: Visit `https://your-app-name.up.railway.app/`
   - Should return: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. **API Documentation**: Visit `https://your-app-name.up.railway.app/docs`
   - Interactive Swagger UI should be available

3. **Test API**: Try the enhance endpoint via the docs

## Using railway.json (Optional)

The `railway.json` file provides configuration for Railway:
- Build settings
- Docker configuration
- Deploy settings

Railway will automatically use this file if present.

## Important Notes

### Free Tier

✅ **Railway Free Tier:**
- $5/month credit (enough for small projects)
- PostgreSQL database included
- Automatic HTTPS
- Custom domains supported
- No credit card required

**For Production:**
- Monitor usage in dashboard
- Upgrade to paid plan if needed
- $5 credit usually covers light usage

### Database Connection

- Railway automatically provides `DATABASE_URL` when you add PostgreSQL
- The connection string is automatically injected
- Use `${{Postgres.DATABASE_URL}}` in variables to reference it

### ML Models

Make sure your ML models are committed to the repository:
- `server/app/ml_models/preference_model.joblib`
- `server/app/ml_models/tfidf_vectorizer.joblib`

If they're in `.gitignore`, remove them temporarily or use Git LFS.

### Environment Variables

- Never commit `.env` files
- All secrets should be set in Railway dashboard
- Railway encrypts all environment variables

## Updating Your Deployment

### Automatic Updates

Railway automatically deploys when you push to your repository:
```bash
git push origin main
```

Railway will:
- Detect changes
- Rebuild if needed
- Deploy automatically

### Manual Deploy

1. Go to your service in Railway Dashboard
2. Click **"Deploy"** → **"Redeploy"**

## Monitoring

### View Logs

1. Click on your service
2. Go to **"Deployments"** tab
3. Click on a deployment to see logs
4. Or use **"Logs"** tab for real-time logs

### Metrics

- View CPU, Memory, and Network usage
- Check deployment history
- Monitor database usage

## Troubleshooting

### Build Failures

1. **Check Build Logs:**
   - Go to your service → "Deployments"
   - Click on failed deployment
   - View build logs

2. **Common Issues:**
   - Missing ML models: Make sure they're committed to Git
   - Database connection: Verify DATABASE_URL is set
   - API keys: Ensure they're set correctly

### Migration Failures

If migrations fail:
1. Check deployment logs
2. Verify DATABASE_URL format
3. Check database service is running
4. Try redeploying

### Service Not Starting

1. Check logs for errors
2. Verify all environment variables are set
3. Check health check endpoint
4. Verify port binding (Railway uses PORT env var)

### Database Connection Issues

1. Verify DATABASE_URL is set correctly
2. Check database service is running
3. Verify database credentials
4. Check if database is linked to web service

## Making It Public

Once deployed, your API will be accessible at:
```
https://your-app-name.up.railway.app
```

### Update Client Application

Update your client application's API URL:
```python
# In enhancer_client/enhancer/config.py or .env
API_BASE_URL=https://your-app-name.up.railway.app/api/v1
```

### Custom Domain (Optional)

1. Go to your service → "Settings"
2. Under "Domains", click "Custom Domain"
3. Add your domain
4. Follow DNS configuration instructions

## Cost Estimation

### Free Tier (Hobby)
- **Web Service**: Included in $5 credit
- **PostgreSQL**: Included in $5 credit
- **Total**: Free (up to $5/month usage)

### Paid Plans
- **Developer**: $5/month (if you exceed free credit)
- **Pro**: $20/month (more resources)

## Advantages Over Render

✅ **No Database Limit** - Can have multiple databases on free tier
✅ **Better Free Tier** - $5 credit vs limited hours
✅ **Automatic HTTPS** - No configuration needed
✅ **Simpler Setup** - Fewer steps required
✅ **Better Documentation** - More detailed guides

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Test the API endpoints
3. ✅ Update client application with new API URL
4. ✅ Share the API URL with users
5. ✅ Monitor usage and performance

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway status: https://status.railway.app

---

**Your PromptBoost API will be live and accessible to everyone!** 🚀
