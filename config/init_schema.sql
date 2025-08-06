-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT NOT NULL UNIQUE,
  email TEXT,
  password TEXT NOT NULL,
  description TEXT,
  posting_config JSONB DEFAULT '{}',
  fingerprint_config JSONB DEFAULT '{}',
  active BOOLEAN DEFAULT true,
  shadowban BOOLEAN DEFAULT false,
  last_posted TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Captions table
CREATE TABLE IF NOT EXISTS captions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  category VARCHAR(100) DEFAULT 'general',
  tags TEXT[] DEFAULT '{}',
  used BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  url TEXT NOT NULL,
  size INTEGER,
  type VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Posting history table
CREATE TABLE IF NOT EXISTS posting_history (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  caption_id UUID REFERENCES captions(id) ON DELETE SET NULL,
  image_id UUID REFERENCES images(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  error_message TEXT,
  posted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(active);
CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);
CREATE INDEX IF NOT EXISTS idx_captions_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_captions_category ON captions(category);
CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
CREATE INDEX IF NOT EXISTS idx_captions_created_at ON captions(created_at);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);
CREATE INDEX IF NOT EXISTS idx_posting_history_account ON posting_history(account_id);
CREATE INDEX IF NOT EXISTS idx_posting_history_status ON posting_history(status);

-- Enable Row Level Security
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for accounts
CREATE POLICY "Allow users to view their own accounts" ON accounts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Allow users to insert their own accounts" ON accounts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to update their own accounts" ON accounts
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Allow users to delete their own accounts" ON accounts
  FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for captions
CREATE POLICY "Allow users to view their own captions" ON captions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Allow users to insert their own captions" ON captions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to update their own captions" ON captions
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Allow users to delete their own captions" ON captions
  FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for images
CREATE POLICY "Allow users to view their own images" ON images
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Allow users to insert their own images" ON images
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to update their own images" ON images
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Allow users to delete their own images" ON images
  FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for posting_history
CREATE POLICY "Allow users to view their own posting history" ON posting_history
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM accounts WHERE accounts.id = posting_history.account_id AND accounts.user_id = auth.uid()
  ));

CREATE POLICY "Allow users to insert their own posting history" ON posting_history
  FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM accounts WHERE accounts.id = posting_history.account_id AND accounts.user_id = auth.uid()
  ));

CREATE POLICY "Allow users to update their own posting history" ON posting_history
  FOR UPDATE USING (EXISTS (
    SELECT 1 FROM accounts WHERE accounts.id = posting_history.account_id AND accounts.user_id = auth.uid()
  ));

CREATE POLICY "Allow users to delete their own posting history" ON posting_history
  FOR DELETE USING (EXISTS (
    SELECT 1 FROM accounts WHERE accounts.id = posting_history.account_id AND accounts.user_id = auth.uid()
  )); 