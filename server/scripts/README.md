# Scripts & SQL Helpers

Helper scripts and SQL files for Threads Bot development and deployment.

## 📁 Files

### SQL Migrations
- **`../sql/000_autopilot.sql`** - Complete autopilot system database setup

### Seed Scripts  
- **`seed_minimal.py`** - Create minimal demo data for testing

## 🚀 Quick Start

### 1. Run Database Migration

```sql
-- In Supabase SQL Editor, run:
-- Copy and paste contents of server/sql/000_autopilot.sql
```

### 2. Seed Demo Data

```bash
cd server
python scripts/seed_minimal.py
```

This creates:
- 📝 **2 demo captions** (tech + motivation)
- 🖼️ **2 demo images** (Unsplash stock photos)
- 👤 **1 demo account** (`demo_autopilot`) with autopilot enabled
- ⚙️ **5-minute cadence** with 30s jitter
- ⏰ **Next run in 2 minutes** for immediate testing

### 3. Test Autopilot

```bash
# Start backend
python start.py

# Manual trigger (in another terminal)
curl -X POST http://localhost:5000/autopilot/tick

# Check status
curl http://localhost:5000/autopilot/status
```

## 📋 Environment Requirements

Ensure these environment variables are set:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 🔧 Script Details

### seed_minimal.py Features
- ✅ **Idempotent**: Safe to run multiple times
- 🔍 **Smart detection**: Checks for existing data
- 📊 **Verification**: Confirms successful seeding
- 📝 **Detailed logging**: Step-by-step progress
- 🛡️ **Error handling**: Graceful failure with helpful messages

### Demo Captions Created
1. **Tech/AI themed**: Building with AI, innovation focus
2. **Motivation themed**: Monday motivation, goal setting

### Demo Images Created  
1. **Tech workspace**: Clean, modern workspace scene
2. **Mountain sunrise**: Inspirational landscape for motivation posts

### Demo Account Setup
- **Username**: `demo_autopilot`
- **Connection**: `connected_session` (ready for posting)
- **Autopilot**: Enabled with 5-minute cadence
- **Next run**: 2 minutes after creation
- **Error tracking**: Clean slate (error_count: 0)

## 🎯 Usage in Development

Perfect for:
- 🧪 **Testing autopilot logic**
- 🔧 **Frontend development** 
- 🐛 **Debugging posting flows**
- 📊 **Dashboard validation**
- 🚀 **Demo environments**

## 🔄 Reset Data

To start fresh:

```sql
-- Clear seeded data (in Supabase SQL Editor)
DELETE FROM posting_history WHERE account_id IN (SELECT id FROM accounts WHERE username = 'demo_autopilot');
DELETE FROM accounts WHERE username = 'demo_autopilot';
DELETE FROM captions WHERE category IN ('tech', 'motivation');
DELETE FROM images WHERE filename IN ('tech_workspace.jpg', 'mountain_sunrise.jpg');
```

Then re-run the seed script!
