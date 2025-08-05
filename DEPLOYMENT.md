# 🚀 Deployment Guide - Railway + Vercel

This guide explains how to deploy the **Enhanced Threads Bot** to Railway (backend) and Vercel (frontend) from the same Git repository.

## 🏗️ Architecture Overview

```
Git Repository
├── backend/          → Railway deployment
└── frontend/         → Vercel deployment
```

## 🚂 Railway Deployment (Backend)

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `behavero/threads-bot-dashboard`

### 2. Configure Railway Settings

**Important**: Railway will automatically detect the `backend/` directory due to our configuration.

#### Build Settings:
- **Root Directory**: `backend` (automatically set)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

#### Environment Variables:
```env
# Supabase Configuration
SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o

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

### 3. Railway Configuration Files

Railway will use these files from the `backend/` directory:
- `railway.json` - Main configuration
- `railway.toml` - Alternative configuration
- `nixpacks.toml` - Build configuration
- `requirements.txt` - Python dependencies
- `main.py` - Entry point

### 4. Deploy

Railway will automatically:
1. Detect the `backend/` directory
2. Install Python dependencies
3. Start the bot with `python main.py`
4. Monitor health at `/api/status`

## 🌐 Vercel Deployment (Frontend)

### 1. Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your repository: `behavero/threads-bot-dashboard`
4. Configure project settings

### 2. Configure Vercel Settings

**Important**: Vercel will automatically detect the `frontend/` directory due to our configuration.

#### Build Settings:
- **Framework Preset**: Next.js
- **Root Directory**: `frontend` (automatically set)
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

#### Environment Variables:
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o

# Backend API URL (replace with your Railway URL)
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
```

### 3. Vercel Configuration Files

Vercel will use these files from the `frontend/` directory:
- `vercel.json` - Main configuration
- `package.json` - Node.js dependencies
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS configuration

### 4. Deploy

Vercel will automatically:
1. Detect the `frontend/` directory
2. Install Node.js dependencies
3. Build the Next.js application
4. Deploy to Vercel's edge network

## 🔧 Directory Targeting Configuration

### Railway (.railwayignore)
```
# Ignore frontend files for Railway deployment
frontend/
node_modules/
.next/
out/
dist/
build/
*.js
*.jsx
*.ts
*.tsx
*.css
*.scss
*.sass
*.less
*.html
*.json
!package.json
!package-lock.json
!requirements.txt
!Pipfile
!Pipfile.lock
!pyproject.toml
!railway.json
!railway.toml
!nixpacks.toml
!Procfile
!runtime.txt
!render.yaml
!.railwayignore
!README.md
!*.py
!*.pyc
!__pycache__/
!*.log
!.env
!.env.local
!.env.production
!.env.development
!.env.test
!*.md
!docs/
!scripts/
!*.yaml
!*.yml
!*.toml
```

### Vercel (.vercelignore)
```
# Ignore backend files for Vercel deployment
backend/
*.py
*.pyc
__pycache__/
*.log
.env
.env.local
.env.production
.env.development
.env.test
*.md
docs/
scripts/
*.yaml
*.yml
*.toml
*.json
!package.json
!package-lock.json
!next.config.js
!tailwind.config.js
!postcss.config.js
!vercel.json
!.vercelignore
!tsconfig.json
!.eslintrc.json
!README.md
```

## 🔄 Automatic Deployment

### Railway (Backend)
- **Trigger**: Push to `main` branch
- **Directory**: `backend/`
- **Build**: `pip install -r requirements.txt`
- **Start**: `python main.py`
- **Health Check**: `/api/status`

### Vercel (Frontend)
- **Trigger**: Push to `main` branch
- **Directory**: `frontend/`
- **Build**: `npm run build`
- **Deploy**: Automatic to edge network
- **Domain**: `your-app.vercel.app`

## 🧪 Testing Deployment

### Test Railway Backend
```bash
# Check if Railway is running
curl https://your-app-name.railway.app/api/status

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "bot_status": "stopped",
  "accounts_count": 0,
  "captions_count": 0,
  "images_count": 0
}
```

### Test Vercel Frontend
```bash
# Visit your Vercel URL
https://your-app.vercel.app

# Should show the dashboard interface
```

## 🔗 Connecting Frontend to Backend

### 1. Get Railway URL
After Railway deployment, note your app URL:
```
https://your-app-name.railway.app
```

### 2. Update Vercel Environment
In Vercel dashboard, update:
```env
NEXT_PUBLIC_BACKEND_URL=https://your-app-name.railway.app
```

### 3. Test Connection
The frontend will automatically proxy API calls to the backend.

## 🐛 Troubleshooting

### Railway Issues
**Build fails:**
- Check `backend/requirements.txt` exists
- Verify Python version in `nixpacks.toml`
- Check for syntax errors in Python files

**Bot won't start:**
- Check environment variables
- Verify Supabase connection
- Review Railway logs

### Vercel Issues
**Build fails:**
- Check `frontend/package.json` exists
- Verify Node.js version
- Check for TypeScript errors

**Frontend can't connect to backend:**
- Verify `NEXT_PUBLIC_BACKEND_URL` is set
- Check CORS settings in backend
- Test backend URL directly

### Common Solutions
1. **Clear cache**: Redeploy both services
2. **Check logs**: Use Railway/Vercel dashboard
3. **Verify environment**: Check all variables are set
4. **Test locally**: Run both services locally first

## 📊 Monitoring

### Railway Monitoring
- **Logs**: Available in Railway dashboard
- **Metrics**: CPU, memory, network usage
- **Health**: Automatic health checks
- **Restarts**: Automatic on failure

### Vercel Monitoring
- **Analytics**: Page views, performance
- **Functions**: API call metrics
- **Edge**: Global performance data
- **Errors**: Automatic error tracking

## 🚀 Production Checklist

### Before Deployment
- [ ] Test locally: `cd backend && python main.py`
- [ ] Test frontend: `cd frontend && npm run dev`
- [ ] Verify environment variables
- [ ] Check database connection
- [ ] Test API endpoints

### After Deployment
- [ ] Verify Railway health check passes
- [ ] Test Vercel frontend loads
- [ ] Check API communication
- [ ] Monitor logs for errors
- [ ] Test bot functionality

---

**🎉 Your Enhanced Threads Bot is now ready for production deployment!** 