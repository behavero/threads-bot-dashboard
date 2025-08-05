# 🚀 Enhanced Threads Bot - Full Stack Architecture

A complete Threads automation solution with **Railway backend** and **Vercel frontend**, powered by **Supabase PostgreSQL**.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Railway       │    │   Supabase      │
│   Frontend      │◄──►│   Backend       │◄──►│   PostgreSQL    │
│   (Dashboard)   │    │   (Bot + API)   │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
threads-bot/
├── backend/                 # Railway deployment (Bot + API)
│   ├── core/               # Bot logic
│   │   ├── bot.py         # Main bot implementation
│   │   └── db_manager.py  # Database operations
│   ├── config/            # Configuration files
│   │   ├── db.py         # Database connection
│   │   └── accounts.json # Account credentials
│   ├── assets/           # Content files
│   │   ├── captions.txt  # Post captions
│   │   └── images/       # Post images
│   ├── scripts/          # Utility scripts
│   ├── app.py           # Flask API server
│   ├── main.py          # Bot entry point
│   ├── requirements.txt # Python dependencies
│   ├── railway.json    # Railway configuration
│   └── nixpacks.toml   # Railway build config
│
├── frontend/              # Vercel deployment (Dashboard)
│   ├── src/
│   │   ├── app/         # Next.js app directory
│   │   └── components/  # React components
│   ├── package.json     # Node.js dependencies
│   ├── next.config.js   # Next.js configuration
│   ├── tailwind.config.js # Tailwind CSS
│   └── vercel.json      # Vercel configuration
│
└── README.md
```

## 🚀 Quick Start

### 1. Backend Deployment (Railway)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Test locally
python main.py

# Deploy to Railway
railway login
railway link
railway up
```

### 2. Frontend Deployment (Vercel)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Test locally
npm run dev

# Deploy to Vercel
vercel
```

## 🔧 Configuration

### Environment Variables

#### Backend (Railway)
```env
# Supabase Configuration
SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
SUPABASE_KEY=your_supabase_anon_key

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

#### Frontend (Vercel)
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

## 🗄️ Database Schema

### Tables (Supabase PostgreSQL)

```sql
-- Captions table
CREATE TABLE captions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Images table
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    use_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Accounts table
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    posting_schedule JSONB,
    posting_config JSONB,
    fingerprint_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posting history table
CREATE TABLE posting_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    caption_id INTEGER REFERENCES captions(id),
    image_id INTEGER REFERENCES images(id),
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    user_agent TEXT
);
```

## 🤖 Bot Features

### Core Functionality
- ✅ **Multi-account support** - Manage multiple Threads accounts
- ✅ **Scheduled posting** - Automatic posts every X minutes
- ✅ **Anti-detection** - User agent rotation, delays, fingerprinting
- ✅ **Content rotation** - Random captions and images
- ✅ **Error handling** - Retry logic and fallback mechanisms
- ✅ **Database integration** - Supabase with PostgreSQL fallback

### Advanced Features
- ✅ **Session management** - Per-account cookies and sessions
- ✅ **Rate limiting** - Smart delays and cooldowns
- ✅ **Image usage tracking** - Prevent overuse of images
- ✅ **Shadowban detection** - Monitor account health
- ✅ **Real-time monitoring** - Live dashboard updates

## 🎛️ Dashboard Features

### Management Interface
- ✅ **Account management** - Add, edit, enable/disable accounts
- ✅ **Caption management** - Add, edit, delete captions
- ✅ **Image management** - Upload, track usage, delete images
- ✅ **Bot control** - Start/stop bot, monitor status
- ✅ **Real-time stats** - Live posting statistics

### Analytics
- ✅ **Posting history** - Track all posting attempts
- ✅ **Success rates** - Monitor bot performance
- ✅ **Error tracking** - Debug failed posts
- ✅ **Usage analytics** - Image and caption usage stats

## 🔄 API Endpoints

### Bot Control
```
POST /api/bot/start     # Start the bot
POST /api/bot/stop      # Stop the bot
GET  /api/bot/status    # Get bot status
```

### Account Management
```
GET    /api/accounts    # Get all accounts
POST   /api/accounts    # Create new account
PUT    /api/accounts/:id # Update account
DELETE /api/accounts/:id # Delete account
```

### Content Management
```
GET    /api/captions    # Get all captions
POST   /api/captions    # Add new caption
PUT    /api/captions/:id # Update caption
DELETE /api/captions/:id # Delete caption

GET    /api/images      # Get all images
POST   /api/images      # Upload image
DELETE /api/images/:id  # Delete image
```

### System Status
```
GET /api/status         # Overall system status
```

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
cd backend
python scripts/init_db.py
```

## 🚀 Deployment

### Railway (Backend)
1. Connect GitHub repository to Railway
2. Set environment variables
3. Deploy automatically on push

### Vercel (Frontend)
1. Connect GitHub repository to Vercel
2. Set environment variables
3. Deploy automatically on push

## 📊 Monitoring

### Health Checks
- ✅ **Railway health check** - `/api/status`
- ✅ **Database connectivity** - Automatic fallback
- ✅ **Bot status monitoring** - Real-time status

### Logging
- ✅ **Structured logging** - JSON format
- ✅ **Error tracking** - Detailed error messages
- ✅ **Performance monitoring** - Response times

## 🔒 Security

### Data Protection
- ✅ **Environment variables** - Secure credential storage
- ✅ **Database encryption** - Supabase security
- ✅ **API authentication** - CORS protection
- ✅ **Input validation** - Sanitized inputs

### Anti-Detection
- ✅ **User agent rotation** - Random browser signatures
- ✅ **Session rotation** - Fresh cookies per account
- ✅ **Delay randomization** - Human-like timing
- ✅ **Device fingerprinting** - Unique device profiles

## 🐛 Troubleshooting

### Common Issues

**Bot won't start:**
- Check account credentials in `config/accounts.json`
- Verify Supabase connection
- Check logs for specific errors

**Posts not appearing:**
- Verify Threads API connectivity
- Check account login status
- Review anti-detection settings

**Database errors:**
- Verify Supabase credentials
- Check table permissions
- Review connection limits

### Debug Commands
```bash
# Test database connection
python -c "from config.db import init_database; import asyncio; asyncio.run(init_database())"

# Test bot initialization
python -c "from core.bot import EnhancedThreadsBot, BotConfig; bot = EnhancedThreadsBot(BotConfig())"

# Check file structure
find . -name "*.py" -o -name "*.json" -o -name "*.txt"
```

## 📈 Performance

### Optimization
- ✅ **Connection pooling** - Efficient database connections
- ✅ **Async operations** - Non-blocking I/O
- ✅ **Caching** - Reduced database queries
- ✅ **Batch operations** - Efficient data processing

### Scalability
- ✅ **Horizontal scaling** - Multiple bot instances
- ✅ **Load balancing** - Railway auto-scaling
- ✅ **Database optimization** - Indexed queries
- ✅ **CDN integration** - Vercel edge caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: Create GitHub issues
- **Discussions**: Use GitHub discussions
- **Email**: Contact maintainers directly

---

**🚀 Ready to automate your Threads presence!** 