-- Initialize database schema for Threads Bot
-- This file creates all necessary tables

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
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
    text TEXT NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
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
    account_id INTEGER REFERENCES accounts(id),
    caption_id INTEGER REFERENCES captions(id),
    image_id INTEGER REFERENCES images(id),
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily engagement table
CREATE TABLE IF NOT EXISTS daily_engagement (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    date DATE NOT NULL,
    total_engagement INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
CREATE INDEX IF NOT EXISTS idx_images_used ON images(used);
CREATE INDEX IF NOT EXISTS idx_posting_history_account ON posting_history(account_id);
CREATE INDEX IF NOT EXISTS idx_posting_history_status ON posting_history(status);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_account_date ON daily_engagement(account_id, date);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_date ON daily_engagement(date); 