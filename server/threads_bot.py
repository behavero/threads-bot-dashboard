import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict
from database import DatabaseManager

try:
    from threads_api_real import RealThreadsAPI
    print("✅ Using real Threads API with instagrapi")
    ThreadsAPI = RealThreadsAPI
except ImportError as e:
    print(f"⚠️ Real Threads API not available: {e}")
    print("💡 Falling back to mock mode")
    try:
        from threads_api_mock import ThreadsAPI
        print("✅ Using mock Threads API for development")
    except ImportError:
        print("❌ No Threads API available")
        ThreadsAPI = None

class ThreadsBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.api_instances = {}  # Store API instances per account
        self.posting_interval = 5 * 60  # 5 minutes
        
    def initialize(self):
        """Initialize the bot"""
        print("🤖 Initializing Threads Bot...")
        
        # Test database connection
        try:
            accounts = self.db.get_active_accounts()
            print(f"✅ Database connection successful - {len(accounts)} accounts found")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
        
        print("✅ Bot initialized successfully")
        return True
    
    async def login_account(self, username: str, password: str) -> Optional[ThreadsAPI]:
        """Login to a Threads account"""
        if not ThreadsAPI:
            print(f"⚠️ No Threads API available for {username}")
            return None
        
        try:
            # Use real Threads API with instagrapi
            api = ThreadsAPI(use_instagrapi=True)
            success = await api.login(username, password)
            
            if success:
                print(f"✅ Successfully logged in to {username}")
                return api
            else:
                print(f"❌ Login failed for {username}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to login {username}: {e}")
            return None
    
    def post_content(self, account: Dict, caption: Dict, image: Dict) -> bool:
        """Post content using Threads API"""
        account_id = account['id']
        username = account['username']
        
        print(f"📝 Posting for {username}...")
        
        try:
            # Get or create API instance for this account
            if username not in self.api_instances:
                api = self.login_account(username, account['password'])
                if api:
                    self.api_instances[username] = api
                else:
                    self.db.add_posting_record(
                        account_id, caption['id'], image['id'] if image else None
                    )
                    return False
            
            api = self.api_instances[username]
            
            # Post content
            if image:
                # Post with image
                result = api.post_with_image(
                    caption['text'],
                    image['url']
                )
            else:
                # Post text only
                result = api.post(caption['text'])
            
            if result:
                print(f"✅ Posted successfully for {username}")
                
                # Mark content as used
                self.db.mark_caption_used(caption['id'])
                if image:
                    self.db.mark_image_used(image['id'])
                
                # Update account
                self.db.update_account_last_posted(account_id)
                
                # Record success
                self.db.add_posting_record(
                    account_id, caption['id'], image['id'] if image else None
                )
                
                return True
            else:
                print(f"❌ Failed to post for {username}")
                self.db.add_posting_record(
                    account_id, caption['id'], image['id'] if image else None
                )
                return False
                
        except Exception as e:
            print(f"❌ Error posting for {username}: {e}")
            self.db.add_posting_record(
                account_id, caption['id'], image['id'] if image else None
            )
            return False
    
    def should_post_for_account(self, account: Dict) -> bool:
        """Check if account should post based on timing"""
        if not account.get('last_posted'):
            return True
        
        last_posted = datetime.fromisoformat(account['last_posted'])
        time_since_last = datetime.now() - last_posted
        
        return time_since_last.total_seconds() >= self.posting_interval
    
    def run_posting_cycle(self):
        """Run one posting cycle for all active accounts"""
        print(f"🔄 Running posting cycle at {datetime.now()}")
        
        # Get active accounts
        accounts = self.db.get_active_accounts()
        if not accounts:
            print("⚠️ No active accounts found")
            return
        
        print(f"📊 Found {len(accounts)} active accounts")
        
        for account in accounts:
            if not self.should_post_for_account(account):
                print(f"⏰ {account['username']} posted recently, skipping")
                continue
            
            # Get content
            caption = self.db.get_unused_caption()
            image = self.db.get_unused_image()
            
            if not caption:
                print("⚠️ No unused captions available")
                continue
            
            # Post content
            self.post_content(account, caption, image)
            
            # Add delay between accounts
            time.sleep(random.uniform(30, 60))
    
    def run_continuously(self):
        """Run the bot continuously"""
        print("🚀 Starting Threads Bot...")
        
        if not self.initialize():
            print("❌ Failed to initialize bot")
            return
        
        print("✅ Bot is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                self.run_posting_cycle()
                
                # Wait for next cycle
                print(f"⏳ Waiting {self.posting_interval} seconds until next cycle...")
                time.sleep(self.posting_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
            raise 