# 🤖 Enhanced Threads Bot

A sophisticated, human-like Threads automation bot with advanced features for reducing ban risk and maximizing engagement.

## 🚀 Features

### **Human-like Behavior**
- **Randomized posting intervals** (1-2 hours with variation)
- **Typing delays** based on text length
- **Natural pauses** between actions
- **Human-like delays** before and after posting

### **Ban Risk Reduction**
- **Account rotation** with cooldowns
- **Daily posting limits** per account
- **Success rate monitoring** with automatic adjustments
- **Ban risk scoring** for each account
- **Rate limiting** and retry logic

### **Content Management**
- **Smart content rotation** with weighted selection
- **Category-based filtering**
- **Image probability** settings
- **Content freshness** prioritization

### **Monitoring & Analytics**
- **Real-time dashboard** with performance metrics
- **Ban risk assessment** for each account
- **Success rate tracking**
- **Error monitoring** and alerting
- **Metrics export** for analysis

### **Security Features**
- **Session management** with timeouts
- **User agent rotation**
- **Proxy support** (configurable)
- **Exponential backoff** for retries

## 📁 File Structure

```
server/
├── enhanced_threads_bot.py      # Main enhanced bot
├── enhanced_threads_api.py      # Enhanced API wrapper
├── bot_monitor.py              # Monitoring system
├── bot_config.json             # Configuration file
├── run_enhanced_bot.py         # Startup script
├── database.py                 # Database manager
├── threads_api_mock.py         # Mock API for testing
└── ENHANCED_BOT_README.md     # This file
```

## 🛠️ Installation & Setup

### 1. **Install Dependencies**
```bash
cd server
pip install requests dataclasses-json
```

### 2. **Configure Database**
Ensure your Supabase database is set up with the required tables:
- `accounts` - Threads accounts
- `captions` - Content captions
- `images` - Content images
- `posting_history` - Posting logs

### 3. **Environment Variables**
Set up your environment variables:
```bash
export SUPABASE_URL="your_supabase_url"
export SUPABASE_ANON_KEY="your_supabase_anon_key"
export THREADS_API_PRODUCTION="false"  # Set to "true" for production
```

### 4. **Configuration**
Edit `bot_config.json` to customize behavior:
```json
{
  "posting": {
    "min_interval": 3600,
    "max_interval": 7200,
    "max_posts_per_day": 8,
    "cooldown_hours": 6
  },
  "content": {
    "image_probability": 0.3,
    "max_text_length": 500
  },
  "security": {
    "ban_risk_threshold": 0.3,
    "rate_limit_strict": true
  }
}
```

## 🚀 Usage

### **Basic Usage**
```bash
python run_enhanced_bot.py
```

### **Test Mode**
```bash
python run_enhanced_bot.py --test
```

### **Custom Configuration**
```bash
python run_enhanced_bot.py --config my_config.json --log-level DEBUG
```

### **Dry Run Mode**
```bash
python run_enhanced_bot.py --dry-run
```

## 📊 Monitoring Dashboard

The bot includes a real-time dashboard showing:

```
============================================================
🤖 THREADS BOT DASHBOARD
============================================================
📊 Total Posts: 45
✅ Success Rate: 87.50%
⏱️ Avg Response Time: 2.34s
🕐 Last Post: 2024-01-15 14:30:25

👥 Active Accounts: 3
  🟢 user1: 15 posts, 93.33% success, 12% risk
  🟡 user2: 12 posts, 75.00% success, 45% risk
  🟢 user3: 18 posts, 88.89% success, 8% risk

🚨 Recent Alerts (2):
  ⚠️ High error rate for user2: 3/12
  ℹ️ Low success rate: 87.50%
============================================================
```

## 🔧 Configuration Options

### **Posting Configuration**
- `min_interval`: Minimum time between posts (seconds)
- `max_interval`: Maximum time between posts (seconds)
- `max_posts_per_day`: Maximum posts per account per day
- `cooldown_hours`: Hours to wait after posting
- `success_rate_threshold`: Minimum success rate before adjustments

### **Content Configuration**
- `image_probability`: Probability of including images (0.0-1.0)
- `category_weights`: Weight multipliers for different categories
- `max_text_length`: Maximum caption length
- `min_text_length`: Minimum caption length

### **Security Configuration**
- `ban_risk_threshold`: Risk level that triggers alerts
- `rate_limit_strict`: Strict rate limiting
- `user_agent_rotation`: Rotate user agents
- `proxy_enabled`: Enable proxy support

## 🛡️ Ban Risk Reduction Strategies

### **1. Human-like Timing**
- Random delays between actions
- Natural typing simulation
- Variable posting intervals
- Account rotation with cooldowns

### **2. Content Diversity**
- Weighted content selection
- Category rotation
- Image/text ratio variation
- Content freshness prioritization

### **3. Account Management**
- Daily posting limits
- Success rate monitoring
- Automatic cooldown adjustments
- Ban risk scoring

### **4. Error Handling**
- Exponential backoff retries
- Rate limit detection
- Session timeout management
- Graceful error recovery

## 📈 Analytics & Monitoring

### **Performance Metrics**
- Success rate tracking
- Response time monitoring
- Error rate analysis
- Account health scoring

### **Ban Risk Assessment**
- High frequency posting detection
- Error rate analysis
- Success rate monitoring
- Suspicious pattern detection

### **Alert System**
- Low success rate alerts
- High error rate warnings
- Ban risk critical alerts
- Performance degradation notifications

## 🔍 Troubleshooting

### **Common Issues**

1. **Low Success Rate**
   - Check account credentials
   - Verify API connectivity
   - Review posting intervals
   - Check for rate limiting

2. **High Ban Risk**
   - Reduce posting frequency
   - Increase delays between posts
   - Rotate accounts more frequently
   - Review content diversity

3. **API Errors**
   - Check network connectivity
   - Verify API credentials
   - Review rate limits
   - Check for service outages

### **Debug Mode**
```bash
python run_enhanced_bot.py --log-level DEBUG --test
```

## 📝 Log Files

The bot generates detailed logs:
- `threads_bot.log` - Main application log
- `bot_metrics_*.json` - Performance metrics
- `test_metrics.json` - Test run metrics

## 🔄 Migration from Old Bot

1. **Backup your data**
2. **Update database schema** if needed
3. **Test with `--test` mode**
4. **Monitor performance** for first few days
5. **Adjust configuration** based on results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This bot is for educational purposes. Use responsibly and in accordance with Threads' Terms of Service. The authors are not responsible for any account bans or other consequences of using this software. 