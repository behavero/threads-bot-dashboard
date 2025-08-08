# Threads Bot Dashboard - Deployment Guide

## 🚀 Overview

This guide covers deploying the Threads Bot Dashboard with Meta OAuth integration, automated posting, and cron scheduling.

## 📋 Prerequisites

- Meta Developer Account with Threads API access
- Supabase project with Storage bucket
- Render account for backend hosting
- Vercel account for frontend hosting

## 🔧 Environment Variables Setup

### Backend (Render) Environment Variables

Set these in your Render service dashboard:

```bash
# Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here

# Meta Threads API Configuration (SECRET - Backend Only)
META_APP_ID=1827652407826369
META_APP_SECRET=your_rotated_app_secret_here
OAUTH_REDIRECT_URI=https://threads-bot-dashboard.vercel.app/api/auth/meta/callback
APP_BASE_URL=https://threads-bot-dashboard.vercel.app
BACKEND_BASE_URL=https://threads-bot-dashboard-3.onrender.com

# Graph API Configuration
GRAPH_API_BASE_URL=https://graph.threads.net/
GRAPH_API_VERSION=v1.0

# Internal API Token (for cron jobs and webhooks)
INTERNAL_API_TOKEN=your_long_random_string_here
```

### Frontend (Vercel) Environment Variables

Set these in your Vercel project dashboard:

```bash
# Public API Configuration (Safe for client bundles)
NEXT_PUBLIC_BACKEND_URL=https://threads-bot-dashboard-3.onrender.com
NEXT_PUBLIC_META_APP_ID=1827652407826369
NEXT_PUBLIC_OAUTH_REDIRECT_URI=https://threads-bot-dashboard.vercel.app/api/auth/meta/callback
NEXT_PUBLIC_APP_BASE_URL=https://threads-bot-dashboard.vercel.app
```

## 🔐 Meta App Configuration

### 1. Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use existing app
3. Add "Threads API" product to your app
4. Configure OAuth settings

### 2. OAuth Configuration

In your Meta app settings:

**Valid OAuth Redirect URIs:**
```
https://threads-bot-dashboard.vercel.app/api/auth/meta/callback
```

**Allowed Domains:**
```
threads-bot-dashboard.vercel.app
threads-bot-dashboard-3.onrender.com
```

### 3. App Secret Rotation

⚠️ **IMPORTANT**: Rotate your app secret regularly:

1. Go to Meta App Settings → Basic
2. Click "Show" next to App Secret
3. Click "Regenerate" to create new secret
4. Update `META_APP_SECRET` in Render environment variables
5. Never commit the secret to git

## 🗄️ Database Setup

### 1. Supabase Configuration

1. Create a new Supabase project
2. Create a Storage bucket named `sessions`
3. Set up RLS policies for security
4. Get your project URL and service role key

### 2. Run Migrations

Execute these SQL migrations in your Supabase SQL editor:

```sql
-- Migration 001: Add Threads API tables
-- (See server/migrations/001_add_threads_api_tables.sql)

-- Migration 002: Add OAuth states table  
-- (See server/migrations/002_add_oauth_states_table.sql)
```

## 🚀 Deployment Steps

### Backend (Render)

1. **Connect Repository**
   - Connect your GitHub repo to Render
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python start.py`

2. **Environment Variables**
   - Add all backend environment variables listed above
   - Ensure `META_APP_SECRET` is the rotated secret

3. **Cron Jobs**
   - Add cron job: `*/5 * * * * curl -X POST https://your-app.onrender.com/scheduler/run`
   - This runs every 5 minutes to process scheduled posts

### Frontend (Vercel)

1. **Connect Repository**
   - Connect your GitHub repo to Vercel
   - Set build command: `npm run build`
   - Set output directory: `client`

2. **Environment Variables**
   - Add all frontend environment variables listed above
   - Ensure `NEXT_PUBLIC_BACKEND_URL` points to your Render backend

3. **Domain Configuration**
   - Configure custom domain if needed
   - Update OAuth redirect URIs in Meta app settings

## 🔍 Testing Deployment

### 1. Health Check

Test backend health:
```bash
curl https://your-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "meta_oauth": "configured",
  "threads_api": "available"
}
```

### 2. OAuth Flow Test

1. Go to your frontend: `https://your-app.vercel.app`
2. Navigate to Accounts page
3. Click "Connect Threads" on an account
4. Complete Meta OAuth flow
5. Verify account shows as connected

### 3. Manual Posting Test

Test posting endpoint:
```bash
curl -X POST https://your-backend.onrender.com/threads/post \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "your_account_id",
    "text": "Test post from API"
  }'
```

### 4. Scheduler Test

Test scheduler endpoint:
```bash
curl -X POST https://your-backend.onrender.com/scheduler/run
```

## 🔒 Security Checklist

- ✅ App secret rotated and not in git
- ✅ Environment variables set in deployment platforms
- ✅ OAuth redirect URIs configured correctly
- ✅ Internal API token set for webhooks
- ✅ Database RLS policies configured
- ✅ No hardcoded secrets in client code

## 🐛 Troubleshooting

### Common Issues

1. **OAuth Redirect Errors**
   - Verify redirect URI matches exactly in Meta app settings
   - Check that domain is in allowed domains list

2. **"Instagram API not available"**
   - Ensure `META_APP_SECRET` is correct and rotated
   - Check that Threads API product is added to Meta app

3. **Database Connection Errors**
   - Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
   - Check that migrations have been run

4. **Cron Jobs Not Running**
   - Verify cron job is configured in Render
   - Check that `/scheduler/run` endpoint is accessible

### Debug Endpoints

- `GET /api/health` - Overall system health
- `GET /api/debug` - Detailed system information
- `GET /scheduler/status` - Scheduler status and recent runs

## 📊 Monitoring

### Key Metrics to Monitor

1. **OAuth Success Rate**: Track successful account connections
2. **Posting Success Rate**: Monitor successful vs failed posts
3. **Scheduler Execution**: Ensure cron jobs are running
4. **API Response Times**: Monitor backend performance

### Logs to Watch

- Backend logs in Render dashboard
- Frontend logs in Vercel dashboard
- Database query logs in Supabase dashboard

## 🔄 Updates and Maintenance

### Regular Tasks

1. **Monthly**: Rotate Meta app secret
2. **Weekly**: Check cron job execution logs
3. **Daily**: Monitor posting success rates
4. **As needed**: Update dependencies and security patches

### Backup Strategy

- Database: Supabase automatic backups
- Sessions: Stored in Supabase Storage
- Configuration: Environment variables in deployment platforms
- Code: Git repository with version control 