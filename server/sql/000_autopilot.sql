-- Autopilot System Database Migration
-- File: 000_autopilot.sql
-- Run this in your Supabase SQL editor to set up autopilot features

-- ============================================
-- 1. Add autopilot columns to accounts table
-- ============================================

-- Basic autopilot configuration
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS autopilot_enabled boolean DEFAULT false;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS cadence_minutes int DEFAULT 10;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS jitter_seconds int DEFAULT 60;

-- Scheduling and status tracking  
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_posted_at timestamptz NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS next_run_at timestamptz NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS threads_user_id text NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS connection_status text DEFAULT 'disconnected';

-- Resilience and error handling
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_caption_id int NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_error text NULL;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS error_count int DEFAULT 0;

-- ============================================
-- 2. Add use tracking to images table  
-- ============================================

ALTER TABLE images ADD COLUMN IF NOT EXISTS use_count int DEFAULT 0;

-- ============================================
-- 3. Create autopilot_locks table
-- ============================================

CREATE TABLE IF NOT EXISTS autopilot_locks (
    id SERIAL PRIMARY KEY,
    account_id int NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    locked_at timestamptz NOT NULL DEFAULT now(),
    locked_by text NOT NULL DEFAULT 'autopilot',
    expires_at timestamptz NOT NULL DEFAULT (now() + interval '5 minutes'),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================
-- 4. Create indexes for performance
-- ============================================

-- Index for efficient autopilot queries (due accounts)
CREATE INDEX IF NOT EXISTS idx_accounts_next_run ON accounts(next_run_at)
  WHERE autopilot_enabled = true;

-- Index for autopilot enabled accounts
CREATE INDEX IF NOT EXISTS idx_accounts_autopilot_enabled ON accounts(autopilot_enabled)
  WHERE autopilot_enabled = true;

-- Index for connection status
CREATE INDEX IF NOT EXISTS idx_accounts_connection_status ON accounts(connection_status);

-- Index for autopilot locks cleanup
CREATE INDEX IF NOT EXISTS idx_autopilot_locks_expires ON autopilot_locks(expires_at);

-- Index for lock lookup by account
CREATE INDEX IF NOT EXISTS idx_autopilot_locks_account ON autopilot_locks(account_id);

-- ============================================
-- 5. Add column comments for documentation
-- ============================================

COMMENT ON COLUMN accounts.autopilot_enabled IS 'Whether autopilot posting is enabled for this account';
COMMENT ON COLUMN accounts.cadence_minutes IS 'Minutes between posts (base interval)';
COMMENT ON COLUMN accounts.jitter_seconds IS 'Random seconds to add to cadence (0-this value)';
COMMENT ON COLUMN accounts.last_posted_at IS 'Timestamp of last successful post';
COMMENT ON COLUMN accounts.next_run_at IS 'Next scheduled post time';
COMMENT ON COLUMN accounts.connection_status IS 'Account connection status: connected_session, connected_official, disconnected';
COMMENT ON COLUMN accounts.last_caption_id IS 'ID of last caption used (for deduplication)';
COMMENT ON COLUMN accounts.last_error IS 'Last error message for troubleshooting';
COMMENT ON COLUMN accounts.error_count IS 'Consecutive error count for backoff logic';
COMMENT ON COLUMN images.use_count IS 'Number of times this image has been used in posts';

COMMENT ON TABLE autopilot_locks IS 'Prevents concurrent autopilot processing of the same account';
COMMENT ON COLUMN autopilot_locks.account_id IS 'Account being processed';
COMMENT ON COLUMN autopilot_locks.locked_at IS 'When the lock was acquired';
COMMENT ON COLUMN autopilot_locks.locked_by IS 'Process/service that acquired the lock';
COMMENT ON COLUMN autopilot_locks.expires_at IS 'When the lock expires (auto-cleanup)';

-- ============================================
-- 6. Enable Row Level Security (RLS) for new table
-- ============================================

ALTER TABLE autopilot_locks ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can manage all locks
CREATE POLICY "Service role can manage autopilot locks" ON autopilot_locks
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- 7. Grant permissions
-- ============================================

-- Grant service role access to autopilot_locks
GRANT ALL ON autopilot_locks TO service_role;
GRANT USAGE, SELECT ON SEQUENCE autopilot_locks_id_seq TO service_role;

-- ============================================
-- 8. Create cleanup function for expired locks
-- ============================================

CREATE OR REPLACE FUNCTION cleanup_expired_autopilot_locks()
RETURNS int
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  deleted_count int;
BEGIN
  DELETE FROM autopilot_locks 
  WHERE expires_at < now();
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  RETURN deleted_count;
END;
$$;

-- Grant execute permission on cleanup function
GRANT EXECUTE ON FUNCTION cleanup_expired_autopilot_locks() TO service_role;

-- ============================================
-- Migration Complete ✅
-- ============================================

SELECT 
  'Autopilot migration completed successfully! 🚀' as message,
  now() as completed_at;
