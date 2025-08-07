#!/usr/bin/env python3
"""
Enhanced Threads Bot with Human-like Behavior
Features:
- Randomized posting intervals
- Human-like typing delays
- Content rotation and randomization
- Ban risk reduction
- Error handling and retry logic
- Account rotation and cooldowns
"""

import os
import time
import random
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('threads_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from enhanced_threads_api import EnhancedThreadsAPI as ThreadsAPI
    logger.info("✅ Using enhanced Threads API")
except ImportError:
    try:
        from threads_api_mock import ThreadsAPI
        logger.info("✅ Using mock Threads API for development")
    except ImportError:
        logger.warning("⚠️ Threads API not available, using mock mode")
        ThreadsAPI = None

@dataclass
class PostingConfig:
    """Configuration for posting behavior"""
    min_interval: int = 3600  # 1 hour minimum
    max_interval: int = 7200  # 2 hours maximum
    human_delay_min: float = 2.0  # Minimum delay between actions
    human_delay_max: float = 8.0  # Maximum delay between actions
    max_posts_per_day: int = 8
    max_posts_per_account: int = 3
    cooldown_hours: int = 6
    retry_attempts: int = 3
    success_rate_threshold: float = 0.7

class HumanBehaviorSimulator:
    """Simulates human-like behavior to reduce detection"""
    
    def __init__(self):
        self.last_action_time = None
        self.typing_speed = random.uniform(0.1, 0.3)  # seconds per character
        
    def random_delay(self, min_delay: float = 2.0, max_delay: float = 8.0):
        """Add random delay to simulate human behavior"""
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"⏳ Human delay: {delay:.2f}s")
        time.sleep(delay)
    
    def typing_delay(self, text: str):
        """Simulate typing delay based on text length"""
        typing_time = len(text) * self.typing_speed
        typing_time = min(typing_time, 5.0)  # Cap at 5 seconds
        logger.info(f"⌨️ Typing delay: {typing_time:.2f}s for {len(text)} chars")
        time.sleep(typing_time)
    
    def natural_pause(self):
        """Add natural pauses between actions"""
        pause = random.uniform(1.0, 3.0)
        logger.info(f"🤔 Natural pause: {pause:.2f}s")
        time.sleep(pause)

class ContentManager:
    """Manages content selection and rotation"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.used_content = set()
        self.content_rotation = {}
        
    def get_random_caption(self, category: str = None) -> Optional[Dict]:
        """Get a random unused caption with category filtering"""
        try:
            # Get all unused captions
            captions = self.db.get_all_captions()
            unused_captions = [c for c in captions if not c.get('used', False)]
            
            if not unused_captions:
                logger.warning("⚠️ No unused captions available")
                return None
            
            # Filter by category if specified
            if category and category != 'all':
                unused_captions = [c for c in unused_captions if c.get('category') == category]
            
            if not unused_captions:
                logger.warning(f"⚠️ No unused captions in category: {category}")
                return None
            
            # Weighted random selection (prefer newer content)
            weights = [1.0 / (i + 1) for i in range(len(unused_captions))]
            selected = random.choices(unused_captions, weights=weights, k=1)[0]
            
            logger.info(f"📝 Selected caption: {selected['text'][:50]}...")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Error selecting caption: {e}")
            return None
    
    def get_random_image(self) -> Optional[Dict]:
        """Get a random unused image"""
        try:
            images = self.db.get_all_images()
            unused_images = [i for i in images if not i.get('used', False)]
            
            if not unused_images:
                logger.warning("⚠️ No unused images available")
                return None
            
            # Random selection with slight preference for newer images
            weights = [1.0 / (i + 1) for i in range(len(unused_images))]
            selected = random.choices(unused_images, weights=weights, k=1)[0]
            
            logger.info(f"📸 Selected image: {selected['filename']}")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Error selecting image: {e}")
            return None
    
    def should_include_image(self, account_config: Dict) -> bool:
        """Decide whether to include an image based on account config"""
        # Check if account has image posting enabled
        posting_config = account_config.get('posting_config', {})
        image_probability = posting_config.get('image_probability', 0.3)
        
        return random.random() < image_probability

class AccountManager:
    """Manages account rotation and cooldowns"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.account_cooldowns = {}
        self.daily_post_counts = {}
        
    def get_available_accounts(self) -> List[Dict]:
        """Get accounts that are ready to post"""
        try:
            accounts = self.db.get_active_accounts()
            available_accounts = []
            
            for account in accounts:
                if self.can_account_post(account):
                    available_accounts.append(account)
            
            return available_accounts
            
        except Exception as e:
            logger.error(f"❌ Error getting available accounts: {e}")
            return []
    
    def can_account_post(self, account: Dict) -> bool:
        """Check if account can post based on cooldowns and limits"""
        account_id = account['id']
        username = account['username']
        
        # Check cooldown
        if account_id in self.account_cooldowns:
            cooldown_until = self.account_cooldowns[account_id]
            if datetime.now() < cooldown_until:
                logger.info(f"⏳ {username} in cooldown until {cooldown_until}")
                return False
        
        # Check daily post limit
        today = datetime.now().date()
        if account_id not in self.daily_post_counts:
            self.daily_post_counts[account_id] = {'date': today, 'count': 0}
        
        daily_data = self.daily_post_counts[account_id]
        if daily_data['date'] != today:
            daily_data['date'] = today
            daily_data['count'] = 0
        
        max_posts = account.get('posting_config', {}).get('max_posts_per_day', 8)
        if daily_data['count'] >= max_posts:
            logger.info(f"📊 {username} reached daily limit ({max_posts} posts)")
            return False
        
        # Check last posted time
        if account.get('last_posted'):
            last_posted = datetime.fromisoformat(account['last_posted'])
            min_interval = account.get('posting_config', {}).get('min_interval', 3600)
            time_since_last = datetime.now() - last_posted
            
            if time_since_last.total_seconds() < min_interval:
                logger.info(f"⏰ {username} posted recently, waiting...")
                return False
        
        return True
    
    def record_account_post(self, account: Dict):
        """Record that an account has posted"""
        account_id = account['id']
        username = account['username']
        
        # Update daily count
        if account_id not in self.daily_post_counts:
            self.daily_post_counts[account_id] = {'date': datetime.now().date(), 'count': 0}
        
        self.daily_post_counts[account_id]['count'] += 1
        
        # Set cooldown
        cooldown_hours = account.get('posting_config', {}).get('cooldown_hours', 6)
        cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)
        self.account_cooldowns[account_id] = cooldown_until
        
        logger.info(f"✅ {username} posted (daily count: {self.daily_post_counts[account_id]['count']})")

class EnhancedThreadsBot:
    """Enhanced Threads Bot with human-like behavior"""
    
    def __init__(self, config: PostingConfig = None):
        self.config = config or PostingConfig()
        self.db = DatabaseManager()
        self.human_simulator = HumanBehaviorSimulator()
        self.content_manager = ContentManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.monitor = BotMonitor()
        self.dashboard = AnalyticsDashboard(self.monitor)
        self.api_instances = {}
        self.success_count = 0
        self.failure_count = 0
        
    def initialize(self) -> bool:
        """Initialize the bot"""
        logger.info("🤖 Initializing Enhanced Threads Bot...")
        
        try:
            # Test database connection
            accounts = self.db.get_active_accounts()
            logger.info(f"✅ Found {len(accounts)} active accounts")
            
            # Test content availability
            captions = self.db.get_all_captions()
            images = self.db.get_all_images()
            logger.info(f"✅ Found {len(captions)} captions, {len(images)} images")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    def login_account(self, username: str, password: str) -> Optional[ThreadsAPI]:
        """Login to a Threads account with retry logic"""
        if not ThreadsAPI:
            logger.info(f"🔐 Mock login for {username}")
            return None
        
        for attempt in range(self.config.retry_attempts):
            try:
                api = ThreadsAPI()
                success = api.login(username, password)
                
                if success:
                    logger.info(f"✅ Logged in to {username}")
                    return api
                else:
                    logger.warning(f"⚠️ Login failed for {username} (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"❌ Login error for {username}: {e}")
            
            # Wait before retry
            if attempt < self.config.retry_attempts - 1:
                time.sleep(random.uniform(5, 15))
        
        logger.error(f"❌ Failed to login {username} after {self.config.retry_attempts} attempts")
        return None
    
    def post_content(self, account: Dict, caption: Dict, image: Dict = None) -> bool:
        """Post content with human-like behavior"""
        account_id = account['id']
        username = account['username']
        
        logger.info(f"📝 Starting post for {username}...")
        start_time = time.time()
        
        try:
            # Get or create API instance
            if username not in self.api_instances:
                api = self.login_account(username, account['password'])
                if api:
                    self.api_instances[username] = api
                else:
                    self.monitor.record_error(username, "login_failed", "Failed to login")
                    self.record_failure(account_id, caption['id'], image['id'] if image else None, "Login failed")
                    return False
            
            api = self.api_instances[username]
            
            # Human-like behavior simulation
            self.human_simulator.natural_pause()
            
            # Simulate typing the caption
            self.human_simulator.typing_delay(caption['text'])
            
            # Post content
            if image:
                logger.info(f"📸 Posting with image for {username}")
                result = api.post_with_image(caption['text'], image['url'])
            else:
                logger.info(f"📝 Posting text only for {username}")
                result = api.post(caption['text'])
            
            # Add post-action delay
            self.human_simulator.random_delay(1.0, 3.0)
            
            response_time = time.time() - start_time
            
            if result:
                logger.info(f"✅ Posted successfully for {username}")
                
                # Mark content as used
                self.db.mark_caption_used(caption['id'])
                if image:
                    self.db.mark_image_used(image['id'])
                
                # Update account
                self.db.update_account_last_posted(account_id)
                self.account_manager.record_account_post(account)
                
                # Record success with monitoring
                self.record_success(account_id, caption['id'], image['id'] if image else None)
                self.monitor.record_post_attempt(username, True, response_time)
                
                return True
            else:
                logger.error(f"❌ Failed to post for {username}")
                self.monitor.record_error(username, "api_error", "API post failed")
                self.record_failure(account_id, caption['id'], image['id'] if image else None, "API post failed")
                self.monitor.record_post_attempt(username, False, response_time)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting for {username}: {e}")
            self.monitor.record_error(username, "exception", str(e))
            self.record_failure(account_id, caption['id'], image['id'] if image else None, str(e))
            self.monitor.record_post_attempt(username, False, time.time() - start_time)
            return False
    
    def record_success(self, account_id: str, caption_id: str, image_id: str = None):
        """Record successful post"""
        self.success_count += 1
        self.db.add_posting_record(account_id, caption_id, image_id)
    
    def record_failure(self, account_id: str, caption_id: str, image_id: str = None, error: str = None):
        """Record failed post"""
        self.failure_count += 1
        self.db.add_posting_record(account_id, caption_id, image_id)
    
    def run_posting_cycle(self):
        """Run one posting cycle with enhanced logic"""
        logger.info(f"🔄 Running enhanced posting cycle at {datetime.now()}")
        
        # Get available accounts
        available_accounts = self.account_manager.get_available_accounts()
        if not available_accounts:
            logger.info("⚠️ No accounts available for posting")
            return
        
        logger.info(f"📊 Found {len(available_accounts)} available accounts")
        
        # Randomize account order
        random.shuffle(available_accounts)
        
        for account in available_accounts:
            try:
                # Get content
                caption = self.content_manager.get_random_caption()
                if not caption:
                    logger.warning("⚠️ No captions available, skipping cycle")
                    continue
                
                # Decide whether to include image
                image = None
                if self.content_manager.should_include_image(account):
                    image = self.content_manager.get_random_image()
                
                # Post content
                success = self.post_content(account, caption, image)
                
                if success:
                    logger.info(f"✅ Successfully posted for {account['username']}")
                else:
                    logger.error(f"❌ Failed to post for {account['username']}")
                
                # Add delay between accounts
                delay = random.uniform(30, 120)  # 30 seconds to 2 minutes
                logger.info(f"⏳ Waiting {delay:.1f}s before next account...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"❌ Error processing account {account['username']}: {e}")
                continue
    
    def get_next_interval(self) -> int:
        """Calculate next posting interval with randomization"""
        base_interval = random.uniform(self.config.min_interval, self.config.max_interval)
        
        # Add some randomness to avoid predictable patterns
        variation = random.uniform(0.8, 1.2)
        final_interval = int(base_interval * variation)
        
        logger.info(f"⏰ Next posting cycle in {final_interval} seconds ({final_interval/3600:.1f} hours)")
        return final_interval
    
    def run_continuously(self):
        """Run the bot continuously with enhanced monitoring"""
        logger.info("🚀 Starting Enhanced Threads Bot...")
        
        if not self.initialize():
            logger.error("❌ Failed to initialize bot")
            return
        
        logger.info("✅ Bot is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                start_time = datetime.now()
                
                # Run posting cycle
                self.run_posting_cycle()
                
                # Show dashboard
                self.dashboard.print_dashboard()
                
                # Calculate success rate
                total_posts = self.success_count + self.failure_count
                if total_posts > 0:
                    success_rate = self.success_count / total_posts
                    logger.info(f"📊 Success rate: {success_rate:.2%} ({self.success_count}/{total_posts})")
                    
                    # Adjust behavior based on success rate
                    if success_rate < self.config.success_rate_threshold:
                        logger.warning("⚠️ Low success rate, increasing delays...")
                        self.config.min_interval = min(self.config.min_interval * 1.5, 10800)  # Max 3 hours
                        self.config.max_interval = min(self.config.max_interval * 1.5, 14400)  # Max 4 hours
                
                # Export metrics periodically
                if total_posts % 10 == 0 and total_posts > 0:
                    self.monitor.export_metrics()
                
                # Wait for next cycle
                interval = self.get_next_interval()
                logger.info(f"⏳ Waiting {interval} seconds until next cycle...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
            # Export final metrics
            self.monitor.export_metrics("final_metrics.json")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            raise

def main():
    """Main entry point"""
    config = PostingConfig(
        min_interval=3600,  # 1 hour
        max_interval=7200,  # 2 hours
        human_delay_min=2.0,
        human_delay_max=8.0,
        max_posts_per_day=8,
        max_posts_per_account=3,
        cooldown_hours=6,
        retry_attempts=3,
        success_rate_threshold=0.7
    )
    
    bot = EnhancedThreadsBot(config)
    bot.run_continuously()

if __name__ == "__main__":
    main() 