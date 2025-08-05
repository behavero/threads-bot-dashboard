# 🚀 Enhanced Threads Bot

A sophisticated Threads automation bot with anti-detection features, multi-account support, and a modern web dashboard.

## 🏗️ Project Structure

```
Threads_Bot/
├── client/          # Vercel Frontend (Next.js Dashboard)
│   ├── src/
│   ├── package.json
│   └── vercel.json
├── server/          # Railway Backend (Python Bot)
│   ├── core/        # Bot logic
│   ├── config/      # Configuration files
│   ├── assets/      # Images and captions
│   ├── start.py     # Entry point
│   ├── Dockerfile   # Python Docker build
│   └── railway.json
└── docs/            # Documentation
```

## 🚀 Deployment

### **Railway (Backend Bot)**
The backend bot runs on Railway using Python and Docker.

#### **Railway Configuration:**
- **Root Directory**: `server/`
- **Builder**: `DOCKERFILE`
- **Start Command**: `python start.py`
- **Health Check**: `/api/status`

#### **Railway Setup:**
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the `server/` directory
3. Set environment variables in Railway dashboard
4. Deploy with `python start.py`

#### **Required Environment Variables:**
```env
# Supabase Configuration
SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
SUPABASE_KEY=your_supabase_key

# Bot Configuration
PLATFORM=railway
ENVIRONMENT=production
ANTI_DETECTION_ENABLED=true
SESSION_TIMEOUT=3600
MAX_RETRIES=3

# File Paths
ACCOUNTS_FILE=config/accounts.json
CAPTIONS_FILE=assets/captions.txt
IMAGES_DIR=assets/images/
USER_AGENTS_FILE=config/user_agents.txt
```

### **Vercel (Frontend Dashboard)**
The frontend dashboard runs on Vercel using Next.js.

#### **Vercel Configuration:**
- **Root Directory**: `client/`
- **Framework**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

#### **Vercel Setup:**
1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the `client/` directory
3. Set environment variables in Vercel dashboard
4. Deploy with `npm run build`

#### **Required Environment Variables:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

## 🎯 Features

### 🤖 Bot Features
- **Multi-Account Support**: Rotate between multiple Threads accounts
- **Anti-Detection**: User-agent rotation, random delays, fingerprint management
- **Smart Scheduling**: Intelligent posting intervals with human-like patterns
- **Media Management**: Image rotation with usage tracking
- **Session Management**: Persistent login sessions with automatic refresh
- **Error Handling**: Robust error recovery and rate limit handling

### 📊 Dashboard Features
- **Real-time Monitoring**: Live bot status and statistics
- **Account Management**: Add, edit, and manage Threads accounts
- **Content Management**: Upload images and manage captions
- **Analytics**: Posting history and performance metrics
- **Settings**: Configure bot behavior and timing

## 🛠️ Technology Stack

### Backend (Railway)
- **Python 3.11** - Core bot logic
- **Flask** - API server for dashboard
- **Supabase** - PostgreSQL database
- **Threads API** - Official posting interface
- **APScheduler** - Task scheduling

### Frontend (Vercel)
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **Supabase JS** - Database client
- **React Hot Toast** - Notifications

## 📦 Installation

### Backend Setup
```bash
cd server
pip install -r requirements.txt
python start.py
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## 📊 Database Schema

### Tables
- **accounts**: Threads account credentials and settings
- **captions**: Post captions with metadata
- **images**: Image files with usage tracking
- **posting_history**: Post history and analytics

## 🔒 Security

- **Environment Variables**: All sensitive data stored in platform variables
- **Database Security**: Supabase Row Level Security (RLS)
- **API Keys**: Secure storage and rotation
- **Session Management**: Encrypted session storage

## 📈 Monitoring

### Health Checks
- **Backend**: `/api/status` endpoint
- **Database**: Connection monitoring
- **Bot Status**: Real-time running status

### Logging
- **Structured Logging**: JSON format with levels
- **Error Tracking**: Comprehensive error reporting
- **Performance Metrics**: Response times and throughput

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` directory
- **Deployment Guide**: `DEPLOYMENT.md`

---

**🎯 Ready to automate your Threads presence with style!** 