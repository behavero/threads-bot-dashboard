-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES FOR THREADS BOT
-- =============================================================================
-- This file contains all RLS policies for the Threads Bot application
-- Run this after creating the tables to enable proper data isolation

-- =============================================================================
-- STEP 1: ADD USER_ID COLUMNS TO EXISTING TABLES (if not already present)
-- =============================================================================

-- Add user_id to accounts table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts' AND column_name = 'user_id') THEN
        ALTER TABLE accounts ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add user_id to captions table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'captions' AND column_name = 'user_id') THEN
        ALTER TABLE captions ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add user_id to images table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'images' AND column_name = 'user_id') THEN
        ALTER TABLE images ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- =============================================================================
-- STEP 2: ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- =============================================================================

ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- STEP 3: DROP EXISTING POLICIES (if any) TO AVOID CONFLICTS
-- =============================================================================

-- Drop existing policies for accounts
DROP POLICY IF EXISTS "Users can view own accounts" ON accounts;
DROP POLICY IF EXISTS "Users can insert own accounts" ON accounts;
DROP POLICY IF EXISTS "Users can update own accounts" ON accounts;
DROP POLICY IF EXISTS "Users can delete own accounts" ON accounts;
DROP POLICY IF EXISTS "Service role can access all accounts" ON accounts;

-- Drop existing policies for captions
DROP POLICY IF EXISTS "Users can view own captions" ON captions;
DROP POLICY IF EXISTS "Users can insert own captions" ON captions;
DROP POLICY IF EXISTS "Users can update own captions" ON captions;
DROP POLICY IF EXISTS "Users can delete own captions" ON captions;
DROP POLICY IF EXISTS "Service role can access all captions" ON captions;

-- Drop existing policies for images
DROP POLICY IF EXISTS "Users can view own images" ON images;
DROP POLICY IF EXISTS "Users can insert own images" ON images;
DROP POLICY IF EXISTS "Users can update own images" ON images;
DROP POLICY IF EXISTS "Users can delete own images" ON images;
DROP POLICY IF EXISTS "Service role can access all images" ON images;

-- Drop existing policies for posting_history
DROP POLICY IF EXISTS "Users can view own posting history" ON posting_history;
DROP POLICY IF EXISTS "Users can insert own posting history" ON posting_history;
DROP POLICY IF EXISTS "Users can update own posting history" ON posting_history;
DROP POLICY IF EXISTS "Users can delete own posting history" ON posting_history;
DROP POLICY IF EXISTS "Service role can access all posting history" ON posting_history;

-- Drop existing policies for daily_engagement
DROP POLICY IF EXISTS "Users can view own engagement data" ON daily_engagement;
DROP POLICY IF EXISTS "Users can insert own engagement data" ON daily_engagement;
DROP POLICY IF EXISTS "Users can update own engagement data" ON daily_engagement;
DROP POLICY IF EXISTS "Users can delete own engagement data" ON daily_engagement;
DROP POLICY IF EXISTS "Service role can access all engagement data" ON daily_engagement;

-- =============================================================================
-- STEP 4: CREATE RLS POLICIES
-- =============================================================================

-- =============================================================================
-- ACCOUNTS TABLE POLICIES
-- =============================================================================
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

-- =============================================================================
-- CAPTIONS TABLE POLICIES
-- =============================================================================
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

-- =============================================================================
-- IMAGES TABLE POLICIES
-- =============================================================================
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

-- =============================================================================
-- POSTING HISTORY TABLE POLICIES
-- =============================================================================
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

-- =============================================================================
-- DAILY ENGAGEMENT TABLE POLICIES
-- =============================================================================
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

-- =============================================================================
-- STEP 5: CREATE INDEXES FOR BETTER PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);

-- =============================================================================
-- VERIFICATION QUERY
-- =============================================================================
-- Run this to verify all policies are created correctly

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname; 