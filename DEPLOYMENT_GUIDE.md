# Threads Bot Deployment Guide

This guide covers deploying the Threads Bot application on Render and other platforms.

## 🚀 Render Deployment

### Prerequisites

1. **Supabase Project** - Set up with all required tables and RLS policies
2. **Environment Variables** - Configure all necessary secrets
3. **Git Repository** - Code pushed to GitHub

### Environment Variables

Configure these in your Render dashboard:

#### **Backend Environment Variables:**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
FLASK_ENV=production
```

#### **Frontend Environment Variables (Vercel):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

### Deployment Steps

#### **1. Backend Deployment (Render)**

1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `threads-bot-backend`
   - **Root Directory**: `server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash deploy.sh`

3. **Environment Variables**
   - Add all backend environment variables
   - Ensure `SUPABASE_SERVICE_ROLE_KEY` is set

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

#### **2. Frontend Deployment (Vercel)**

1. **Connect Repository**
   - Go to Vercel Dashboard
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `/` (root of repository)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

3. **Environment Variables**
   - Add all frontend environment variables
   - Configure Supabase integration

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

### Health Checks

The backend includes a health check endpoint:

```bash
GET https://your-backend.onrender.com/api/status
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T12:00:00.000000",
  "version": "1.0.0"
}
```

## 🔧 Deployment Scripts

### Backend Deployment (`server/deploy.sh`)

```bash
#!/bin/bash

# Update pip to latest version
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask, supabase, aiohttp; print('All dependencies installed successfully')"

# Start the application
python start.py
```

### Frontend Build

The frontend uses standard Next.js build process:

```bash
npm install
npm run build
npm start
```

## 🛠️ Troubleshooting

### Common Issues

#### **1. Pip Update Warning**
```
[notice] A new release of pip is available: 25.1.1 -> 25.2
```
**Solution**: The deployment script automatically updates pip. This warning is harmless.

#### **2. Environment Variables Missing**
```
ValueError: Supabase credentials not configured
```
**Solution**: Ensure all environment variables are set in Render dashboard.

#### **3. RLS Policy Violations**
```
Row Level Security policy violation
```
**Solution**: Ensure RLS policies are applied to your Supabase database.

#### **4. Health Check Failing**
```
Health check failed
```
**Solution**: Check the `/api/status` endpoint is accessible and returning 200.

### Debug Commands

#### **Check Backend Status**
```bash
curl https://your-backend.onrender.com/api/status
```

#### **Check Frontend Status**
```bash
curl https://your-frontend.vercel.app
```

#### **Check Supabase Connection**
```bash
curl https://your-backend.onrender.com/api/test-env
```

## 📊 Monitoring

### Render Dashboard
- Monitor CPU, memory, and disk usage
- Check deployment logs for errors
- Set up alerts for downtime

### Vercel Dashboard
- Monitor build status and performance
- Check function execution times
- Review error logs

### Supabase Dashboard
- Monitor database performance
- Check RLS policy effectiveness
- Review authentication logs

## 🔄 Continuous Deployment

### Automatic Deployments
- **Render**: Automatically deploys on git push to main branch
- **Vercel**: Automatically deploys on git push to main branch

### Manual Deployments
```bash
# Trigger manual deployment on Render
# Go to Render dashboard → Deploy → "Manual Deploy"

# Trigger manual deployment on Vercel
# Go to Vercel dashboard → Deployments → "Redeploy"
```

## 🚨 Security Checklist

- [ ] Environment variables are set and secure
- [ ] RLS policies are applied to all tables
- [ ] Service role key is used for backend operations
- [ ] Anonymous key is used for frontend operations
- [ ] Health checks are configured and working
- [ ] HTTPS is enabled on all endpoints
- [ ] CORS is properly configured
- [ ] Rate limiting is implemented (if needed)

## 📈 Performance Optimization

### Backend
- Use connection pooling for database connections
- Implement caching for frequently accessed data
- Monitor and optimize slow queries

### Frontend
- Enable Next.js image optimization
- Use proper caching headers
- Implement lazy loading for components

## 🔍 Testing Deployment

### 1. Health Check
```bash
curl https://your-backend.onrender.com/api/status
```

### 2. Authentication Test
```bash
curl https://your-frontend.vercel.app/login
```

### 3. Database Connection Test
```bash
curl https://your-backend.onrender.com/api/test-env
```

### 4. Full Application Test
1. Visit your frontend URL
2. Create a test account
3. Upload some test content
4. Verify data isolation works

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] All code is committed and pushed to GitHub
- [ ] Environment variables are configured
- [ ] Supabase database is set up with RLS
- [ ] Dependencies are up to date

### Post-Deployment
- [ ] Health checks are passing
- [ ] Authentication is working
- [ ] Database connections are successful
- [ ] User data isolation is working
- [ ] All API endpoints are accessible

### Monitoring
- [ ] Set up error alerts
- [ ] Monitor performance metrics
- [ ] Check logs regularly
- [ ] Test user workflows

This deployment guide ensures your Threads Bot application is properly deployed and monitored on Render and Vercel. 