# Railway Deployment - Quick Start

Get your PromptBoost API live on Railway in 5 minutes!

## Prerequisites ✅

- [ ] Railway account (sign up at [railway.app](https://railway.app))
- [ ] Code pushed to GitHub/GitLab
- [ ] Groq API key
- [ ] Google API key

## Step 1: Create Project (1 min)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway auto-detects your Dockerfile! ✅

## Step 2: Add PostgreSQL (1 min)

1. In your project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Done! Railway creates it automatically ✅

## Step 3: Set Environment Variables (2 min)

1. Click on your **Web Service**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Click PostgreSQL service → Copy `DATABASE_URL` |
| `GROQ_API_KEY` | `your_actual_groq_key` |
| `GOOGLE_API_KEY` | `your_actual_google_key` |
| `PROJECT_NAME` | `PromptBoost` |
| `PROJECT_DESCRIPTION` | `Prompt Enhancement Service` |

**Tip**: For DATABASE_URL, you can also use:
- Click PostgreSQL service
- Copy the `DATABASE_URL` value
- Paste it in your web service variables

## Step 4: Deploy (1 min)

That's it! Railway automatically:
- ✅ Builds your Docker image
- ✅ Runs migrations
- ✅ Starts your service
- ✅ Assigns a public URL

## Step 5: Get Your URL

1. Click on your **Web Service**
2. Go to **"Settings"** tab
3. Under **"Domains"**, you'll see your URL
4. Or click **"Generate Domain"** for a custom subdomain

Your API will be at:
```
https://your-app-name.up.railway.app
```

## Step 6: Verify ✅

1. Visit `https://your-app-name.up.railway.app/`
   - Should see: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. Visit `https://your-app-name.up.railway.app/docs`
   - Interactive API documentation

## Step 7: Update Client

Edit `enhancer_client/.env` or `enhancer_client/enhancer/config.py`:
```
API_BASE_URL=https://your-app-name.up.railway.app/api/v1
```

## That's It! 🎉

Your API is now publicly accessible!

### Your API URL
```
https://your-app-name.up.railway.app
```

### API Endpoints
- Health: `https://your-app-name.up.railway.app/`
- Docs: `https://your-app-name.up.railway.app/docs`
- Enhance: `https://your-app-name.up.railway.app/api/v1/enhance`
- Feedback: `https://your-app-name.up.railway.app/api/v1/feedback`

## Railway Benefits

✅ **No Database Limit** - Can have multiple databases
✅ **Better Free Tier** - $5/month credit
✅ **Automatic HTTPS** - SSL included
✅ **Simpler Setup** - Fewer steps
✅ **Auto-Deploy** - Deploys on every push

## Troubleshooting

**Build fails?**
- Check logs in Railway dashboard
- Verify ML models are committed to Git
- Check environment variables are set

**Can't connect?**
- Wait for first deployment (2-5 min)
- Check service is running
- Verify DATABASE_URL is correct

**Migrations fail?**
- Check DATABASE_URL format
- Verify database service is running
- Check logs for specific error

## Next Steps

- [ ] Test all API endpoints
- [ ] Update client application
- [ ] Share API URL with users
- [ ] Monitor usage in Railway dashboard

For detailed guide, see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
