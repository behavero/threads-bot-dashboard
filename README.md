# Threadly - Advanced Threads Auto-Posting Bot

A comprehensive auto-posting bot for Threads with advanced features, human-like behavior, and a modern dashboard interface.

## 🏗️ Architecture

- **Backend**: Enhanced Python bot with human-like behavior and ban risk reduction
- **Frontend**: Next.js dashboard with modern UI and real-time monitoring
- **Database**: Supabase PostgreSQL with optimized schema
- **Deployment**: Railway (backend) + Vercel (frontend)
- **Storage**: Supabase Storage for image management

## 📁 Project Structure

```
├── server/                 # Enhanced backend bot (Railway deployment)
│   ├── enhanced_threads_bot.py     # Main bot with human behavior
│   ├── enhanced_threads_api.py     # Robust API wrapper
│   ├── bot_config.json             # Externalized configuration
│   ├── bot_monitor.py              # Real-time monitoring & analytics
│   ├── run_enhanced_bot.py         # Startup script with CLI options
│   ├── start.py                    # Legacy entry point
│   ├── database.py                 # Supabase database operations
│   ├── requirements.txt            # Python dependencies
│   ├── Procfile                   # Railway deployment
│   ├── nixpacks.toml              # Railway build config
│   └── runtime.txt                 # Python version
├── src/                   # Frontend dashboard (Vercel deployment)
│   ├── app/              # Next.js app directory
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utilities and configurations
│   ├── package.json      # Node.js dependencies
│   ├── next.config.js    # Next.js configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   └── vercel.json       # Vercel deployment
├── config/               # Configuration files
│   └── init_schema.sql   # Database schema
├── public/               # Static assets
│   └── logo.svg          # Threadly logo
└── env.example           # Environment variables template
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd threads-bot
```

### 2. Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Frontend Environment Variables
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

### 3. Local Development

**Backend:**
```bash
cd server
pip install -r requirements.txt
python run_enhanced_bot.py --test
```

**Frontend:**
```bash
npm install
npm run dev
```

## 🛠️ Enhanced Features

### 🤖 Advanced Bot System
- ✅ **Human-Like Behavior**: Random delays, typing simulation, natural pauses
- ✅ **Ban Risk Reduction**: Dynamic intervals, account rotation, success rate monitoring
- ✅ **Content Management**: Weighted random selection, category filtering, image probability
- ✅ **Account Management**: Cooldowns, daily limits, session management
- ✅ **Robust API Integration**: Retry logic, rate limiting, error handling
- ✅ **Real-time Monitoring**: Performance metrics, ban risk assessment, alerts

### 🎛️ Configuration Management
- ✅ **Externalized Settings**: `bot_config.json` for easy customization
- ✅ **CLI Options**: Test mode, dry-run, configuration overrides
- ✅ **Environment Variables**: Flexible deployment configuration
- ✅ **Runtime Adjustments**: Dynamic posting intervals based on success rates

### 📊 Advanced Analytics
- ✅ **Performance Tracking**: Success rates, response times, error rates
- ✅ **Ban Risk Assessment**: Real-time risk calculation and alerts
- ✅ **Account Health Monitoring**: Cooldown tracking, usage patterns
- ✅ **Content Analytics**: Usage statistics, category performance

### 🖥️ Enhanced Dashboard
- ✅ **Modern UI**: Clean, responsive design with Threadly branding
- ✅ **Real-time Status**: Live bot activity and performance metrics
- ✅ **Content Management**: Advanced caption and image management
- ✅ **Account Overview**: Detailed account status and health
- ✅ **Error Tracking**: Comprehensive error logging and display

### 🗄️ Optimized Database
- ✅ **Enhanced Schema**: Category and tags support for captions
- ✅ **Performance Indexes**: Optimized queries for large datasets
- ✅ **Data Integrity**: Proper constraints and relationships
- ✅ **Migration Support**: Backward compatibility with existing data

## 🚀 Deployment

### Railway (Enhanced Backend)

1. **Connect Repository**: Link your GitHub repo to Railway
2. **Set Root Directory**: `server/`
3. **Environment Variables**:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```
4. **Deploy**: Railway will auto-detect Python and deploy

### Vercel (Frontend)

1. **Connect Repository**: Link your GitHub repo to Vercel
2. **Set Root Directory**: `src/`
3. **Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
   ```
4. **Deploy**: Vercel will build and deploy the Next.js app

## 📊 API Endpoints

### Enhanced Backend API (Railway)

- `GET /` - Health check
- `GET /api/status` - Enhanced bot status with metrics
- `GET /api/health` - Health endpoint
- `GET /api/accounts` - List accounts with health data
- `POST /api/accounts` - Add account
- `GET /api/captions` - List captions with categories
- `POST /api/captions` - Add caption
- `GET /api/images` - List images
- `POST /api/images` - Add image
- `GET /api/metrics` - Performance metrics
- `GET /api/analytics` - Ban risk and analytics data

### Frontend API (Vercel)

- `GET /api/prompts` - Fetch captions with error handling
- `POST /api/prompts` - Add captions
- `PUT /api/prompts/[id]` - Update captions
- `DELETE /api/prompts/[id]` - Delete captions
- `POST /api/prompts/upload-csv` - Bulk upload captions
- `GET /api/images` - Fetch images
- `POST /api/images` - Upload images
- `DELETE /api/upload/images/[id]` - Delete images

## 🔧 Advanced Configuration

### Bot Configuration (`bot_config.json`)

```json
{
  "posting": {
    "min_interval": 3600,
    "max_interval": 7200,
    "human_delay_min": 2.0,
    "human_delay_max": 8.0,
    "max_posts_per_day": 8,
    "max_posts_per_account": 3,
    "cooldown_hours": 6,
    "retry_attempts": 3,
    "success_rate_threshold": 0.7
  },
  "content": {
    "image_probability": 0.3,
    "category_weights": {
      "general": 1.0,
      "business": 0.8,
      "personal": 0.7,
      "creative": 0.9,
      "humor": 0.6,
      "inspiration": 0.8,
      "tech": 0.7,
      "lifestyle": 0.8
    }
  },
  "security": {
    "user_agent_rotation": true,
    "proxy_enabled": false,
    "rate_limit_strict": true,
    "ban_risk_threshold": 0.3
  }
}
```

### Enhanced Database Schema

The bot automatically initializes an optimized database schema:

1. **Enhanced Tables**:
   - `accounts` - Threads account credentials with health tracking
   - `captions` - Post captions with categories and tags
   - `images` - Image URLs with metadata
   - `posting_history` - Detailed posting attempts and results
   - `daily_engagement` - Engagement tracking and analytics

2. **Performance Optimizations**:
   - Indexed queries for fast retrieval
   - Proper foreign key relationships
   - Efficient data types and constraints

## 🛡️ Advanced Security

- ✅ **Human-like Behavior**: Mimics natural posting patterns
- ✅ **Ban Risk Reduction**: Dynamic intervals and account rotation
- ✅ **Rate Limiting**: Intelligent API request management
- ✅ **Error Handling**: Comprehensive error recovery
- ✅ **Data Protection**: Secure credential storage
- ✅ **Monitoring**: Real-time threat detection

## 📈 Enhanced Monitoring

### Real-time Dashboard Features
- **Live Bot Status**: Current activity and performance metrics
- **Account Health**: Individual account status and cooldowns
- **Content Analytics**: Usage statistics and category performance
- **Ban Risk Assessment**: Real-time risk calculation
- **Performance Metrics**: Success rates, response times, error tracking

### Advanced Logging
- **Structured Logs**: Detailed bot activity with timestamps
- **Error Tracking**: Comprehensive error categorization
- **Performance Metrics**: Response times and success rates
- **Analytics Export**: JSON format for external analysis

## 🔄 Development Workflow

1. **Local Testing**: Run enhanced bot with test mode
2. **Database Setup**: Configure Supabase with optimized schema
3. **Configuration**: Customize `bot_config.json` for your needs
4. **Deploy Backend**: Push to Railway with enhanced features
5. **Deploy Frontend**: Push to Vercel with modern UI
6. **Monitor**: Use enhanced dashboard for comprehensive management

## 🐛 Troubleshooting

### Common Issues

1. **Threads API Errors**: Enhanced retry logic and error handling
2. **Database Connection**: Optimized connection management
3. **Deployment Issues**: Comprehensive environment validation
4. **Performance Issues**: Real-time monitoring and alerts

### Debug Mode

Enable enhanced debug logging:
```bash
python run_enhanced_bot.py --test --log-level DEBUG
```

### Analytics and Monitoring

Access real-time metrics:
- **Dashboard**: `/dashboard` for comprehensive overview
- **API Metrics**: `/api/metrics` for performance data
- **Analytics**: `/api/analytics` for ban risk assessment

## 📝 License

This project is for educational purposes. Use responsibly and in accordance with Threads' terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with enhanced monitoring
5. Submit a pull request

---

**Note**: This enhanced bot is designed for educational purposes. Please ensure compliance with Threads' terms of service and use responsibly. The advanced features help reduce ban risk through human-like behavior and intelligent monitoring. 