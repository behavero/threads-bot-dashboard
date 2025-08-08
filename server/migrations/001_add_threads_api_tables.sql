-- Migration: Add Threads API tables
-- Date: 2024-01-XX
-- Description: Add tables for official Threads API integration

-- Update accounts table to support Threads API
ALTER TABLE accounts 
ADD COLUMN IF NOT EXISTS threads_user_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS ig_user_id VARCHAR(255);

-- Create tokens table for OAuth tokens
CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    scopes TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create scheduled_posts table
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    caption_id INTEGER REFERENCES captions(id),
    image_id INTEGER REFERENCES images(id),
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tokens_account_id ON tokens(account_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_account_id ON scheduled_posts(account_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_for ON scheduled_posts(scheduled_for);

-- Add RLS policies for tokens table
ALTER TABLE tokens ENABLE ROW LEVEL SECURITY;

-- Add RLS policies for scheduled_posts table
ALTER TABLE scheduled_posts ENABLE ROW LEVEL SECURITY;

-- Create storage bucket for OAuth tokens (if using Supabase Storage)
-- Note: This would be done via Supabase dashboard or API
-- INSERT INTO storage.buckets (id, name, public) VALUES ('oauth-tokens', 'oauth-tokens', false);

-- Update posting_history table to support Threads API
ALTER TABLE posting_history 
ADD COLUMN IF NOT EXISTS thread_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS api_type VARCHAR(50) DEFAULT 'threads_api';

-- Add comments for documentation
COMMENT ON TABLE tokens IS 'OAuth tokens for Threads API authentication';
COMMENT ON TABLE scheduled_posts IS 'Scheduled posts for automated posting';
COMMENT ON COLUMN accounts.threads_user_id IS 'Threads user ID from OAuth';
COMMENT ON COLUMN accounts.ig_user_id IS 'Instagram user ID (if different from Threads)';
COMMENT ON COLUMN posting_history.thread_id IS 'Thread ID from Threads API';
COMMENT ON COLUMN posting_history.api_type IS 'API type used for posting (threads_api, instagrapi, etc.)';
