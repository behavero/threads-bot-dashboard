#!/usr/bin/env python3
"""
Enhanced Threads Bot - Advanced Python bot for posting to Threads
Features: Anti-detection, User-Agent rotation, Random delays, Media variation,
         External configuration support, Background scheduler optimization
"""

import json
import os
import random
import asyncio
import time
import logging
import hashlib
import secrets
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging based on environment
def setup_logging():
    """Setup logging based on environment"""
    environment = os.getenv('ENVIRONMENT', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    if environment == 'production':
        # Production logging - less verbose
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('enhanced_bot.log')
            ]
        )
    else:
        # Development logging - more verbose
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('enhanced_bot.log')
            ]
        )

setup_logging()
logger = logging.getLogger(__name__)

try:
    from threads_api import ThreadsAPI
except ImportError:
    print("⚠️  threads-api not available. Install with: pip install git+https://github.com/Danie1/threads-api.git")
    print("📝 For now, the bot will run in simulation mode.")
    ThreadsAPI = None


class PostingFrequency(Enum):
    """Enum for posting frequency options"""
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_10_MINUTES = "every_10_minutes"
    EVERY_30_MINUTES = "every_30_minutes"
    EVERY_HOUR = "every_hour"
    CUSTOM = "custom"


@dataclass
class AccountConfig:
    """Data class for account configuration"""
    username: str
    email: str
    password: str
    enabled: bool = True
    description: str = ""
    max_posts_per_day: int = 288
    delay_between_posts_seconds: int = 300
    use_random_caption: bool = True
    use_random_image: bool = True
    user_agent_rotation: bool = True
    random_delays: bool = True
    media_variation: bool = True
    posting_schedule: Dict = None
    
    def __post_init__(self):
        if self.posting_schedule is None:
            self.posting_schedule = {
                "frequency": PostingFrequency.EVERY_5_MINUTES.value,
                "interval_minutes": 5,
                "timezone": "UTC",
                "start_time": "00:00",
                "end_time": "23:59"
            }


@dataclass
class BotConfig:
    """Data class for bot configuration"""
    accounts_file: str = "config/accounts.json"
    captions_file: str = "assets/captions.txt"
    images_dir: str = "assets/images/"
    config_source: str = "json"  # "json", "airtable", "database"
    airtable_api_key: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = ""
    user_agents_file: str = "config/user_agents.txt"
    proxy_list_file: str = "proxies.txt"
    session_timeout: int = 3600
    max_retries: int = 3
    retry_delay: int = 60
    anti_detection_enabled: bool = True
    fingerprint_rotation: bool = True
    device_rotation: bool = True
    
    def __post_init__(self):
        """Load configuration from environment variables"""
        # Load from environment variables if available
        self.accounts_file = os.getenv('ACCOUNTS_FILE', self.accounts_file)
        self.captions_file = os.getenv('CAPTIONS_FILE', self.captions_file)
        self.images_dir = os.getenv('IMAGES_DIR', self.images_dir)
        self.config_source = os.getenv('CONFIG_SOURCE', self.config_source)
        self.airtable_api_key = os.getenv('AIRTABLE_API_KEY', self.airtable_api_key)
        self.airtable_base_id = os.getenv('AIRTABLE_BASE_ID', self.airtable_base_id)
        self.airtable_table_name = os.getenv('AIRTABLE_TABLE_NAME', self.airtable_table_name)
        self.user_agents_file = os.getenv('USER_AGENTS_FILE', self.user_agents_file)
        self.proxy_list_file = os.getenv('PROXY_LIST_FILE', self.proxy_list_file)
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', self.session_timeout))
        self.max_retries = int(os.getenv('MAX_RETRIES', self.max_retries))
        self.retry_delay = int(os.getenv('RETRY_DELAY', self.retry_delay))
        self.anti_detection_enabled = os.getenv('ANTI_DETECTION_ENABLED', 'true').lower() == 'true'
        self.fingerprint_rotation = os.getenv('FINGERPRINT_ROTATION', 'true').lower() == 'true'
        self.device_rotation = os.getenv('DEVICE_ROTATION', 'true').lower() == 'true'


class UserAgentRotator:
    """Handles user-agent rotation for anti-detection"""
    
    def __init__(self, user_agents_file: str = "config/user_agents.txt"):
        self.user_agents_file = user_agents_file
        self.user_agents = self._load_user_agents()
        self.current_index = 0
        self.used_agents = set()
        self.agent_rotation_count = 0
    
    def _load_user_agents(self) -> List[str]:
        """Load user agents from file or use defaults"""
        try:
            with open(self.user_agents_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            # Enhanced user agents for Threads with more variety
            return [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.3 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 17_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.3 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"
            ]
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent with smart rotation"""
        # Reset if all agents have been used
        if len(self.used_agents) >= len(self.user_agents):
            self.used_agents.clear()
            self.agent_rotation_count += 1
            logger.info(f"🔄 User agent rotation #{self.agent_rotation_count}: Resetting used agents")
        
        # Get unused agents
        available_agents = [agent for agent in self.user_agents if agent not in self.used_agents]
        
        if not available_agents:
            # If no unused agents, use any agent
            available_agents = self.user_agents
        
        selected_agent = random.choice(available_agents)
        self.used_agents.add(selected_agent)
        
        return selected_agent
    
    def get_next_user_agent(self) -> str:
        """Get the next user agent in rotation"""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def get_weighted_random_user_agent(self) -> str:
        """Get a user agent with weighted randomization (prefer newer versions)"""
        # Weight newer iOS versions more heavily
        weights = []
        for agent in self.user_agents:
            if "17_0" in agent:
                weights.append(3)  # Higher weight for iOS 17
            elif "16_7" in agent:
                weights.append(2)  # Medium weight for iOS 16.7
            else:
                weights.append(1)  # Lower weight for older versions
        
        return random.choices(self.user_agents, weights=weights, k=1)[0]


class DelayManager:
    """Manages random delays for anti-detection"""
    
    def __init__(self, min_delay: int = 30, max_delay: int = 120):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_delay = 0
    
    async def random_delay(self):
        """Perform a random delay between min and max seconds"""
        delay = random.randint(self.min_delay, self.max_delay)
        logger.info(f"⏳ Random delay: {delay} seconds")
        await asyncio.sleep(delay)
        self.last_delay = delay
        return delay
    
    async def exponential_backoff(self, attempt: int, base_delay: int = 60):
        """Exponential backoff for retries"""
        delay = base_delay * (2 ** attempt)
        logger.info(f"⏳ Exponential backoff: {delay} seconds (attempt {attempt})")
        await asyncio.sleep(delay)
        return delay
    
    async def human_like_delay(self, action_type: str = "post"):
        """Simulate human-like delays based on action type"""
        if action_type == "login":
            # Login delays: 2-5 seconds
            delay = random.uniform(2, 5)
        elif action_type == "post":
            # Post delays: 3-8 seconds
            delay = random.uniform(3, 8)
        elif action_type == "browse":
            # Browse delays: 10-30 seconds
            delay = random.uniform(10, 30)
        else:
            # Default delay: 5-15 seconds
            delay = random.uniform(5, 15)
        
        logger.info(f"👤 Human-like delay ({action_type}): {delay:.1f} seconds")
        await asyncio.sleep(delay)
        return delay
    
    async def random_sleep_interval(self, min_minutes: int = 3, max_minutes: int = 6):
        """Random sleep interval between 3-6 minutes (180-360 seconds)"""
        minutes = random.randint(min_minutes, max_minutes)
        seconds = minutes * 60
        logger.info(f"😴 Random sleep interval: {minutes} minutes ({seconds} seconds)")
        await asyncio.sleep(seconds)
        return seconds


class ImageUsageTracker:
    """Tracks image usage across accounts to prevent duplicate posting"""
    
    def __init__(self):
        self.image_usage_history = {}  # image_path -> usage_data
        self.account_image_history = {}  # username -> recent_images
        self.max_account_history = 5  # Keep last 5 images per account
        self.global_cooldown = 1800  # 30 minutes global cooldown
        self.account_cooldown = 3600  # 1 hour per account cooldown
    
    def can_use_image(self, image_path: str, username: str) -> bool:
        """Check if an image can be used by this account"""
        current_time = time.time()
        
        # Check global cooldown
        if image_path in self.image_usage_history:
            last_global_use = self.image_usage_history[image_path].get('last_global_use', 0)
            if current_time - last_global_use < self.global_cooldown:
                return False
        
        # Check account-specific cooldown
        if image_path in self.image_usage_history:
            account_usage = self.image_usage_history[image_path].get('account_usage', {})
            if username in account_usage:
                last_account_use = account_usage[username]
                if current_time - last_account_use < self.account_cooldown:
                    return False
        
        return True
    
    def record_image_usage(self, image_path: str, username: str):
        """Record that an image was used by an account"""
        current_time = time.time()
        
        # Initialize image history if not exists
        if image_path not in self.image_usage_history:
            self.image_usage_history[image_path] = {
                'last_global_use': current_time,
                'account_usage': {},
                'total_uses': 0
            }
        
        # Update global usage
        self.image_usage_history[image_path]['last_global_use'] = current_time
        self.image_usage_history[image_path]['total_uses'] += 1
        
        # Update account-specific usage
        if 'account_usage' not in self.image_usage_history[image_path]:
            self.image_usage_history[image_path]['account_usage'] = {}
        self.image_usage_history[image_path]['account_usage'][username] = current_time
        
        # Update account history
        if username not in self.account_image_history:
            self.account_image_history[username] = []
        
        # Add to account history and maintain max size
        self.account_image_history[username].append(image_path)
        if len(self.account_image_history[username]) > self.max_account_history:
            self.account_image_history[username].pop(0)
        
        logger.info(f"📸 Recorded image usage: {image_path} by {username}")
    
    def get_image_stats(self, image_path: str) -> Dict:
        """Get usage statistics for an image"""
        if image_path not in self.image_usage_history:
            return {
                'total_uses': 0,
                'last_used': None,
                'account_count': 0,
                'available': True
            }
        
        stats = self.image_usage_history[image_path]
        current_time = time.time()
        
        return {
            'total_uses': stats['total_uses'],
            'last_used': stats['last_global_use'],
            'account_count': len(stats['account_usage']),
            'available': current_time - stats['last_global_use'] >= self.global_cooldown
        }
    
    def get_available_images(self, images: List[Path], username: str) -> List[Path]:
        """Get list of images available for use by this account"""
        available_images = []
        
        for img in images:
            if self.can_use_image(str(img), username):
                available_images.append(img)
        
        return available_images
    
    def cleanup_old_records(self, max_age_hours: int = 24):
        """Clean up old usage records to prevent memory bloat"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Clean up image usage history
        images_to_remove = []
        for image_path, usage_data in self.image_usage_history.items():
            if current_time - usage_data['last_global_use'] > max_age_seconds:
                images_to_remove.append(image_path)
        
        for image_path in images_to_remove:
            del self.image_usage_history[image_path]
        
        # Clean up account history
        for username in list(self.account_image_history.keys()):
            # Keep only recent entries
            self.account_image_history[username] = self.account_image_history[username][-self.max_account_history:]
        
        if images_to_remove:
            logger.info(f"🧹 Cleaned up {len(images_to_remove)} old image usage records")


class MediaVariationManager:
    """Handles media variation for anti-detection"""
    
    def __init__(self, images_dir: str = "assets/images/"):
        self.images_dir = Path(images_dir)
        self.used_images = set()
        self.image_rotation_count = 0
        self.image_reuse_delays = {}  # Track when images were last used
        self.min_reuse_delay = 3600  # 1 hour minimum reuse delay
        self.image_usage_tracker = ImageUsageTracker()  # New image usage tracker
    
    def get_varied_image(self, images: List[Path], username: str = None) -> Optional[Path]:
        """Get an image with variation strategy, reuse delay, and cross-account tracking"""
        if not images:
            return None
        
        current_time = time.time()
        
        # Use image usage tracker to get available images
        if username:
            available_images = self.image_usage_tracker.get_available_images(images, username)
            if not available_images:
                logger.warning(f"⚠️  No images available for {username} due to usage restrictions")
                # Fall back to basic reuse delay check
                available_images = []
                for img in images:
                    last_used = self.image_reuse_delays.get(str(img), 0)
                    if current_time - last_used >= self.min_reuse_delay:
                        available_images.append(img)
                
                if not available_images:
                    available_images = images
                    logger.info("⚠️  No images available due to reuse delay, using any image")
        else:
            # Fallback to original logic if no username provided
            available_images = []
            for img in images:
                last_used = self.image_reuse_delays.get(str(img), 0)
                if current_time - last_used >= self.min_reuse_delay:
                    available_images.append(img)
            
            if not available_images:
                available_images = images
                logger.info("⚠️  No images available due to reuse delay, using any image")
        
        selected_image = random.choice(available_images)
        
        # Update both tracking systems
        self.image_reuse_delays[str(selected_image)] = current_time
        
        if username:
            # Record usage in the tracker
            self.image_usage_tracker.record_image_usage(str(selected_image), username)
        
        # Track usage for rotation
        self.used_images.add(selected_image)
        
        # Reset rotation if all images have been used
        if len(self.used_images) >= len(images):
            self.used_images.clear()
            self.image_rotation_count += 1
            logger.info(f"🔄 Image rotation #{self.image_rotation_count}: Resetting used images")
        
        # Periodic cleanup of old records
        if random.random() < 0.1:  # 10% chance to cleanup
            self.image_usage_tracker.cleanup_old_records()
        
        return selected_image
    
    def add_image_metadata(self, image_path: Path) -> Path:
        """Add metadata to image for variation (placeholder for future enhancement)"""
        # This could include adding EXIF data, slight modifications, etc.
        return image_path
    
    def get_content_order(self, captions: List[str], images: List[Path]) -> Dict:
        """Get varied content order to simulate human behavior"""
        content_order = {
            'caption_first': random.choice([True, False]),
            'use_hashtags': random.choice([True, False]),
            'use_mentions': random.choice([True, False]),
            'use_emojis': random.choice([True, False])
        }
        
        # Vary content length
        if captions:
            selected_caption = random.choice(captions)
            # Randomly truncate or extend caption
            if random.random() < 0.3:  # 30% chance to modify caption
                if len(selected_caption) > 100:
                    selected_caption = selected_caption[:random.randint(50, 100)]
                else:
                    selected_caption += " " + random.choice(["🔥", "💯", "✨", "🎯", "🚀"])
            
            content_order['caption'] = selected_caption
        
        return content_order


class SessionManager:
    """Manages session handling, token refresh, and rate limiting"""
    
    def __init__(self):
        self.sessions = {}  # username -> session_data
        self.rate_limits = {}  # username -> rate_limit_data
        self.shadowban_status = {}  # username -> shadowban_status
    
    def create_session(self, username: str) -> Dict:
        """Create a new session for an account"""
        session_id = hashlib.md5(f"{username}_{time.time()}_{secrets.token_hex(4)}".encode()).hexdigest()[:12]
        session_data = {
            'session_id': session_id,
            'created_at': time.time(),
            'last_used': time.time(),
            'login_attempts': 0,
            'post_attempts': 0,
            'rate_limited_until': 0,
            'shadowban_detected': False,
            'token_refresh_count': 0
        }
        self.sessions[username] = session_data
        logger.info(f"🔧 Created session for {username}: {session_id}")
        return session_data
    
    def get_session(self, username: str) -> Optional[Dict]:
        """Get existing session for an account"""
        return self.sessions.get(username)
    
    def update_session(self, username: str, **kwargs):
        """Update session data"""
        if username in self.sessions:
            self.sessions[username].update(kwargs)
            self.sessions[username]['last_used'] = time.time()
    
    def is_session_valid(self, username: str, max_age: int = 3600) -> bool:
        """Check if session is still valid"""
        session = self.get_session(username)
        if not session:
            return False
        
        age = time.time() - session['created_at']
        return age < max_age
    
    def handle_rate_limit(self, username: str, duration: int = 1800):
        """Handle rate limiting for an account"""
        self.rate_limits[username] = {
            'limited_until': time.time() + duration,
            'reason': 'rate_limit',
            'duration': duration
        }
        logger.warning(f"⚠️  Rate limit detected for {username}, waiting {duration} seconds")
    
    def is_rate_limited(self, username: str) -> bool:
        """Check if account is currently rate limited"""
        rate_limit = self.rate_limits.get(username)
        if not rate_limit:
            return False
        
        return time.time() < rate_limit['limited_until']
    
    def handle_shadowban(self, username: str, duration: int = 7200):
        """Handle shadowban detection"""
        self.shadowban_status[username] = {
            'shadowbanned_until': time.time() + duration,
            'detected_at': time.time(),
            'duration': duration
        }
        logger.error(f"🚫 Shadowban detected for {username}, waiting {duration} seconds")
    
    def is_shadowbanned(self, username: str) -> bool:
        """Check if account is shadowbanned"""
        shadowban = self.shadowban_status.get(username)
        if not shadowban:
            return False
        
        return time.time() < shadowban['shadowbanned_until']
    
    def refresh_token_if_needed(self, username: str) -> bool:
        """Check if token needs refresh and handle it"""
        session = self.get_session(username)
        if not session:
            return False
        
        # Check if token is older than 1 hour
        if time.time() - session['created_at'] > 3600:
            logger.info(f"🔄 Token refresh needed for {username}")
            session['token_refresh_count'] += 1
            session['created_at'] = time.time()
            return True
        
        return False


class RateLimitHandler:
    """Handles rate limiting and error detection"""
    
    def __init__(self):
        self.error_patterns = {
            'rate_limit': [
                'rate limit', 'too many requests', '429', 'quota exceeded',
                'temporary block', 'try again later'
            ],
            'shadowban': [
                'shadowban', 'content not visible', 'post not appearing',
                'engagement reduced', 'visibility limited'
            ],
            'auth_error': [
                'authentication', 'login failed', 'invalid credentials',
                'session expired', 'token invalid'
            ],
            'network_error': [
                'network', 'connection', 'timeout', 'dns', 'ssl'
            ]
        }
    
    def detect_error_type(self, error_message: str) -> str:
        """Detect the type of error from error message"""
        error_message = error_message.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in error_message:
                    return error_type
        
        return 'unknown'
    
    def get_retry_delay(self, error_type: str, attempt: int) -> int:
        """Get appropriate retry delay based on error type"""
        base_delays = {
            'rate_limit': 1800,  # 30 minutes
            'shadowban': 7200,   # 2 hours
            'auth_error': 300,   # 5 minutes
            'network_error': 60, # 1 minute
            'unknown': 300       # 5 minutes default
        }
        
        base_delay = base_delays.get(error_type, 300)
        return base_delay * (2 ** min(attempt, 3))  # Cap exponential growth
    
    def should_retry(self, error_type: str, attempt: int) -> bool:
        """Determine if retry should be attempted"""
        max_attempts = {
            'rate_limit': 1,     # Don't retry rate limits
            'shadowban': 1,      # Don't retry shadowbans
            'auth_error': 3,     # Retry auth errors up to 3 times
            'network_error': 5,  # Retry network errors up to 5 times
            'unknown': 2         # Retry unknown errors up to 2 times
        }
        
        return attempt < max_attempts.get(error_type, 2)


class ExternalConfigManager:
    """Manages external configuration sources (JSON, Airtable, Database)"""
    
    def __init__(self, config: BotConfig):
        self.config = config
    
    def load_accounts_from_json(self) -> List[AccountConfig]:
        """Load accounts from JSON file"""
        try:
            with open(self.config.accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            accounts = []
            for acc_data in accounts_data:
                account = AccountConfig(
                    username=acc_data.get('username', ''),
                    email=acc_data.get('email', ''),
                    password=acc_data.get('password', ''),
                    enabled=acc_data.get('enabled', True),
                    description=acc_data.get('description', ''),
                    max_posts_per_day=acc_data.get('posting_config', {}).get('max_posts_per_day', 288),
                    delay_between_posts_seconds=acc_data.get('posting_config', {}).get('delay_between_posts_seconds', 300),
                    use_random_caption=acc_data.get('posting_config', {}).get('use_random_caption', True),
                    use_random_image=acc_data.get('posting_config', {}).get('use_random_image', True),
                    user_agent_rotation=acc_data.get('posting_config', {}).get('user_agent_rotation', True),
                    random_delays=acc_data.get('posting_config', {}).get('random_delays', True),
                    media_variation=acc_data.get('posting_config', {}).get('media_variation', True),
                    posting_schedule=acc_data.get('posting_schedule', {})
                )
                accounts.append(account)
            
            return accounts
        except Exception as e:
            logger.error(f"Error loading accounts from JSON: {e}")
            return []
    
    def load_accounts_from_airtable(self) -> List[AccountConfig]:
        """Load accounts from Airtable (placeholder implementation)"""
        if not self.config.airtable_api_key:
            logger.warning("Airtable API key not configured")
            return []
        
        try:
            # Airtable API implementation would go here
            # For now, return empty list
            logger.info("Airtable integration not yet implemented")
            return []
        except Exception as e:
            logger.error(f"Error loading accounts from Airtable: {e}")
            return []
    
    def load_accounts(self) -> List[AccountConfig]:
        """Load accounts from configured source"""
        if self.config.config_source == "airtable":
            return self.load_accounts_from_airtable()
        else:
            return self.load_accounts_from_json()


class EnhancedThreadsBot:
    """Enhanced Threads Bot with anti-detection and scalability features"""
    
    def __init__(self, config: BotConfig = None):
        """Initialize the enhanced bot with configuration"""
        self.config = config or BotConfig()
        
        # Initialize managers
        self.user_agent_rotator = UserAgentRotator(self.config.user_agents_file)
        self.delay_manager = DelayManager()
        self.media_variation_manager = MediaVariationManager(self.config.images_dir)
        self.external_config_manager = ExternalConfigManager(self.config)
        self.session_manager = SessionManager()
        self.rate_limit_handler = RateLimitHandler()
        
        # Load data (will be loaded asynchronously in run_async)
        self.accounts = self.external_config_manager.load_accounts()
        self.captions = []
        self.images = []
        
        # Initialize API
        self.api = None
        self.session_start_time = None
        
        # Statistics
        self.stats = {
            'total_posts': 0,
            'successful_posts': 0,
            'failed_posts': 0,
            'account_rotations': 0,
            'session_restarts': 0,
            'rate_limits_handled': 0,
            'shadowbans_detected': 0,
            'token_refreshes': 0,
            'human_like_delays': 0
        }
    
    async def _load_captions(self) -> List[str]:
        """Load captions from database with fallback to file"""
        try:
            from core.db_manager import DatabaseOperations
            captions = await DatabaseOperations.get_captions()
            return captions
        except Exception as e:
            logger.error(f"❌ Error loading captions from database: {e}")
            # Fallback to file-based loading
            try:
                with open(self.config.captions_file, 'r', encoding='utf-8') as f:
                    captions = [line.strip() for line in f if line.strip()]
                logger.info(f"📝 Loaded {len(captions)} captions from file (fallback)")
                return captions
            except FileNotFoundError:
                logger.warning(f"⚠️  Captions file not found: {self.config.captions_file}")
                return []
            except Exception as e:
                logger.error(f"❌ Error loading captions from file: {e}")
                return []
    
    async def _get_images(self) -> List[Path]:
        """Get list of available images from database with fallback to file system"""
        try:
            from core.db_manager import DatabaseOperations
            db_images = await DatabaseOperations.get_images()
            images = []
            for img_data in db_images:
                file_path = Path(img_data['file_path'])
                if file_path.exists():
                    images.append(file_path)
            logger.info(f"📸 Loaded {len(images)} images from database")
            return images
        except Exception as e:
            logger.error(f"❌ Error loading images from database: {e}")
            # Fallback to file-based loading
            if not self.config.images_dir:
                return []
            
            images_dir = Path(self.config.images_dir)
            if not images_dir.exists():
                logger.warning(f"{images_dir} directory not found. Creating it.")
                images_dir.mkdir(exist_ok=True)
                return []
            
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            images = []
            
            for file_path in images_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    images.append(file_path)
            
            logger.info(f"📸 Loaded {len(images)} images from file system (fallback)")
            return images
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for tracking"""
        return hashlib.md5(f"{time.time()}{secrets.token_hex(8)}".encode()).hexdigest()[:8]
    
    async def _initialize_api(self):
        """Initialize the Threads API with anti-detection features"""
        if not ThreadsAPI:
            raise ImportError("threads-api package not available")
        
        self.api = ThreadsAPI()
        self.session_start_time = time.time()
        session_id = self._generate_session_id()
        
        logger.info(f"🔧 Initializing API session: {session_id}")
        
        # Set user agent if rotation is enabled
        if self.config.anti_detection_enabled and self.config.user_agent_rotation:
            user_agent = self.user_agent_rotator.get_random_user_agent()
            # Note: User agent setting would depend on the threads-api implementation
            logger.info(f"🔄 Using user agent: {user_agent[:50]}...")
    
    async def _check_session_timeout(self):
        """Check if session needs to be refreshed"""
        if self.session_start_time and (time.time() - self.session_start_time) > self.config.session_timeout:
            logger.info("⏰ Session timeout reached. Refreshing session...")
            await self._initialize_api()
    
    async def login_to_account(self, account: AccountConfig) -> bool:
        """Login to account with enhanced anti-detection features"""
        try:
            await self._check_session_timeout()
            
            username = account.username
            password = account.password
            
            if not username or not password:
                logger.error(f"Missing username or password for account")
                return False
            
            # Check if account is rate limited or shadowbanned
            if self.session_manager.is_rate_limited(username):
                logger.warning(f"⏳ Account {username} is rate limited, skipping")
                return False
            
            if self.session_manager.is_shadowbanned(username):
                logger.warning(f"🚫 Account {username} is shadowbanned, skipping")
                return False
            
            # Human-like delay before login
            if self.config.anti_detection_enabled and account.random_delays:
                await self.delay_manager.human_like_delay("login")
                self.stats['human_like_delays'] += 1
            
            # Create or get session
            session = self.session_manager.get_session(username)
            if not session or not self.session_manager.is_session_valid(username):
                session = self.session_manager.create_session(username)
            
            # Use weighted random user agent
            if self.config.anti_detection_enabled and account.user_agent_rotation:
                user_agent = self.user_agent_rotator.get_weighted_random_user_agent()
                logger.info(f"🔄 Using weighted user agent for {username}: {user_agent[:50]}...")
            
            # Use cached token path with session ID
            session_id = session['session_id']
            cached_token_path = f".token_{username}_{session_id}"
            
            # Attempt login with retry logic
            for attempt in range(self.config.max_retries):
                try:
                    await self.api.login(username, password, cached_token_path=cached_token_path)
                    logger.info(f"✅ Successfully logged in as {username}")
                    
                    # Update session
                    self.session_manager.update_session(username, login_attempts=session['login_attempts'] + 1)
                    
                    # Human-like delay after login
                    if self.config.anti_detection_enabled and account.random_delays:
                        await self.delay_manager.human_like_delay("browse")
                        self.stats['human_like_delays'] += 1
                    
                    return True
                    
                except Exception as login_error:
                    error_message = str(login_error).lower()
                    error_type = self.rate_limit_handler.detect_error_type(error_message)
                    
                    logger.warning(f"⚠️  Login attempt {attempt + 1} failed for {username}: {error_type}")
                    
                    if error_type == 'rate_limit':
                        self.session_manager.handle_rate_limit(username)
                        self.stats['rate_limits_handled'] += 1
                        return False
                    elif error_type == 'shadowban':
                        self.session_manager.handle_shadowban(username)
                        self.stats['shadowbans_detected'] += 1
                        return False
                    elif error_type == 'auth_error':
                        if attempt < self.config.max_retries - 1:
                            delay = self.rate_limit_handler.get_retry_delay(error_type, attempt)
                            logger.info(f"⏳ Waiting {delay} seconds before retry...")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"💥 All login attempts failed for {username}")
                            return False
                    else:
                        # Unknown error, retry with exponential backoff
                        if attempt < self.config.max_retries - 1:
                            await self.delay_manager.exponential_backoff(attempt)
                        else:
                            logger.error(f"💥 Login failed for {username} after {self.config.max_retries} attempts")
                            return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error logging in to account {account.username}: {e}")
            return False
    
    async def post_content(self, caption: str, image_path: Optional[Path] = None, account: AccountConfig = None) -> bool:
        """Post content with enhanced anti-detection features"""
        try:
            await self._check_session_timeout()
            
            username = account.username if account else "unknown"
            
            # Check if account is rate limited or shadowbanned
            if self.session_manager.is_rate_limited(username):
                logger.warning(f"⏳ Account {username} is rate limited, skipping post")
                return False
            
            if self.session_manager.is_shadowbanned(username):
                logger.warning(f"🚫 Account {username} is shadowbanned, skipping post")
                return False
            
            # Human-like delay before posting
            if account and self.config.anti_detection_enabled and account.random_delays:
                await self.delay_manager.human_like_delay("post")
                self.stats['human_like_delays'] += 1
            
            # Apply media variation if enabled
            if image_path and account and account.media_variation:
                image_path = self.media_variation_manager.add_image_metadata(image_path)
            
            # Attempt posting with retry logic
            for attempt in range(self.config.max_retries):
                try:
                    if image_path and image_path.exists():
                        logger.info(f"📸 Posting with image: {image_path.name}")
                        result = await self.api.post(caption=caption, image_path=str(image_path))
                    else:
                        logger.info("📝 Posting text only")
                        result = await self.api.post(caption=caption)
                    
                    if result:
                        self.stats['successful_posts'] += 1
                        logger.info(f"🎉 SUCCESS! Posted to Threads successfully!")
                        
                        # Update session
                        if account:
                            self.session_manager.update_session(username, post_attempts=attempt + 1)
                        
                        return True
                    else:
                        self.stats['failed_posts'] += 1
                        logger.error("💥 FAILED! Posting to Threads was unsuccessful")
                        return False
                        
                except Exception as post_error:
                    error_message = str(post_error).lower()
                    error_type = self.rate_limit_handler.detect_error_type(error_message)
                    
                    logger.warning(f"⚠️  Post attempt {attempt + 1} failed for {username}: {error_type}")
                    
                    if error_type == 'rate_limit':
                        self.session_manager.handle_rate_limit(username)
                        self.stats['rate_limits_handled'] += 1
                        return False
                    elif error_type == 'shadowban':
                        self.session_manager.handle_shadowban(username)
                        self.stats['shadowbans_detected'] += 1
                        return False
                    elif error_type == 'auth_error':
                        # Token might be expired, try to refresh
                        if self.session_manager.refresh_token_if_needed(username):
                            self.stats['token_refreshes'] += 1
                            logger.info(f"🔄 Token refreshed for {username}, retrying...")
                            continue
                        else:
                            logger.error(f"💥 Authentication error for {username}, cannot refresh token")
                            return False
                    else:
                        # Unknown error, retry with exponential backoff
                        if attempt < self.config.max_retries - 1:
                            delay = self.rate_limit_handler.get_retry_delay(error_type, attempt)
                            logger.info(f"⏳ Waiting {delay} seconds before retry...")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"💥 Post failed for {username} after {self.config.max_retries} attempts")
                            self.stats['failed_posts'] += 1
                            return False
            
            return False
                
        except Exception as e:
            self.stats['failed_posts'] += 1
            logger.error(f"💥 ERROR! Exception occurred while posting: {e}")
            return False
    
    async def process_account(self, account: AccountConfig) -> bool:
        """Process a single account with enhanced human-like features"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Processing account: {account.username}")
        logger.info(f"📊 Status: {'✅ Enabled' if account.enabled else '❌ Disabled'}")
        logger.info(f"{'='*60}")
        
        if not account.enabled:
            logger.info(f"⏭️  Skipping disabled account: {account.username}")
            return False
        
        # Check session and rate limiting
        username = account.username
        if self.session_manager.is_rate_limited(username):
            logger.warning(f"⏳ Account {username} is rate limited, skipping")
            return False
        
        if self.session_manager.is_shadowbanned(username):
            logger.warning(f"🚫 Account {username} is shadowbanned, skipping")
            return False
        
        # Login with enhanced retry logic
        for attempt in range(self.config.max_retries):
            if await self.login_to_account(account):
                break
            else:
                if attempt < self.config.max_retries - 1:
                    logger.warning(f"⚠️  Login attempt {attempt + 1} failed. Retrying...")
                    await self.delay_manager.exponential_backoff(attempt)
                else:
                    logger.error(f"💥 All login attempts failed for account: {account.username}")
                    return False
        
        # Get varied content with human-like behavior
        content_order = self.media_variation_manager.get_content_order(self.captions, self.images)
        
        # Select caption with variation
        if account.use_random_caption and self.captions:
            caption = content_order.get('caption', random.choice(self.captions))
        else:
            caption = "Default caption"
        
        # Select image with reuse delay and cross-account tracking
        image = None
        if account.use_random_image and self.images:
            image = self.media_variation_manager.get_varied_image(self.images, account.username)
        
        logger.info(f"📝 Selected caption: {caption[:50]}{'...' if len(caption) > 50 else ''}")
        if image:
            logger.info(f"🖼️  Selected image: {image.name}")
        else:
            logger.info(f"⚠️  No images available - posting text only")
        
        # Human-like delay before posting
        if self.config.anti_detection_enabled and account.random_delays:
            await self.delay_manager.human_like_delay("browse")
            self.stats['human_like_delays'] += 1
        
        # Post content with enhanced error handling
        success = await self.post_content(caption, image, account)
        
        if success:
            logger.info(f"🎉 ACCOUNT SUCCESS! Posted to Threads account: {account.username}")
        else:
            logger.error(f"💥 ACCOUNT FAILED! Failed to post to Threads account: {account.username}")
        
        return success
    
    async def run_async(self):
        """Main bot execution with enhanced features"""
        await self._initialize_api()
        
        # Load data asynchronously
        self.captions = await self._load_captions()
        self.images = await self._get_images()
        
        logger.info("🚀 Enhanced Threads Bot Starting...")
        logger.info(f"📋 Loaded {len(self.accounts)} accounts")
        logger.info(f"💬 Loaded {len(self.captions)} captions")
        logger.info(f"🖼️  Found {len(self.images)} images")
        logger.info(f"🛡️  Anti-detection: {'✅ Enabled' if self.config.anti_detection_enabled else '❌ Disabled'}")
        
        if not self.accounts:
            logger.error("❌ No accounts configured.")
            return
        
        if not self.captions:
            logger.error("❌ No captions available.")
            return
        
        # Get enabled accounts
        enabled_accounts = [acc for acc in self.accounts if acc.enabled]
        if not enabled_accounts:
            logger.error("❌ No enabled accounts found.")
            return
        
        logger.info(f"✅ Found {len(enabled_accounts)} enabled accounts")
        logger.info("🔄 Starting enhanced 24/7 posting...")
        
        # Enhanced continuous posting loop
        post_count = 0
        
        while True:
            post_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 POSTING ROUND #{post_count} - {current_time}")
            logger.info(f"🕐 Enhanced 24/7 Operation with anti-detection")
            logger.info(f"{'='*60}")
            
            successful_posts = 0
            total_accounts = len(enabled_accounts)
            
            # Rotate accounts for better distribution
            if self.config.anti_detection_enabled:
                random.shuffle(enabled_accounts)
                self.stats['account_rotations'] += 1
                logger.info("🔄 Account rotation applied")
            
            for i, account in enumerate(enabled_accounts, 1):
                logger.info(f"\n📊 Progress: {i}/{total_accounts}")
                
                # Process account
                success = await self.process_account(account)
                if success:
                    successful_posts += 1
                
                # Enhanced delay between accounts
                if i < total_accounts:
                    delay = account.delay_between_posts_seconds
                    if self.config.anti_detection_enabled and account.random_delays:
                        delay += random.randint(-30, 30)  # Add randomness
                    
                    logger.info(f"⏳ Waiting {delay} seconds before next account...")
                    await asyncio.sleep(delay)
            
            # Update statistics
            self.stats['total_posts'] += total_accounts
            
            # Round summary
            logger.info(f"\n📊 ROUND #{post_count} SUMMARY - {current_time}")
            logger.info(f"✅ Successful posts: {successful_posts}/{total_accounts}")
            logger.info(f"❌ Failed posts: {total_accounts - successful_posts}")
            logger.info(f"📈 Success rate: {(successful_posts/total_accounts)*100:.1f}%")
            logger.info(f"📊 Total stats: {self.stats}")
            
            if successful_posts == total_accounts:
                logger.info(f"🎉 PERFECT ROUND! All accounts posted successfully!")
            elif successful_posts > 0:
                logger.info(f"⚠️  PARTIAL SUCCESS! Some accounts failed to post")
            else:
                logger.error(f"💥 COMPLETE FAILURE! No accounts posted successfully")
            
            # Random sleep interval (3-6 minutes) instead of fixed 5 minutes
            sleep_seconds = await self.delay_manager.random_sleep_interval(3, 6)
            
            logger.info(f"\n⏳ Random sleep interval completed: {sleep_seconds} seconds")
            next_round_time = (datetime.now() + timedelta(seconds=sleep_seconds)).strftime("%H:%M:%S")
            logger.info(f"🕐 Next round will start at: {next_round_time}")
    
    def run(self):
        """Main bot execution method (synchronous wrapper)"""
        if not ThreadsAPI:
            logger.error("❌ Error: threads-api package not available")
            logger.info("💡 Please install it with: pip install -r requirements.txt")
            return
        
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user (Ctrl+C)")
            logger.info("✅ Graceful shutdown completed")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            logger.info("🔄 Restarting bot in 30 seconds...")
            time.sleep(30)
            self.run()  # Restart the bot


def main():
    """Main function to run the enhanced bot."""
    # Load configuration
    config = BotConfig()
    
    # Create and run the enhanced bot
    bot = EnhancedThreadsBot(config)
    bot.run()


if __name__ == "__main__":
    main() 