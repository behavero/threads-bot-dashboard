# 🚀 Threads Bot Deployment Guide

## 📋 Overview

This project is split into two independent services:

- **Frontend (Dashboard)** → Hosted on **Vercel**
- **Backend (Bot + API)** → Hosted on **Render**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │    │   Supabase      │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Dashboard)   │    │   (Bot + API)   │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Deployment Status

### ✅ Backend (Render) - WORKING
- **URL**: https://threads-bot-dashboard-3.onrender.com
- **Status**: ✅ Running successfully
- **API Endpoints**: 
  - `/` - Health check
  - `/api/status` - Bot status
  - `/api/health` - Health endpoint
  - `/api/accounts` - Account management
  - `/api/captions` - Caption management
  - `/api/images` - Image management

### 🔄 Frontend (Vercel) - NEEDS DEPLOYMENT
- **URL**: Your Vercel app URL
- **Status**: ⏳ Ready for deployment
- **Features**: Dashboard UI for bot management

## 🚀 Deployment Steps

### 1. Backend (Render) - ✅ COMPLETE

**Current Status**: Successfully deployed and running

**Environment Variables Set**:
```
SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o
```

**Features Working**:
- ✅ Bot initialization
- ✅ Database schema setup
- ✅ Mock Threads API
- ✅ API endpoints
- ✅ Background worker process

### 2. Frontend (Vercel) - 🎯 READY TO DEPLOY

#### **Step 1: Connect Repository**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `behavero/threads-bot-dashboard`

#### **Step 2: Configure Project**
- **Framework Preset**: Next.js
- **Root Directory**: `client`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

#### **Step 3: Set Environment Variables**
Add these in Vercel project settings:

```
NEXT_PUBLIC_SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o
NEXT_PUBLIC_BACKEND_URL=https://threads-bot-dashboard-3.onrender.com
```

#### **Step 4: Deploy**
Click "Deploy" and wait for the build to complete.

## 🔧 Testing the Connection

### Backend Test
Visit: https://threads-bot-dashboard-3.onrender.com/api/status
Expected response:
```json
{
  "status": "running",
  "service": "threads-bot",
  "bot_running": true,
  "timestamp": "2025-08-05T19:36:21.412309",
  "environment": "render",
  "backend_url": "https://threads-bot-dashboard-3.onrender.com"
}
```

### Frontend Test
After Vercel deployment, visit your app and check:
- ✅ Dashboard loads without errors
- ✅ Connection status shows "connected"
- ✅ Bot status shows "running"
- ✅ Can add accounts, captions, and images

## 📊 Project Structure

```
/
├── client/                 # Frontend (Vercel)
│   ├── src/app/           # Next.js app directory
│   ├── package.json       # Dependencies
│   ├── next.config.js     # Next.js config
│   └── vercel.json        # Vercel deployment
├── server/                # Backend (Render)
│   ├── start.py          # Main entry point
│   ├── database.py       # Supabase operations
│   ├── threads_bot.py    # Bot logic
│   ├── requirements.txt  # Python dependencies
│   ├── Procfile         # Render worker process
│   └── init_schema.sql  # Database schema
├── config/               # Shared config
│   └── init_schema.sql  # Database schema (copy)
└── env.example          # Environment template
```

## 🔗 API Endpoints

### Backend API (Render)
- `GET /` - Health check
- `GET /api/status` - Bot status
- `GET /api/health` - Health endpoint
- `GET /api/info` - Service information
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Add account
- `GET /api/captions` - List captions
- `POST /api/captions` - Add caption
- `GET /api/images` - List images
- `POST /api/images` - Add image

## 🛠️ Environment Variables

### Backend (Render)
```
SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o
```

### Frontend (Vercel)
```
NEXT_PUBLIC_SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o
NEXT_PUBLIC_BACKEND_URL=https://threads-bot-dashboard-3.onrender.com
```

## 🎯 Next Steps

1. **Deploy Frontend to Vercel** using the steps above
2. **Test the connection** between frontend and backend
3. **Add test accounts** via the dashboard
4. **Add captions and images** for the bot to use
5. **Monitor bot activity** through the dashboard

## 🐛 Troubleshooting

### Common Issues

1. **404 Error on Vercel**
   - Check that `NEXT_PUBLIC_BACKEND_URL` is set correctly
   - Verify the backend URL is accessible

2. **CORS Errors**
   - Backend has CORS enabled for all origins
   - Frontend makes direct API calls (no proxy)

3. **Database Connection Issues**
   - Verify Supabase credentials are correct
   - Check that database schema is initialized

4. **Bot Not Running**
   - Check Render logs for errors
   - Verify environment variables are set

## 📈 Monitoring

### Backend Health
- **URL**: https://threads-bot-dashboard-3.onrender.com/api/health
- **Status**: Should return `{"health": "ok"}`

### Frontend Health
- Visit your Vercel app URL
- Check connection status in dashboard
- Test API calls via browser console

---

**🎉 Ready for production deployment!** 