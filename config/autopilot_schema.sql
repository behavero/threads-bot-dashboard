-- Autopilot System Database Changes
-- Run this in your Supabase SQL editor

-- Add autopilot columns to accounts table
ALTER TABLE accounts 
  ADD COLUMN IF NOT EXISTS autopilot_enabled boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS cadence_minutes int DEFAULT 10,
  ADD COLUMN IF NOT EXISTS jitter_seconds int DEFAULT 60,
  ADD COLUMN IF NOT EXISTS last_posted_at timestamptz NULL,
  ADD COLUMN IF NOT EXISTS next_run_at timestamptz NULL,
  ADD COLUMN IF NOT EXISTS threads_user_id text NULL,
  ADD COLUMN IF NOT EXISTS connection_status text DEFAULT 'disconnected';

-- Create index for efficient autopilot queries
CREATE INDEX IF NOT EXISTS idx_accounts_next_run ON accounts(next_run_at)
  WHERE autopilot_enabled = true;

-- Create locks table for poor-man's locking
CREATE TABLE IF NOT EXISTS autopilot_locks (
  id text PRIMARY KEY,
  locked_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Add use_count to images table for tracking usage
ALTER TABLE images 
  ADD COLUMN IF NOT EXISTS use_count int DEFAULT 0;

-- Add comments for documentation
COMMENT ON COLUMN accounts.autopilot_enabled IS 'Whether autopilot posting is enabled for this account';
COMMENT ON COLUMN accounts.cadence_minutes IS 'Minutes between posts (base interval)';
COMMENT ON COLUMN accounts.jitter_seconds IS 'Random seconds to add to cadence (0-this value)';
COMMENT ON COLUMN accounts.last_posted_at IS 'Timestamp of last successful post';
COMMENT ON COLUMN accounts.next_run_at IS 'Next scheduled post time';
COMMENT ON COLUMN accounts.connection_status IS 'Account connection status: connected, disconnected, error';
COMMENT ON COLUMN images.use_count IS 'Number of times this image has been used in posts';
