-- Initialize database schema for Threads Bot
-- This file creates all necessary tables

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    password VARCHAR(255),
    description TEXT,
    posting_config JSONB DEFAULT '{}',
    fingerprint_config JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'enabled',
    last_posted TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Captions table
CREATE TABLE IF NOT EXISTS captions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename VARCHAR(255),
    url TEXT,
    size INTEGER,
    type VARCHAR(100),
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posting history table
CREATE TABLE IF NOT EXISTS posting_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    caption_id INTEGER REFERENCES captions(id) ON DELETE SET NULL,
    image_id INTEGER REFERENCES images(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, post_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_category ON captions(category);
CREATE INDEX IF NOT EXISTS idx_images_used ON images(used);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
CREATE INDEX IF NOT EXISTS idx_posting_history_account ON posting_history(account_id);
CREATE INDEX IF NOT EXISTS idx_posting_history_status ON posting_history(status);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_account_date ON daily_engagement(account_id, post_date);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_date ON daily_engagement(post_date);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- ROW LEVEL SECURITY POLICIES
-- =============================================================================

-- Accounts table policies
-- Users can only access their own accounts
CREATE POLICY "Users can view own accounts" ON accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own accounts" ON accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own accounts" ON accounts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own accounts" ON accounts
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all accounts (for backend operations)
CREATE POLICY "Service role can access all accounts" ON accounts
    FOR ALL USING (auth.role() = 'service_role');

-- Captions table policies
-- Users can only access their own captions
CREATE POLICY "Users can view own captions" ON captions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own captions" ON captions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own captions" ON captions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own captions" ON captions
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all captions (for backend operations)
CREATE POLICY "Service role can access all captions" ON captions
    FOR ALL USING (auth.role() = 'service_role');

-- Images table policies
-- Users can only access their own images
CREATE POLICY "Users can view own images" ON images
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own images" ON images
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own images" ON images
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own images" ON images
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all images (for backend operations)
CREATE POLICY "Service role can access all images" ON images
    FOR ALL USING (auth.role() = 'service_role');

-- Posting history table policies
-- Users can only access posting history for their own accounts
CREATE POLICY "Users can view own posting history" ON posting_history
    FOR SELECT USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can insert own posting history" ON posting_history
    FOR INSERT WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can update own posting history" ON posting_history
    FOR UPDATE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can delete own posting history" ON posting_history
    FOR DELETE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

-- Service role can access all posting history (for backend operations)
CREATE POLICY "Service role can access all posting history" ON posting_history
    FOR ALL USING (auth.role() = 'service_role');

-- Daily engagement table policies
-- Users can only access engagement data for their own accounts
CREATE POLICY "Users can view own engagement data" ON daily_engagement
    FOR SELECT USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can insert own engagement data" ON daily_engagement
    FOR INSERT WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can update own engagement data" ON daily_engagement
    FOR UPDATE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can delete own engagement data" ON daily_engagement
    FOR DELETE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

-- Service role can access all engagement data (for backend operations)
CREATE POLICY "Service role can access all engagement data" ON daily_engagement
    FOR ALL USING (auth.role() = 'service_role'); 