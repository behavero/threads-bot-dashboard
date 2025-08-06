-- =============================================================================
-- THREADS BOT DATABASE SCHEMA
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLES
-- =============================================================================

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255),
    description TEXT,
    posting_config JSONB DEFAULT '{}',
    fingerprint_config JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'enabled',
    last_posted TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Captions table
CREATE TABLE IF NOT EXISTS captions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    size INTEGER,
    type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompts table (NEW)
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Posting history table
CREATE TABLE IF NOT EXISTS posting_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    caption_id INTEGER REFERENCES captions(id) ON DELETE CASCADE,
    image_id INTEGER REFERENCES images(id) ON DELETE CASCADE,
    posted_at TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Daily engagement table
CREATE TABLE IF NOT EXISTS daily_engagement (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    post_date DATE NOT NULL,
    total_engagement INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(account_id, post_date)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Accounts indexes
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);

-- Captions indexes
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
CREATE INDEX IF NOT EXISTS idx_captions_created_at ON captions(created_at);

-- Images indexes
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);

-- Prompts indexes (NEW)
CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_used ON prompts(used);
CREATE INDEX IF NOT EXISTS idx_prompts_created_at ON prompts(created_at);

-- Posting history indexes
CREATE INDEX IF NOT EXISTS idx_posting_history_account_id ON posting_history(account_id);
CREATE INDEX IF NOT EXISTS idx_posting_history_posted_at ON posting_history(posted_at);
CREATE INDEX IF NOT EXISTS idx_posting_history_success ON posting_history(success);

-- Daily engagement indexes
CREATE INDEX IF NOT EXISTS idx_daily_engagement_account_id ON daily_engagement(account_id);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_post_date ON daily_engagement(post_date);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

-- Accounts policies
CREATE POLICY "Users can view own accounts" ON accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own accounts" ON accounts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own accounts" ON accounts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own accounts" ON accounts FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can access all accounts" ON accounts FOR ALL USING (auth.role() = 'service_role');

-- Captions policies
CREATE POLICY "Users can view own captions" ON captions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own captions" ON captions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own captions" ON captions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own captions" ON captions FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can access all captions" ON captions FOR ALL USING (auth.role() = 'service_role');

-- Images policies
CREATE POLICY "Users can view own images" ON images FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own images" ON images FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own images" ON images FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own images" ON images FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can access all images" ON images FOR ALL USING (auth.role() = 'service_role');

-- Prompts policies (NEW)
CREATE POLICY "Users can view own prompts" ON prompts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own prompts" ON prompts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own prompts" ON prompts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own prompts" ON prompts FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can access all prompts" ON prompts FOR ALL USING (auth.role() = 'service_role');

-- Posting history policies
CREATE POLICY "Users can view own posting history" ON posting_history FOR SELECT USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id)
);
CREATE POLICY "Users can insert own posting history" ON posting_history FOR INSERT WITH CHECK (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id)
);
CREATE POLICY "Users can update own posting history" ON posting_history FOR UPDATE USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id)
);
CREATE POLICY "Users can delete own posting history" ON posting_history FOR DELETE USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id)
);
CREATE POLICY "Service role can access all posting history" ON posting_history FOR ALL USING (auth.role() = 'service_role');

-- Daily engagement policies
CREATE POLICY "Users can view own daily engagement" ON daily_engagement FOR SELECT USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id)
);
CREATE POLICY "Users can insert own daily engagement" ON daily_engagement FOR INSERT WITH CHECK (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id)
);
CREATE POLICY "Users can update own daily engagement" ON daily_engagement FOR UPDATE USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id)
);
CREATE POLICY "Users can delete own daily engagement" ON daily_engagement FOR DELETE USING (
    auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id)
);
CREATE POLICY "Service role can access all daily engagement" ON daily_engagement FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Check if tables were created successfully
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('accounts', 'captions', 'images', 'prompts', 'posting_history', 'daily_engagement')
ORDER BY table_name; 