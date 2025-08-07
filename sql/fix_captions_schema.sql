-- Fix captions table schema
-- Run this in your Supabase SQL editor

-- Drop existing captions table if it exists (backup first if needed)
-- DROP TABLE IF EXISTS captions CASCADE;

-- Create captions table with proper schema
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

-- Add missing columns if table already exists
ALTER TABLE captions 
ADD COLUMN IF NOT EXISTS category VARCHAR(100) DEFAULT 'general',
ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to have default values
UPDATE captions 
SET 
    category = COALESCE(category, 'general'),
    tags = COALESCE(tags, '{}'),
    updated_at = COALESCE(updated_at, created_at)
WHERE category IS NULL OR tags IS NULL OR updated_at IS NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_category ON captions(category);
CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
CREATE INDEX IF NOT EXISTS idx_captions_created_at ON captions(created_at);

-- Enable RLS
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own captions" ON captions;
DROP POLICY IF EXISTS "Users can insert own captions" ON captions;
DROP POLICY IF EXISTS "Users can update own captions" ON captions;
DROP POLICY IF EXISTS "Users can delete own captions" ON captions;
DROP POLICY IF EXISTS "Service role can access all captions" ON captions;
DROP POLICY IF EXISTS "Allow public access for debugging" ON captions;

-- Create RLS policies
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

-- Temporarily allow public access for debugging (remove this later)
CREATE POLICY "Allow public access for debugging" ON captions
    FOR ALL USING (true);

-- Verify the schema
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'captions' 
ORDER BY ordinal_position;

-- Show sample data
SELECT 
    id,
    text,
    category,
    tags,
    used,
    created_at,
    updated_at
FROM captions 
LIMIT 5;
