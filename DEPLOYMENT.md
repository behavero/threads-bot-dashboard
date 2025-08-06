# 🚀 Threadly - Enhanced Threads Bot Deployment Guide

## 📋 Overview

This project is split into two independent services with advanced features:

- **Frontend (Dashboard)** → Hosted on **Vercel**
- **Backend (Enhanced Bot + API)** → Hosted on **Railway**

## 🏗️ Enhanced Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Railway       │    │   Supabase      │
│   Frontend      │◄──►│   Enhanced      │◄──►│   Database      │
│   (Dashboard)   │    │   Bot + API     │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Deployment Status

### ✅ Enhanced Backend (Railway) - WORKING
- **URL**: Your Railway app URL
- **Status**: ✅ Running with advanced features
- **Enhanced API Endpoints**: 
  - `/` - Health check
  - `/api/status` - Enhanced bot status with metrics
  - `/api/health` - Health endpoint
  - `/api/accounts` - Account management with health data
  - `/api/captions` - Caption management with categories
  - `/api/images` - Image management
  - `/api/metrics` - Performance metrics
  - `/api/analytics` - Ban risk and analytics data

### ✅ Enhanced Frontend (Vercel) - WORKING
- **URL**: Your Vercel app URL
- **Status**: ✅ Deployed with modern UI
- **Enhanced Features**: Advanced dashboard with real-time monitoring

## 🚀 Deployment Steps

### 1. Enhanced Backend (Railway) - ✅ COMPLETE

**Current Status**: Successfully deployed with advanced features

**Environment Variables Set**:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**Enhanced Features Working**:
- ✅ **Human-like Behavior**: Random delays, typing simulation
- ✅ **Ban Risk Reduction**: Dynamic intervals, account rotation
- ✅ **Advanced Monitoring**: Real-time metrics and analytics
- ✅ **Configuration Management**: Externalized `bot_config.json`
- ✅ **Robust API Integration**: Retry logic, rate limiting
- ✅ **Content Management**: Weighted selection, category filtering

### 2. Enhanced Frontend (Vercel) - ✅ COMPLETE

#### **Step 1: Connect Repository**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `behavero/threads-bot-dashboard`

#### **Step 2: Configure Project**
- **Framework Preset**: Next.js
- **Root Directory**: `src`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

#### **Step 3: Set Environment Variables**
Add these in Vercel project settings:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

#### **Step 4: Deploy**
Click "Deploy" and wait for the build to complete.

## 🔧 Testing the Enhanced Connection

### Enhanced Backend Test
Visit: `https://your-railway-app.railway.app/api/status`
Expected response:
```json
{
  "status": "running",
  "service": "enhanced-threads-bot",
  "bot_running": true,
  "timestamp": "2025-08-06T16:00:00.000000",
  "environment": "railway",
  "backend_url": "https://your-railway-app.railway.app",
  "metrics": {
    "success_rate": 0.85,
    "total_posts": 192,
    "active_accounts": 5,
    "ban_risk": 0.12
  }
}
```

### Enhanced Frontend Test
After Vercel deployment, visit your app and check:
- ✅ **Modern UI**: Clean, responsive design with Threadly branding
- ✅ **Real-time Status**: Live bot activity and performance metrics
- ✅ **Advanced Content Management**: Categories, tags, bulk upload
- ✅ **Account Health**: Individual account status and cooldowns
- ✅ **Error Tracking**: Comprehensive error logging and display

## 📊 Enhanced Project Structure

```
/
├── src/                   # Enhanced Frontend (Vercel)
│   ├── app/              # Next.js app directory
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utilities and configurations
│   ├── package.json      # Dependencies
│   ├── next.config.js    # Next.js config
│   └── vercel.json       # Vercel deployment
├── server/               # Enhanced Backend (Railway)
│   ├── enhanced_threads_bot.py     # Main bot with human behavior
│   ├── enhanced_threads_api.py     # Robust API wrapper
│   ├── bot_config.json             # Externalized configuration
│   ├── bot_monitor.py              # Real-time monitoring & analytics
│   ├── run_enhanced_bot.py         # Startup script with CLI options
│   ├── start.py                    # Legacy entry point
│   ├── database.py                 # Supabase operations
│   ├── requirements.txt            # Python dependencies
│   ├── Procfile                   # Railway worker process
│   └── init_schema.sql            # Enhanced database schema
├── public/               # Static assets
│   └── logo.svg          # Threadly logo
├── config/               # Shared config
│   └── init_schema.sql  # Database schema (copy)
└── env.example          # Environment template
```

## 🔗 Enhanced API Endpoints

### Enhanced Backend API (Railway)
- `GET /` - Health check
- `GET /api/status` - Enhanced bot status with metrics
- `GET /api/health` - Health endpoint
- `GET /api/info` - Service information
- `GET /api/accounts` - List accounts with health data
- `POST /api/accounts` - Add account
- `GET /api/captions` - List captions with categories
- `POST /api/captions` - Add caption
- `GET /api/images` - List images
- `POST /api/images` - Add image
- `GET /api/metrics` - Performance metrics
- `GET /api/analytics` - Ban risk and analytics data

### Enhanced Frontend API (Vercel)
- `GET /api/prompts` - Fetch captions with error handling
- `POST /api/prompts` - Add captions
- `PUT /api/prompts/[id]` - Update captions
- `DELETE /api/prompts/[id]` - Delete captions
- `POST /api/prompts/upload-csv` - Bulk upload captions
- `GET /api/images` - Fetch images
- `POST /api/images` - Upload images
- `DELETE /api/upload/images/[id]` - Delete images

## 🛠️ Enhanced Environment Variables

### Enhanced Backend (Railway)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### Enhanced Frontend (Vercel)
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

## 🎛️ Advanced Configuration

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

## 🎯 Enhanced Next Steps

1. **Configure Bot Settings**: Customize `bot_config.json` for your needs
2. **Add Test Accounts**: Use the enhanced dashboard to add Threads accounts
3. **Upload Content**: Add captions with categories and images
4. **Monitor Performance**: Use real-time metrics and analytics
5. **Optimize Settings**: Adjust based on performance data

## 🐛 Enhanced Troubleshooting

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

---

**🎉 Enhanced bot ready for production deployment with advanced features!** 