-- Migration script to update existing database schema
-- Run this in your Supabase SQL editor

-- Add missing columns to captions table
ALTER TABLE captions 
ADD COLUMN IF NOT EXISTS category VARCHAR(100) DEFAULT 'general',
ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add missing columns to images table
ALTER TABLE images 
ADD COLUMN IF NOT EXISTS used BOOLEAN DEFAULT FALSE;

-- Rename date column to post_date in daily_engagement table
ALTER TABLE daily_engagement 
RENAME COLUMN IF EXISTS date TO post_date;

-- Update existing captions to have default values
UPDATE captions 
SET 
    category = COALESCE(category, 'general'),
    tags = COALESCE(tags, '{}'),
    updated_at = COALESCE(updated_at, created_at)
WHERE category IS NULL OR tags IS NULL OR updated_at IS NULL;

-- Update existing images to have default values
UPDATE images 
SET used = COALESCE(used, FALSE)
WHERE used IS NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_captions_category ON captions(category);
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);

-- Enable RLS on all tables (if not already enabled)
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own captions" ON captions;
DROP POLICY IF EXISTS "Users can insert own captions" ON captions;
DROP POLICY IF EXISTS "Users can update own captions" ON captions;
DROP POLICY IF EXISTS "Users can delete own captions" ON captions;
DROP POLICY IF EXISTS "Service role can access all captions" ON captions;

DROP POLICY IF EXISTS "Users can view own images" ON images;
DROP POLICY IF EXISTS "Users can insert own images" ON images;
DROP POLICY IF EXISTS "Users can update own images" ON images;
DROP POLICY IF EXISTS "Users can delete own images" ON images;
DROP POLICY IF EXISTS "Service role can access all images" ON images;

-- Recreate RLS policies for captions
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

-- Recreate RLS policies for images
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

-- Temporarily allow public access for debugging (remove this later)
CREATE POLICY "Allow public access for debugging" ON captions
    FOR ALL USING (true);

CREATE POLICY "Allow public access for debugging" ON images
    FOR ALL USING (true);

-- Verify the migration
SELECT 
    'captions' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN category IS NOT NULL THEN 1 END) as with_category,
    COUNT(CASE WHEN tags IS NOT NULL THEN 1 END) as with_tags
FROM captions
UNION ALL
SELECT 
    'images' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN used IS NOT NULL THEN 1 END) as with_used_flag,
    0 as with_tags
FROM images;
