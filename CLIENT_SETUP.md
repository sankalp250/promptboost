# Client Setup Guide

After deploying your PromptBoost server on Render, you need to update the client application to use the new API URL.

## Update Client Configuration

### Option 1: Using Environment File (Recommended)

1. Create or edit `.env` file in the `enhancer_client/` directory:

```env
API_BASE_URL=https://your-app-name.onrender.com/api/v1
```

Replace `your-app-name` with your actual Render service name.

### Option 2: Direct Code Update

Edit `enhancer_client/enhancer/config.py`:

```python
class Settings(BaseSettings):
    API_BASE_URL: str = "https://your-app-name.onrender.com/api/v1"  # Update this
    USER_ID: uuid.UUID | None = None
```

## Testing the Connection

1. **Start your client application:**
   ```bash
   cd enhancer_client
   python main.py
   ```

2. **Test the enhancement:**
   - Copy some text
   - Add `!!e` at the end
   - The client should connect to your Render-hosted API

3. **Check for errors:**
   - If you see connection errors, verify:
     - The API URL is correct
     - The Render service is running
     - Your firewall allows the connection

## Verifying API is Accessible

Before updating the client, verify your Render API is working:

```bash
# Test health check
curl https://your-app-name.onrender.com/

# Test API docs
# Open in browser: https://your-app-name.onrender.com/docs
```

## Distribution

When distributing your client application:

1. **Include the Render API URL** in the default configuration
2. **Or provide a setup wizard** that lets users enter the API URL
3. **Document the API URL** in your README

### Example User Configuration

You can create a simple config file users can edit:

```json
{
  "api_url": "https://your-app-name.onrender.com/api/v1",
  "user_preferences": {}
}
```

## Troubleshooting

### Connection Refused

- Check if Render service is running
- Verify the API URL is correct (include `https://`)
- Check if Render service has spun down (free tier limitation)

### API Not Responding

- Check Render service logs
- Verify environment variables are set correctly
- Check database connection

### CORS Errors (if using web client)

The server includes CORS middleware configured for `*` origins. For production, you may want to restrict this to specific domains.

