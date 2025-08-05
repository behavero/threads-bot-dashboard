# Enhanced Threads Bot - Deployment Guide 🚀

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ All required files in your repository
- ✅ Valid Threads account credentials
- ✅ Images and captions ready

## 🛠️ Required Files

Make sure these files are present in your repository:

```
├── enhanced_bot.py          # Main bot script
├── start.py                 # Production startup script
├── requirements.txt         # Python dependencies
├── render.yaml             # Render.com configuration
├── Procfile                # Railway.app configuration
├── runtime.txt             # Python version specification
├── enhanced_accounts.json  # Account configurations
├── captions.txt           # Post captions
├── user_agents.txt        # User agent rotation
├── images/                # Images directory
└── health_check.py        # Health check endpoint
```

## 🚀 Deployment Options

### Option 1: Render.com Deployment

1. **Connect Repository**
   - Go to [Render.com](https://render.com)
   - Connect your GitHub repository
   - Select "Web Service"

2. **Configure Service**
   - **Name**: `enhanced-threads-bot`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`

3. **Environment Variables**
   The following environment variables are automatically set by `render.yaml`:
   ```yaml
   ENVIRONMENT: production
   PLATFORM: render
   ENABLE_MONITORING: true
   ENABLE_LOGGING: true
   ANTI_DETECTION_ENABLED: true
   FINGERPRINT_ROTATION: true
   DEVICE_ROTATION: true
   SESSION_TIMEOUT: 3600
   MAX_RETRIES: 3
   CONFIG_SOURCE: json
   ACCOUNTS_FILE: enhanced_accounts.json
   CAPTIONS_FILE: captions.txt
   IMAGES_DIR: images/
   USER_AGENTS_FILE: user_agents.txt
   LOG_LEVEL: INFO
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your bot

### Option 2: Railway.app Deployment

1. **Connect Repository**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select "Deploy from GitHub repo"

2. **Automatic Configuration**
   - Railway will automatically detect the `Procfile`
   - Build command: `pip install -r requirements.txt`
   - Start command: `python start.py`

3. **Environment Variables** (Optional)
   You can set these in Railway dashboard:
   ```
   ENVIRONMENT=production
   PLATFORM=railway
   LOG_LEVEL=INFO
   ANTI_DETECTION_ENABLED=true
   ```

4. **Deploy**
   - Railway will automatically deploy your bot
   - Monitor logs in the Railway dashboard

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Set to `production` for deployment |
| `PLATFORM` | `local` | Platform identifier |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ANTI_DETECTION_ENABLED` | `true` | Enable anti-detection features |
| `FINGERPRINT_ROTATION` | `true` | Enable fingerprint rotation |
| `DEVICE_ROTATION` | `true` | Enable device rotation |
| `SESSION_TIMEOUT` | `3600` | Session timeout in seconds |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `ACCOUNTS_FILE` | `enhanced_accounts.json` | Accounts configuration file |
| `CAPTIONS_FILE` | `captions.txt` | Captions file |
| `IMAGES_DIR` | `images/` | Images directory |
| `USER_AGENTS_FILE` | `user_agents.txt` | User agents file |

### Account Configuration

Update `enhanced_accounts.json` with your Threads accounts:

```json
[
  {
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password",
    "enabled": true,
    "description": "Your account description",
    "posting_schedule": {
      "frequency": "every_5_minutes",
      "interval_minutes": 5,
      "timezone": "UTC",
      "start_time": "00:00",
      "end_time": "23:59"
    },
    "posting_config": {
      "use_random_caption": true,
      "use_random_image": true,
      "max_posts_per_day": 288,
      "delay_between_posts_seconds": 300,
      "user_agent_rotation": true,
      "random_delays": true,
      "media_variation": true,
      "anti_detection_level": "high",
      "session_timeout": 3600,
      "max_retries": 3
    }
  }
]
```

## 📊 Monitoring

### Health Check

The bot includes a health check endpoint:

```bash
# Check bot status
python health_check.py
```

Expected output:
```json
{
  "status": "healthy",
  "data": {
    "status": "running",
    "timestamp": "2024-01-01T12:00:00",
    "environment": "production",
    "platform": "render",
    "version": "2.0.0",
    "features": {
      "anti_detection": true,
      "user_agent_rotation": true,
      "session_management": true,
      "rate_limit_handling": true,
      "human_behavior_simulation": true
    },
    "files": {
      "enhanced_accounts.json": true,
      "captions.txt": true,
      "user_agents.txt": true
    },
    "images_directory": true
  }
}
```

### Logs

- **Development**: Verbose logging with debug information
- **Production**: Clean logging with INFO level only
- **Log File**: `enhanced_bot.log`

## 🔒 Security Features

### Anti-Detection
- ✅ Random sleep intervals (3-6 minutes)
- ✅ User-agent rotation (25 different agents)
- ✅ Session management with token refresh
- ✅ Rate limiting and shadowban detection
- ✅ Human behavior simulation

### Error Handling
- ✅ Pattern-based error detection
- ✅ Automatic retry with exponential backoff
- ✅ Graceful handling of rate limits
- ✅ Shadowban detection and cooldown

## 🚨 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Missing Files**
   - Ensure all required files are present
   - Check file permissions

3. **Import Errors**
   - Verify Python version (3.11+)
   - Check all dependencies are installed

4. **Authentication Errors**
   - Verify account credentials in `enhanced_accounts.json`
   - Check if accounts are not rate limited

### Log Analysis

Check logs for:
- ✅ Successful logins
- ✅ Successful posts
- ⚠️ Rate limit warnings
- 🚫 Shadowban detections
- 🔄 Token refreshes

## 📈 Performance

### Expected Behavior
- **Posts**: 1 post every 3-6 minutes per account
- **Accounts**: All enabled accounts processed in rotation
- **Uptime**: 24/7 continuous operation
- **Success Rate**: 95%+ with proper configuration

### Resource Usage
- **CPU**: Low (Python async operations)
- **Memory**: ~50-100MB per account
- **Network**: Minimal (API calls only)
- **Storage**: Logs and temporary files

## 🎯 Success Metrics

Monitor these metrics for successful deployment:
- ✅ Bot starts without errors
- ✅ Accounts login successfully
- ✅ Posts are created on Threads
- ✅ No rate limiting or shadowbans
- ✅ Continuous operation for 24+ hours

## 🔄 Updates

To update the bot:
1. Push changes to your repository
2. Platform will automatically redeploy
3. Monitor logs for successful startup
4. Verify bot functionality

## 📞 Support

For deployment issues:
1. Check platform-specific logs
2. Verify all required files are present
3. Test locally before deploying
4. Review environment variable configuration

---

**🎉 Your Enhanced Threads Bot is now ready for production deployment!** 