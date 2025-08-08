# Threads API Integration Deployment Guide

## Overview

This guide covers the deployment of the Threads API integration, which replaces the previous `instagrapi` and `threads-api` approach with Meta's official Threads API using OAuth authentication.

## Prerequisites

### 1. Meta App Configuration

1. **Create Meta App**: Go to [Meta for Developers](https://developers.facebook.com/)
2. **Add Threads API**: In your app, add the Threads API product
3. **Configure OAuth**: Set up OAuth redirect URIs:
   - `https://threads-bot-dashboard.vercel.app/api/auth/meta/callback`
4. **Enable Required Scopes**:
   - `threads_basic`
   - `threads_content_publish`
   - `threads_manage_insights`
   - `threads_manage_replies`
   - `threads_read_replies`
   - `threads_keyword_search`
   - `threads_manage_mentions`
   - `threads_delete`
   - `threads_location_tagging`
   - `threads_profile_discovery`

### 2. Environment Variables

#### Backend (Render)

```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

# Meta Threads API
META_APP_ID=1827652407826369
META_APP_SECRET=50d1453dc80f9b6cc06c9e3f70c50109
OAUTH_REDIRECT_URI=https://threads-bot-dashboard.vercel.app/api/auth/meta/callback
APP_BASE_URL=https://threads-bot-dashboard.vercel.app
BACKEND_BASE_URL=https://threads-bot-dashboard-3.onrender.com

# Graph API
GRAPH_API_BASE_URL=https://graph.threads.net/
GRAPH_API_VERSION=v1.0

# Internal API
INTERNAL_API_TOKEN=your_long_random_string
```

#### Frontend (Vercel)

```bash
# API Configuration
NEXT_PUBLIC_API_BASE=https://threads-bot-dashboard-3.onrender.com
NEXT_PUBLIC_META_APP_ID=1827652407826369
NEXT_PUBLIC_OAUTH_REDIRECT_URI=https://threads-bot-dashboard.vercel.app/api/auth/meta/callback
NEXT_PUBLIC_APP_BASE_URL=https://threads-bot-dashboard.vercel.app
```

## Database Setup

### 1. Run Migration

Execute the migration script to create new tables:

```sql
-- Run server/migrations/001_add_threads_api_tables.sql
```

### 2. Verify Tables

Check that the following tables exist:
- `tokens` (for OAuth tokens)
- `scheduled_posts` (for automated posting)
- Updated `accounts` table with `threads_user_id` column
- Updated `posting_history` table with `thread_id` column

## Deployment Steps

### 1. Backend Deployment (Render)

1. **Update Code**: Push the new code with Threads API integration
2. **Set Environment Variables**: Add all required environment variables
3. **Deploy**: Trigger a new deployment
4. **Verify Health Check**: Test `/api/health` endpoint

### 2. Frontend Deployment (Vercel)

1. **Update Code**: Push the new frontend code
2. **Set Environment Variables**: Add frontend environment variables
3. **Deploy**: Trigger a new deployment
4. **Test OAuth Flow**: Verify Connect Threads buttons work

### 3. Cron Job Setup (Render)

Set up a cron job to run every 5 minutes:

```bash
*/5 * * * * curl -X POST https://threads-bot-dashboard-3.onrender.com/scheduler/run
```

## Cron Configuration

### Render Cron Jobs

The application uses Render's cron job feature to automatically run the scheduler. Configure the following cron jobs in your Render dashboard:

1. **Scheduler Job** (every 5 minutes):
   - URL: `https://your-app-name.onrender.com/scheduler/run`
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Body: `{}`
   - Timeout: 300 seconds
   - Retries: 3

2. **Health Check** (every 10 minutes):
   - URL: `https://your-app-name.onrender.com/api/health`
   - Method: `GET`
   - Timeout: 60 seconds
   - Retries: 2

### Manual Cron Setup

If you prefer to set up cron manually, add these entries to your server's crontab:

```bash
# Run scheduler every 5 minutes
*/5 * * * * curl -X POST https://your-app-name.onrender.com/scheduler/run -H "Content-Type: application/json" -d '{}'

# Health check every 10 minutes
*/10 * * * * curl -X GET https://your-app-name.onrender.com/api/health
```

### Cron Job Monitoring

Monitor your cron jobs through:
- Render Dashboard → Your App → Cron Jobs
- Application logs for scheduler execution
- Database `scheduled_posts` table for post status

## Testing

### 1. Run Test Script

```bash
cd server
python test_threads_api.py
```

### 2. Manual Testing

1. **Health Check**: `GET /api/health`
2. **OAuth Start**: `POST /auth/meta/start`
3. **Threads Post**: `POST /threads/post`
4. **Scheduler Status**: `GET /scheduler/status`

### 3. Frontend Testing

1. **Accounts Page**: Verify Connect Threads buttons appear
2. **OAuth Flow**: Test connecting an account
3. **Posting**: Test manual posting via Threads API
4. **Scheduling**: Test scheduling posts

## Monitoring

### 1. Health Checks

Monitor the health endpoint for service status:
- Database connectivity
- Meta OAuth service availability
- Threads API service availability

### 2. Logs

Check Render logs for:
- OAuth flow errors
- Posting failures
- Scheduler issues

### 3. Metrics

Track:
- Successful OAuth connections
- Posts published via Threads API
- Scheduled posts completed
- Failed operations

## Troubleshooting

### Common Issues

1. **OAuth Errors**:
   - Check Meta app configuration
   - Verify redirect URIs
   - Ensure required scopes are enabled

2. **Posting Failures**:
   - Check account connection status
   - Verify token validity
   - Review Threads API error messages

3. **Scheduler Issues**:
   - Check cron job configuration
   - Verify database connectivity
   - Review scheduled posts status

### Debug Endpoints

- `GET /api/health` - Service health
- `GET /auth/meta/status/{account_id}` - OAuth status
- `GET /scheduler/status` - Scheduler status
- `POST /threads/test/{account_id}` - Test account connection

## Migration from Old System

### 1. Data Migration

- Existing accounts remain in database
- New OAuth connections will be added
- Old posting history is preserved

### 2. Feature Parity

- ✅ Manual posting via Threads API
- ✅ Automated scheduling
- ✅ Account management
- ✅ OAuth authentication
- ✅ Token management

### 3. New Features

- 🔒 Secure OAuth authentication
- 📊 Official Threads API insights
- 🚀 Improved reliability
- 📱 Better error handling

## Security Considerations

1. **Token Storage**: OAuth tokens stored securely in database
2. **HTTPS Only**: All OAuth flows use HTTPS
3. **Token Refresh**: Automatic token refresh handling
4. **Access Control**: Proper RLS policies on new tables

## Support

For issues with the Threads API integration:

1. Check the logs for detailed error messages
2. Verify Meta app configuration
3. Test with the provided test script
4. Review the troubleshooting section above 