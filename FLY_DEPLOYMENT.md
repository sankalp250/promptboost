# Deploy PromptBoost on Fly.io

Fly.io offers a **generous free tier** with PostgreSQL support! Perfect for hosting PromptBoost.

## Why Fly.io?

- ✅ **Free Tier Available** - 3 shared VMs, 3GB storage
- ✅ **PostgreSQL Included** - Free PostgreSQL database
- ✅ **No Credit Card Required** - For free tier
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Global Edge Network** - Fast worldwide
- ✅ **Docker Support** - Uses your existing Dockerfile

## Prerequisites

1. **Fly.io Account** - Sign up at [fly.io](https://fly.io) (no credit card needed for free tier)
2. **Fly CLI** - Install from [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl)
3. **GitHub/GitLab Repository** - Your code should be in a Git repository
4. **API Keys** ready:
   - Groq API Key: https://console.groq.com/
   - Google API Key: https://makersuite.google.com/app/apikey

## Step-by-Step Deployment

### Step 1: Install Fly CLI

**Windows (PowerShell):**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Or use installer:**
- Download from: https://fly.io/docs/hands-on/install-flyctl/

### Step 2: Login to Fly.io

```bash
fly auth login
```

This will open your browser to authenticate.

### Step 3: Create PostgreSQL Database

```bash
fly postgres create --name promptboost-db --region iad --vm-size shared-cpu-1x --volume-size 3
```

**Options:**
- `--name`: Database name (change if needed)
- `--region`: Choose closest region (iad, ord, dfw, etc.)
- `--vm-size`: `shared-cpu-1x` is free tier
- `--volume-size`: 3GB is free tier

Wait for the database to be created (takes 2-3 minutes).

### Step 4: Initialize Your App

In your project directory:

```bash
fly launch --name promptboost --region iad
```

**When prompted:**
- **App name**: `promptboost` (or any name)
- **Region**: Choose closest to you
- **PostgreSQL**: Say **No** (we already created it)
- **Redis**: Say **No**
- **Deploy now**: Say **Yes** (we'll configure first)

### Step 5: Attach Database to App

```bash
fly postgres attach promptboost-db -a promptboost
```

This automatically sets the `DATABASE_URL` secret for your app! ✅

### Step 6: Set Environment Variables

```bash
# Set API keys
fly secrets set GROQ_API_KEY="your_groq_api_key"
fly secrets set GOOGLE_API_KEY="your_google_api_key"

# Optional
fly secrets set PROJECT_NAME="PromptBoost"
fly secrets set PROJECT_DESCRIPTION="Prompt Enhancement Service"
```

**Note**: DATABASE_URL is automatically set when you attach the database!

### Step 7: Deploy

```bash
fly deploy
```

Fly.io will:
- Build your Docker image
- Run migrations (via entrypoint script)
- Deploy your app
- Assign a public URL

### Step 8: Get Your Public URL

```bash
fly status
```

Or check your app dashboard at: https://fly.io/dashboard

Your API will be at:
```
https://promptboost.fly.dev
```

### Step 9: Verify Deployment

1. **Health Check**: Visit `https://promptboost.fly.dev/`
   - Should return: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. **API Documentation**: Visit `https://promptboost.fly.dev/docs`
   - Interactive Swagger UI should be available

## Using fly.toml

The `fly.toml` file is already configured for your app. It includes:
- Docker build configuration
- HTTP service settings
- Health checks
- Auto-start/stop (free tier feature)

## Free Tier Details

### What's Included
- ✅ 3 shared-cpu VMs
- ✅ 3GB storage per VM
- ✅ 160GB outbound data transfer
- ✅ PostgreSQL database (3GB storage)
- ✅ Automatic HTTPS

### Limitations
- Machines may sleep after inactivity (wake on first request)
- Shared CPU resources
- Limited to 3GB storage

### Upgrade Options
- **Hobby**: $1.94/month per VM (better performance)
- **Pro**: $5/month per VM (dedicated resources)

## Managing Your App

### View Logs
```bash
fly logs
```

### Check Status
```bash
fly status
```

### Scale (if needed)
```bash
fly scale count 1
```

### Restart
```bash
fly apps restart promptboost
```

### SSH into App
```bash
fly ssh console
```

### View Secrets
```bash
fly secrets list
```

## Troubleshooting

### Build Failures

1. **Check Build Logs:**
   ```bash
   fly logs
   ```

2. **Common Issues:**
   - Missing ML models: Make sure they're committed to Git
   - Database connection: Verify DATABASE_URL is set
   - API keys: Ensure they're set correctly

### Migration Failures

If migrations fail:
```bash
# SSH into app
fly ssh console

# Run migrations manually
cd /app
alembic -c alembic.ini upgrade head
```

### Service Not Starting

1. Check logs: `fly logs`
2. Verify environment variables: `fly secrets list`
3. Check health endpoint
4. Verify database is attached

### Database Connection Issues

1. Verify database is attached:
   ```bash
   fly postgres list
   fly postgres attach promptboost-db -a promptboost
   ```

2. Check DATABASE_URL:
   ```bash
   fly secrets list
   ```

3. Test connection:
   ```bash
   fly postgres connect -a promptboost-db
   ```

## Updating Your Deployment

### Automatic Updates

1. Push to your repository:
   ```bash
   git push origin main
   ```

2. Redeploy:
   ```bash
   fly deploy
   ```

### Manual Deploy

```bash
fly deploy
```

## Cost

### Free Tier
- **App**: Free (3 shared VMs)
- **PostgreSQL**: Free (3GB storage)
- **Total**: **$0/month** ✅

### If You Need More
- **Hobby Plan**: ~$2-6/month
- **Pro Plan**: ~$5-15/month

## Making It Public

Once deployed, your API will be accessible at:
```
https://promptboost.fly.dev
```

### Update Client Application

Update your client application's API URL:
```python
# In enhancer_client/enhancer/config.py or .env
API_BASE_URL=https://promptboost.fly.dev/api/v1
```

### Custom Domain (Optional)

1. Add your domain in Fly.io dashboard
2. Update DNS records
3. Fly.io automatically provisions SSL

## Advantages

✅ **Truly Free** - No credit card required
✅ **PostgreSQL Included** - No separate database service needed
✅ **Global Network** - Fast worldwide
✅ **Docker Support** - Uses your existing setup
✅ **Auto HTTPS** - SSL included
✅ **Simple CLI** - Easy to manage

## Next Steps

1. ✅ Deploy to Fly.io
2. ✅ Test the API endpoints
3. ✅ Update client application with new API URL
4. ✅ Share the API URL with users
5. ✅ Monitor usage in Fly.io dashboard

## Support

- Fly.io Documentation: https://fly.io/docs
- Fly.io Community: https://community.fly.io
- Check Fly.io status: https://status.fly.io

---

**Your PromptBoost API will be live and accessible to everyone - completely free!** 🚀
