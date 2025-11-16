# 🚀 Quick Start Guide - Fixed!

## ✅ Issues Fixed

1. **Import Error Fixed**: The app can now be run from `enhancer_client` directory
2. **API URL Fixed**: Created `.env` file with correct URL format: `https://promptboost-server.onrender.com/api/v1`

## 🎯 How to Start the App

### Option 1: Run from enhancer_client directory (Now Works!)

```powershell
cd enhancer_client
python main.py
```

### Option 2: Run from project root

```powershell
# From project root
python main_app.py
```

### Option 3: Use the executable

```powershell
# Double-click or run:
dist\PromptBoost\PromptBoost.exe
```

## ⚙️ Configuration

The `.env` file has been created at `enhancer_client/.env` with:

```
API_BASE_URL=https://promptboost-server.onrender.com/api/v1
```

**Important**: Make sure your backend URL includes `/api/v1` at the end!

If you need to change it, edit `enhancer_client/.env` or run:
```powershell
.\create_env.bat
```

## 🔍 Verify It's Working

1. The app should start and show a system tray icon (green square)
2. You should see output like:
   ```
   ============================================================
      PromptBoost - AI Prompt Enhancement Tool
   ============================================================
   👤 User ID: [your-id]
   🌐 API URL: https://promptboost-server.onrender.com/api/v1
   💻 OS: Windows
   🔔 Dialog Box: ENABLED ✅
   ============================================================
   ```

3. Test it:
   - Type: `Write a function to sort a list!!e`
   - Copy it (Ctrl+C)
   - Wait for the dialog box to appear

## ❓ Troubleshooting

### If you still get import errors:

Make sure you're in the correct directory:
```powershell
# Check current directory
pwd

# Should be either:
# D:\promptboost\enhancer_client  (for python main.py)
# OR
# D:\promptboost  (for python main_app.py)
```

### If connection fails:

1. Check your backend is running: Visit `https://promptboost-server.onrender.com/` in browser
2. Verify `.env` file has correct URL: `Get-Content enhancer_client\.env`
3. Make sure URL ends with `/api/v1`

## 🎉 That's It!

The app should now work! Just run it and use the `!!e` trigger to enhance prompts.

