# Fly.io Deployment - Quick Start

Deploy PromptBoost on Fly.io - **100% Free** with PostgreSQL!

## Prerequisites ✅

- [ ] Fly.io account (sign up at [fly.io](https://fly.io) - no credit card needed!)
- [ ] Fly CLI installed
- [ ] Code pushed to GitHub
- [ ] Groq API key
- [ ] Google API key

## Step 1: Install Fly CLI (1 min)

**Windows (PowerShell):**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

## Step 2: Login (30 sec)

```bash
fly auth login
```

Opens browser to authenticate.

## Step 3: Create Database (2 min)

```bash
fly postgres create --name promptboost-db --region iad --vm-size shared-cpu-1x --volume-size 3
```

Wait 2-3 minutes for it to create.

## Step 4: Initialize App (1 min)

```bash
fly launch --name promptboost --region iad
```

**When prompted:**
- PostgreSQL: **No** (we already created it)
- Redis: **No**
- Deploy now: **No** (we'll configure first)

## Step 5: Attach Database (30 sec)

```bash
fly postgres attach promptboost-db -a promptboost
```

This automatically sets DATABASE_URL!

## Step 6: Set API Keys (1 min)

```bash
fly secrets set GROQ_API_KEY="your_groq_api_key"
fly secrets set GOOGLE_API_KEY="your_google_api_key"
fly secrets set PROJECT_NAME="PromptBoost"
fly secrets set PROJECT_DESCRIPTION="Prompt Enhancement Service"
```

## Step 7: Deploy (2 min)

```bash
fly deploy
```

Wait for build to complete!

## Step 8: Get Your URL

```bash
fly status
```

Your API will be at:
```
https://promptboost.fly.dev
```

## Step 9: Verify ✅

1. Visit `https://promptboost.fly.dev/`
   - Should see: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. Visit `https://promptboost.fly.dev/docs`
   - Interactive API documentation

## That's It! 🎉

Your API is live and **completely FREE**!

### Your API URL
```
https://promptboost.fly.dev
```

## Free Tier Includes

✅ 3 shared VMs
✅ 3GB storage per VM  
✅ PostgreSQL database (3GB)
✅ 160GB data transfer
✅ Automatic HTTPS
✅ **No credit card required!**

## Common Commands

```bash
# View logs
fly logs

# Check status
fly status

# Restart app
fly apps restart promptboost

# View secrets
fly secrets list
```

## Troubleshooting

**Build fails?**
- Check logs: `fly logs`
- Verify ML models are in Git
- Check environment variables: `fly secrets list`

**Can't connect?**
- Wait for deployment (2-5 min)
- Check service status: `fly status`
- Verify database attached: `fly postgres list`

For detailed guide, see [FLY_DEPLOYMENT.md](FLY_DEPLOYMENT.md)
