#!/usr/bin/env python3
"""
Setup script for Supabase database
This script creates all required tables and RLS policies for the Threads Bot
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_supabase():
    """Setup Supabase database with tables and RLS policies"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Setting up Supabase database...")
    
    # SQL commands to create tables and policies
    sql_commands = [
        # Create accounts table
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
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
        """,
        
        # Create captions table
        """
        CREATE TABLE IF NOT EXISTS captions (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create images table
        """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            filename VARCHAR(255),
            url TEXT,
            size INTEGER,
            type VARCHAR(100),
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create posting_history table
        """
        CREATE TABLE IF NOT EXISTS posting_history (
            id SERIAL PRIMARY KEY,
            account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
            caption_id INTEGER REFERENCES captions(id) ON DELETE SET NULL,
            image_id INTEGER REFERENCES images(id) ON DELETE SET NULL,
            status VARCHAR(50) NOT NULL,
            error_message TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create daily_engagement table
        """
        CREATE TABLE IF NOT EXISTS daily_engagement (
            id SERIAL PRIMARY KEY,
            account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
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
        """,
        
        # Create indexes
        """
        CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
        CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
        CREATE INDEX IF NOT EXISTS idx_captions_used ON captions(used);
        CREATE INDEX IF NOT EXISTS idx_captions_user_id ON captions(user_id);
        CREATE INDEX IF NOT EXISTS idx_images_used ON images(used);
        CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
        CREATE INDEX IF NOT EXISTS idx_posting_history_account ON posting_history(account_id);
        CREATE INDEX IF NOT EXISTS idx_posting_history_status ON posting_history(status);
        CREATE INDEX IF NOT EXISTS idx_daily_engagement_account_date ON daily_engagement(account_id, date);
        CREATE INDEX IF NOT EXISTS idx_daily_engagement_date ON daily_engagement(date);
        """,
        
        # Enable RLS on all tables
        """
        ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE captions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE images ENABLE ROW LEVEL SECURITY;
        ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
        ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;
        """,
        
        # Drop existing policies to avoid conflicts
        """
        DROP POLICY IF EXISTS "Users can view own accounts" ON accounts;
        DROP POLICY IF EXISTS "Users can insert own accounts" ON accounts;
        DROP POLICY IF EXISTS "Users can update own accounts" ON accounts;
        DROP POLICY IF EXISTS "Users can delete own accounts" ON accounts;
        DROP POLICY IF EXISTS "Service role can access all accounts" ON accounts;
        
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
        
        DROP POLICY IF EXISTS "Users can view own posting history" ON posting_history;
        DROP POLICY IF EXISTS "Users can insert own posting history" ON posting_history;
        DROP POLICY IF EXISTS "Users can update own posting history" ON posting_history;
        DROP POLICY IF EXISTS "Users can delete own posting history" ON posting_history;
        DROP POLICY IF EXISTS "Service role can access all posting history" ON posting_history;
        
        DROP POLICY IF EXISTS "Users can view own daily engagement" ON daily_engagement;
        DROP POLICY IF EXISTS "Users can insert own daily engagement" ON daily_engagement;
        DROP POLICY IF EXISTS "Users can update own daily engagement" ON daily_engagement;
        DROP POLICY IF EXISTS "Users can delete own daily engagement" ON daily_engagement;
        DROP POLICY IF EXISTS "Service role can access all daily engagement" ON daily_engagement;
        """,
        
        # Create RLS policies for accounts
        """
        CREATE POLICY "Users can view own accounts" ON accounts
            FOR SELECT USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can insert own accounts" ON accounts
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        
        CREATE POLICY "Users can update own accounts" ON accounts
            FOR UPDATE USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can delete own accounts" ON accounts
            FOR DELETE USING (auth.uid() = user_id);
        
        CREATE POLICY "Service role can access all accounts" ON accounts
            FOR ALL USING (auth.role() = 'service_role');
        """,
        
        # Create RLS policies for captions
        """
        CREATE POLICY "Users can view own captions" ON captions
            FOR SELECT USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can insert own captions" ON captions
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        
        CREATE POLICY "Users can update own captions" ON captions
            FOR UPDATE USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can delete own captions" ON captions
            FOR DELETE USING (auth.uid() = user_id);
        
        CREATE POLICY "Service role can access all captions" ON captions
            FOR ALL USING (auth.role() = 'service_role');
        """,
        
        # Create RLS policies for images
        """
        CREATE POLICY "Users can view own images" ON images
            FOR SELECT USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can insert own images" ON images
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        
        CREATE POLICY "Users can update own images" ON images
            FOR UPDATE USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can delete own images" ON images
            FOR DELETE USING (auth.uid() = user_id);
        
        CREATE POLICY "Service role can access all images" ON images
            FOR ALL USING (auth.role() = 'service_role');
        """,
        
        # Create RLS policies for posting_history
        """
        CREATE POLICY "Users can view own posting history" ON posting_history
            FOR SELECT USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id));
        
        CREATE POLICY "Users can insert own posting history" ON posting_history
            FOR INSERT WITH CHECK (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id));
        
        CREATE POLICY "Users can update own posting history" ON posting_history
            FOR UPDATE USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id));
        
        CREATE POLICY "Users can delete own posting history" ON posting_history
            FOR DELETE USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = posting_history.account_id));
        
        CREATE POLICY "Service role can access all posting history" ON posting_history
            FOR ALL USING (auth.role() = 'service_role');
        """,
        
        # Create RLS policies for daily_engagement
        """
        CREATE POLICY "Users can view own daily engagement" ON daily_engagement
            FOR SELECT USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id));
        
        CREATE POLICY "Users can insert own daily engagement" ON daily_engagement
            FOR INSERT WITH CHECK (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id));
        
        CREATE POLICY "Users can update own daily engagement" ON daily_engagement
            FOR UPDATE USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id));
        
        CREATE POLICY "Users can delete own daily engagement" ON daily_engagement
            FOR DELETE USING (auth.uid() = (SELECT user_id FROM accounts WHERE accounts.id = daily_engagement.account_id));
        
        CREATE POLICY "Service role can access all daily engagement" ON daily_engagement
            FOR ALL USING (auth.role() = 'service_role');
        """
    ]
    
    # Execute each SQL command
    for i, sql in enumerate(sql_commands, 1):
        print(f"📝 Executing SQL command {i}/{len(sql_commands)}...")
        
        try:
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"sql": sql}
            )
            
            if response.status_code == 200:
                print(f"✅ Command {i} executed successfully")
            else:
                print(f"⚠️ Command {i} returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error executing command {i}: {e}")
    
    print("\n🎉 Database setup completed!")
    print("\n📋 Next steps:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to Authentication > Settings")
    print("3. Enable 'Allow user signups'")
    print("4. Enable 'Confirm email'")
    print("5. Enable 'Allow email login'")
    print("6. Disable all third-party logins")
    print("\n7. Test the login functionality")
    
    return True

if __name__ == "__main__":
    setup_supabase() 