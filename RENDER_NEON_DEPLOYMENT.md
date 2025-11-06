# Render Deployment with Neon Database - Step by Step Guide

## Prerequisites
- ✅ Your Neon database URL: `postgresql://neondb_owner:npg_yh5RA4VkMfCW@ep-lucky-flower-ah8vs80k-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
- ✅ Your code pushed to GitHub
- ✅ Render account (free tier works)

---

## Step 1: Push Your Code to GitHub

1. **Make sure your code is committed:**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```
   *(Or use your main branch name - master/main/etc.)*

---

## Step 2: Create Render Account & New Web Service

1. **Go to Render:** https://render.com
2. **Sign up/Login** (you can use GitHub to sign in)
3. **Click "New +"** button (top right)
4. **Select "Web Service"**

---

## Step 3: Connect Your GitHub Repository

1. **Click "Connect GitHub"** or "Connect Repository"
2. **Authorize Render** to access your GitHub (if first time)
3. **Search for your repository** (`promptboost` or whatever it's named)
4. **Click "Connect"** next to your repository

---

## Step 4: Configure Your Web Service

Fill in these fields **EXACTLY**:

### Basic Settings:
- **Name:** `promptboost-server` (or any name you like)
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main` (or your main branch name)
- **Root Directory:** Leave **EMPTY** (or put `.` if required)

### Build & Deploy:
- **Runtime:** `Docker`
- **Dockerfile Path:** `./Dockerfile` (should auto-detect)
- **Docker Context:** `.` (dot = root directory)

### Plan:
- **Plan:** `Free` (for testing) or `Starter` ($7/month)

---

## Step 5: Set Environment Variables

**This is the MOST IMPORTANT step!**

Click **"Advanced"** → **"Add Environment Variable"** and add these **ONE BY ONE**:

### 1. DATABASE_URL
- **Key:** `DATABASE_URL`
- **Value:** `postgresql://neondb_owner:npg_yh5RA4VkMfCW@ep-lucky-flower-ah8vs80k-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
- **Click "Save"**

### 2. GROQ_API_KEY
- **Key:** `GROQ_API_KEY`
- **Value:** `your-groq-api-key-here` (paste your actual key)
- **Click "Save"**

### 3. GOOGLE_API_KEY
- **Key:** `GOOGLE_API_KEY`
- **Value:** `your-google-api-key-here` (paste your actual key)
- **Click "Save"**

### 4. PROJECT_NAME (Optional)
- **Key:** `PROJECT_NAME`
- **Value:** `PromptBoost`
- **Click "Save"**

### 5. PROJECT_DESCRIPTION (Optional)
- **Key:** `PROJECT_DESCRIPTION`
- **Value:** `Prompt Enhancement Service`
- **Click "Save"**

---

## Step 6: Deploy!

1. **Scroll down** and click **"Create Web Service"**
2. **Wait for deployment** (takes 5-10 minutes first time)
3. **Watch the logs** - you should see:
   - ✅ Building Docker image
   - ✅ Installing dependencies
   - ✅ Running migrations: `alembic upgrade head`
   - ✅ Starting server: `uvicorn main:app`

---

## Step 7: Verify Deployment

1. **Check the logs** for any errors (red text)
2. **Click on your service URL** (looks like: `https://promptboost-server.onrender.com`)
3. **You should see:** `{"status": "ok", "message": "Welcome to PromptBoost"}`

---

## Step 8: Test Your API

Your API will be available at:
- **Base URL:** `https://your-service-name.onrender.com`
- **Health Check:** `https://your-service-name.onrender.com/`
- **Enhance Endpoint:** `https://your-service-name.onrender.com/api/v1/enhance`
- **Feedback Endpoint:** `https://your-service-name.onrender.com/api/v1/feedback`

---

## Troubleshooting

### ❌ Build Fails
- **Check:** Dockerfile path is correct (`./Dockerfile`)
- **Check:** All files are committed to GitHub
- **Check:** Logs for specific error messages

### ❌ Database Connection Error
- **Check:** DATABASE_URL is set correctly (copy-paste from Neon)
- **Check:** No extra spaces in the environment variable
- **Check:** Your Neon database is active (not paused)

### ❌ Migration Fails
- **Check:** DATABASE_URL is correct
- **Check:** Database exists in Neon
- **Check:** Logs for specific Alembic errors

### ❌ App Crashes on Start
- **Check:** All environment variables are set (GROQ_API_KEY, GOOGLE_API_KEY)
- **Check:** PORT is automatically set by Render (don't set it manually)
- **Check:** Logs for Python errors

### ❌ 502 Bad Gateway
- **Wait 2-3 minutes** - free tier services spin down after inactivity
- **Check:** Service is running (green status in Render dashboard)
- **Check:** Health check endpoint responds

---

## Important Notes

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds
   - 750 hours/month free (enough for 24/7 if you're the only user)

2. **Database Migrations:**
   - Migrations run automatically on every deploy (via docker-entrypoint.sh)
   - If migration fails, deployment will fail (good for safety!)

3. **Environment Variables:**
   - Never commit `.env` file to GitHub
   - Always set secrets in Render dashboard
   - Changes to env vars require redeploy

4. **Updating Your App:**
   - Just push to GitHub → Render auto-deploys
   - Or click "Manual Deploy" in Render dashboard

---

## Quick Checklist

Before deploying, make sure:
- [ ] Code is pushed to GitHub
- [ ] DATABASE_URL is copied correctly from Neon
- [ ] GROQ_API_KEY is set
- [ ] GOOGLE_API_KEY is set
- [ ] Dockerfile exists in root directory
- [ ] docker-entrypoint.sh exists and is executable

---

## That's It! 🎉

Your app should now be live on Render using your Neon database!

