-- Migration: Add OAuth states table
-- Date: 2024-01-XX
-- Description: Add table for OAuth state management and CSRF protection

-- Create oauth_states table
CREATE TABLE IF NOT EXISTS oauth_states (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    state VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_oauth_states_state ON oauth_states(state);
CREATE INDEX IF NOT EXISTS idx_oauth_states_account_id ON oauth_states(account_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_created_at ON oauth_states(created_at);

-- Add RLS policies for oauth_states table
ALTER TABLE oauth_states ENABLE ROW LEVEL SECURITY;

-- Add comments for documentation
COMMENT ON TABLE oauth_states IS 'OAuth state tokens for CSRF protection';
COMMENT ON COLUMN oauth_states.account_id IS 'Account ID associated with the OAuth state';
COMMENT ON COLUMN oauth_states.state IS 'Secure random state token for OAuth flow';
COMMENT ON COLUMN oauth_states.created_at IS 'Timestamp when state was created';

-- Add provider column to accounts table if not exists
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS provider VARCHAR(50) DEFAULT 'manual';

-- Add comment for provider column
COMMENT ON COLUMN accounts.provider IS 'Authentication provider (manual, meta, etc.)';
