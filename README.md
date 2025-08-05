# Enhanced Threads Bot 🧵

Advanced Python bot for posting to Threads with anti-detection features, user-agent rotation, random delays, and multi-platform deployment support.

## 🚀 Features

### Core Features
- ✅ **Multi-account support** - Manage multiple Threads accounts
- ✅ **24/7 continuous posting** - Automated posting every 5 minutes
- ✅ **Random caption & image selection** - Dynamic content variation
- ✅ **Background scheduler optimization** - Efficient 24/7 operation

### Anti-Detection Features 🛡️
- ✅ **User-Agent rotation** - Rotates between 16 different user agents
- ✅ **Random delays** - Variable delays between actions (30-120 seconds)
- ✅ **Media variation** - Image rotation and metadata variation
- ✅ **Session management** - Automatic session refresh and timeout handling
- ✅ **Account rotation** - Randomizes account processing order
- ✅ **Exponential backoff** - Smart retry logic with increasing delays
- ✅ **Fingerprint rotation** - Device and browser fingerprint variation

### Security Features 🔒
- ✅ **Encrypted token storage** - Secure session token management
- ✅ **Proxy support** - Optional proxy rotation for IP protection
- ✅ **Rate limiting** - Built-in rate limiting to avoid bans
- ✅ **Session isolation** - Separate sessions per account
- ✅ **Error handling** - Comprehensive error handling and recovery

### Deployment Features 🚀
- ✅ **Multi-platform support** - Render.com, Railway.app, Replit.com
- ✅ **Docker support** - Containerized deployment
- ✅ **Environment configuration** - Easy environment variable management
- ✅ **Health checks** - Built-in health monitoring
- ✅ **Auto-restart** - Automatic restart on failures

## 📁 Project Structure

```
Threads_Bot/
├── core/                    # Bot logic and core functionality
│   ├── bot.py              # Main bot application
│   ├── health_check.py     # Health check endpoint
│   └── example_post.py     # Example posting script
├── config/                  # Configuration files
│   ├── accounts.json       # Account configurations
│   ├── user_agents.txt     # User agent rotation list
│   └── legacy_accounts.json # Legacy account format
├── assets/                  # Content assets
│   ├── captions.txt        # Caption content (one per line)
│   └── images/             # Image directory
├── server/                  # Web dashboard backend
│   └── app.py              # Flask server
├── docs/                    # Documentation
│   ├── README.md           # Basic documentation
│   ├── enhanced_README.md  # Enhanced documentation
│   ├── DEPLOYMENT_GUIDE.md # Deployment instructions
│   └── *.md                # Other documentation
├── start.py                 # Main entry point
├── requirements.txt         # Python dependencies
├── deploy.py               # Deployment validation script
└── *.yaml/*.json          # Platform deployment configs
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/enhanced-threads-bot.git
cd enhanced-threads-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Accounts
Edit `config/accounts.json` with your Threads accounts:
```json
[
  {
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password",
    "enabled": true,
    "description": "Main account",
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
    },
    "fingerprint_config": {
      "device_type": "iPhone",
      "os_version": "17.0",
      "browser_version": "Safari/604.1",
      "screen_resolution": "1170x2532",
      "timezone": "UTC"
    }
  }
]
```

### 4. Add Content
- Add captions to `assets/captions.txt` (one per line)
- Add images to `assets/images/` directory (JPG, PNG, GIF)

### 5. Configure Environment
Create `.env` file:
```env
PLATFORM=local
ENVIRONMENT=production
ENABLE_MONITORING=true
ENABLE_LOGGING=true
```

## 🚀 Usage

### Quick Start
```bash
python start.py
```

### Local Development
```bash
python core/bot.py
```

### Health Check
```bash
python core/health_check.py
```

### Example Post
```bash
python core/example_post.py
```

### Deployment Validation
```bash
python deploy.py
```

## 📊 Configuration

### Account Configuration
Each account supports the following settings:

```json
{
  "username": "string",
  "email": "string", 
  "password": "string",
  "enabled": true,
  "description": "string",
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
  },
  "fingerprint_config": {
    "device_type": "iPhone",
    "os_version": "17.0",
    "browser_version": "Safari/604.1",
    "screen_resolution": "1170x2532",
    "timezone": "UTC"
  }
}
```

### Content Configuration

#### Captions (`assets/captions.txt`)
Add your captions, one per line:
```
Just another day in paradise! 🌴
Coffee and creativity ☕️✨
Living my best life 💫
Sharing some awesome content! 🔥
This is absolutely amazing! 🚀
```

#### Images (`assets/images/`)
Place your images in the `assets/images/` directory. Supported formats:
- .jpg
- .jpeg  
- .png
- .gif

#### User Agents (`config/user_agents.txt`)
The bot includes 16 different user agents for rotation:
```
Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15
Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15
```

## 🚀 Deployment

### Render.com
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python start.py`
4. Add environment variables in dashboard

### Railway.app
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`

### Replit.com
1. Import your GitHub repository
2. Click "Run" button
3. Service will be available at your Repl URL

### Docker
```bash
docker build -t enhanced-threads-bot .
docker run -d enhanced-threads-bot
```

## 🛡️ Anti-Detection Features

### User-Agent Rotation
- 16 different user agents for iPhone and iPad
- Automatic rotation between requests
- Realistic device and OS combinations

### Random Delays
- 30-120 second random delays between actions
- Exponential backoff for retries
- Variable delays between accounts

### Media Variation
- Image rotation to avoid repetition
- Metadata variation for images
- Smart content selection algorithms

### Session Management
- Automatic session refresh every hour
- Unique session IDs per account
- Secure token storage with encryption

## 📈 Monitoring & Statistics

The bot tracks comprehensive statistics:
- Total posts attempted
- Successful vs failed posts
- Account rotation count
- Session restart count
- Success rates per account

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Core Configuration
ENVIRONMENT=production
PLATFORM=render|railway|replit
LOG_LEVEL=INFO

# Bot Features
ANTI_DETECTION_ENABLED=true
FINGERPRINT_ROTATION=true
DEVICE_ROTATION=true

# Image Usage Tracking
GLOBAL_IMAGE_COOLDOWN=1800
ACCOUNT_IMAGE_COOLDOWN=3600
MAX_ACCOUNT_HISTORY=5
CLEANUP_MAX_AGE_HOURS=24

# Session Management
SESSION_TIMEOUT=3600
MAX_RETRIES=3

# File Paths
ACCOUNTS_FILE=config/accounts.json
CAPTIONS_FILE=assets/captions.txt
IMAGES_DIR=assets/images/
USER_AGENTS_FILE=config/user_agents.txt
```

### Health Check Endpoint
```bash
GET /api/status
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "environment": "production",
  "platform": "render|railway|replit",
  "bot_status": {...},
  "accounts_count": 5,
  "captions_count": 10,
  "images_count": 15
}
```

## 🐛 Troubleshooting

### Common Issues

#### Login Failures
- Check username/password
- Verify account is not banned
- Try different user agent
- Check network connection

#### Posting Failures
- Verify account permissions
- Check content guidelines
- Monitor rate limits
- Review error logs

#### Performance Issues
- Monitor memory usage
- Check CPU utilization
- Review network latency
- Optimize delays

### Debug Mode
```bash
DEBUG=true python start.py
```

### Log Analysis
```bash
tail -f enhanced_bot.log
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📞 Support

- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for errors
- Test with a single account first

---

**⚠️ Disclaimer**: This bot is for educational purposes. Use responsibly and in accordance with Threads' Terms of Service. The authors are not responsible for any account bans or violations. 