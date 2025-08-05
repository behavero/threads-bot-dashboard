# Threads Auto-Posting Bot

A complete auto-posting bot for Threads with a modern dashboard interface.

## 🏗️ Architecture

- **Backend**: Python Flask server with Threads API integration
- **Frontend**: Next.js dashboard with Tailwind CSS
- **Database**: Supabase PostgreSQL
- **Deployment**: Railway (backend) + Vercel (frontend)

## 📁 Project Structure

```
├── server/                 # Backend bot (Railway deployment)
│   ├── start.py           # Main entry point
│   ├── database.py        # Supabase database operations
│   ├── threads_bot.py     # Threads API integration
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile          # Railway deployment
│   ├── nixpacks.toml     # Railway build config
│   └── runtime.txt        # Python version
├── client/                # Frontend dashboard (Vercel deployment)
│   ├── src/app/          # Next.js app directory
│   ├── package.json      # Node.js dependencies
│   ├── next.config.js    # Next.js configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   └── vercel.json       # Vercel deployment
├── config/               # Configuration files
│   └── init_schema.sql   # Database schema
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
python start.py
```

**Frontend:**
```bash
cd client
npm install
npm run dev
```

## 🛠️ Features

### Backend Bot
- ✅ **Threads API Integration**: Uses official Threads API
- ✅ **Multi-Account Support**: Manages multiple Threads accounts
- ✅ **Auto-Posting**: Posts every 5 minutes per account
- ✅ **Content Rotation**: Random captions and images
- ✅ **Error Handling**: Comprehensive error tracking
- ✅ **Database Integration**: Supabase PostgreSQL storage

### Frontend Dashboard
- ✅ **Account Management**: Add/remove Threads accounts
- ✅ **Content Management**: Upload captions and images
- ✅ **Real-time Status**: Monitor bot activity
- ✅ **Modern UI**: Clean, responsive design
- ✅ **Error Tracking**: View posting history and errors

### Database Schema
- ✅ **Accounts Table**: Store Threads credentials
- ✅ **Captions Table**: Manage post captions
- ✅ **Images Table**: Store image URLs
- ✅ **Posting History**: Track all posting attempts

## 🚀 Deployment

### Railway (Backend)

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
2. **Set Root Directory**: `client/`
3. **Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
   ```
4. **Deploy**: Vercel will build and deploy the Next.js app

## 📊 API Endpoints

### Backend API (Railway)

- `GET /` - Health check
- `GET /api/status` - Bot status
- `GET /api/health` - Health endpoint
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Add account
- `GET /api/captions` - List captions
- `POST /api/captions` - Add caption
- `GET /api/images` - List images
- `POST /api/images` - Add image

## 🔧 Configuration

### Bot Settings

The bot posts every 5 minutes by default. You can modify:

- **Posting Interval**: Change `POSTING_INTERVAL` environment variable
- **Content Rotation**: Bot automatically selects unused captions/images
- **Error Handling**: Failed posts are logged with error messages
- **Account Management**: Add/remove accounts via dashboard

### Database Setup

The bot automatically initializes the database schema on startup:

1. **Tables Created**:
   - `accounts` - Threads account credentials
   - `captions` - Post captions
   - `images` - Image URLs
   - `posting_history` - Posting attempts and results

2. **Indexes**: Optimized for performance
3. **Relationships**: Proper foreign key constraints

## 🛡️ Security

- ✅ **Environment Variables**: Sensitive data stored securely
- ✅ **Database Security**: Supabase RLS policies
- ✅ **API Security**: CORS configured properly
- ✅ **Error Handling**: No sensitive data in logs

## 📈 Monitoring

### Dashboard Features
- **Real-time Status**: Bot activity indicator
- **Account Overview**: Active/inactive accounts
- **Content Management**: Add captions and images
- **Posting History**: Track success/failure rates

### Logging
- **Console Logs**: Detailed bot activity
- **Database Logs**: All posting attempts recorded
- **Error Tracking**: Comprehensive error messages

## 🔄 Development Workflow

1. **Local Testing**: Run both backend and frontend locally
2. **Database Setup**: Configure Supabase project
3. **Deploy Backend**: Push to Railway
4. **Deploy Frontend**: Push to Vercel
5. **Monitor**: Use dashboard to manage bot

## 🐛 Troubleshooting

### Common Issues

1. **Threads API Errors**: Check account credentials
2. **Database Connection**: Verify Supabase credentials
3. **Deployment Issues**: Check environment variables
4. **CORS Errors**: Ensure backend URL is correct

### Debug Mode

Enable debug logging by setting:
```
LOG_LEVEL=DEBUG
```

## 📝 License

This project is for educational purposes. Use responsibly and in accordance with Threads' terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This bot is designed for educational purposes. Please ensure compliance with Threads' terms of service and use responsibly. 