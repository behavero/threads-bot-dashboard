-- Simple Autopilot Migration (Copy-Paste Ready)
-- Run this in Supabase SQL Editor

-- Add autopilot columns to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS autopilot_enabled boolean DEFAULT false;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS cadence_minutes int DEFAULT 10;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS jitter_seconds int DEFAULT 60;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_posted_at timestamptz NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS next_run_at timestamptz NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS threads_user_id text NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS connection_status text DEFAULT 'disconnected';
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_caption_id int NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_error text NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS error_count int DEFAULT 0;

-- Add use tracking to images table
ALTER TABLE images ADD COLUMN IF NOT EXISTS use_count int DEFAULT 0;

-- Create autopilot locks table
CREATE TABLE IF NOT EXISTS autopilot_locks (
    id SERIAL PRIMARY KEY,
    account_id int NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    locked_at timestamptz NOT NULL DEFAULT now(),
    locked_by text NOT NULL DEFAULT 'autopilot',
    expires_at timestamptz NOT NULL DEFAULT (now() + interval '5 minutes'),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_accounts_next_run ON accounts(next_run_at) WHERE autopilot_enabled = true;
CREATE INDEX IF NOT EXISTS idx_accounts_autopilot_enabled ON accounts(autopilot_enabled) WHERE autopilot_enabled = true;
CREATE INDEX IF NOT EXISTS idx_accounts_connection_status ON accounts(connection_status);
CREATE INDEX IF NOT EXISTS idx_autopilot_locks_expires ON autopilot_locks(expires_at);
CREATE INDEX IF NOT EXISTS idx_autopilot_locks_account ON autopilot_locks(account_id);

-- Enable RLS for autopilot_locks
ALTER TABLE autopilot_locks ENABLE ROW LEVEL SECURITY;

-- Policy for service role
CREATE POLICY "Service role can manage autopilot locks" ON autopilot_locks
  FOR ALL USING (auth.role() = 'service_role');

-- Grant permissions
GRANT ALL ON autopilot_locks TO service_role;
GRANT USAGE, SELECT ON SEQUENCE autopilot_locks_id_seq TO service_role;

-- Success message
SELECT 'Autopilot migration completed! 🚀' as status;
