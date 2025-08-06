#!/usr/bin/env python3
"""
Enhanced Threads API Wrapper
Features:
- Better error handling
- Rate limiting
- Human-like behavior simulation
- Retry logic with exponential backoff
- Session management
"""

import time
import random
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API behavior"""
    base_url: str = "https://www.threads.net/api/v1"
    max_retries: int = 3
    retry_delay_base: float = 2.0
    rate_limit_delay: float = 1.0
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class EnhancedThreadsAPI:
    """Enhanced Threads API with human-like behavior"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.logged_in = False
        self.username = None
        self.last_request_time = None
        self.rate_limit_reset = None
        
    def _rate_limit_check(self):
        """Check and respect rate limits"""
        if self.last_request_time:
            time_since_last = time.time() - self.last_request_time
            if time_since_last < self.config.rate_limit_delay:
                sleep_time = self.config.rate_limit_delay - time_since_last
                logger.info(f"⏳ Rate limit delay: {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like delay"""
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"🤖 Human delay: {delay:.2f}s")
        time.sleep(delay)
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     retries: int = None) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        if retries is None:
            retries = self.config.max_retries
        
        url = f"{self.config.base_url}/{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                self._rate_limit_check()
                
                logger.info(f"🌐 API request: {method} {endpoint}")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"⚠️ Rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                # Check for other errors
                if response.status_code >= 400:
                    logger.error(f"❌ API error {response.status_code}: {response.text}")
                    if response.status_code == 401:
                        logger.error("❌ Authentication failed")
                        return None
                    elif response.status_code == 403:
                        logger.error("❌ Access forbidden")
                        return None
                    elif response.status_code >= 500:
                        logger.error("❌ Server error, retrying...")
                        if attempt < retries:
                            time.sleep(self.config.retry_delay_base * (2 ** attempt))
                            continue
                        return None
                    else:
                        return None
                
                # Success
                result = response.json() if response.content else {}
                logger.info(f"✅ API request successful")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request error: {e}")
                if attempt < retries:
                    delay = self.config.retry_delay_base * (2 ** attempt)
                    logger.info(f"⏳ Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    return None
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                return None
        
        return None
    
    def login(self, username: str, password: str) -> bool:
        """Login to Threads account"""
        logger.info(f"🔐 Logging in to {username}...")
        
        # Add human-like delay before login
        self._human_delay(2.0, 5.0)
        
        # Mock login for development
        if not self._is_production():
            logger.info(f"🔐 Mock login for {username}")
            self.logged_in = True
            self.username = username
            return True
        
        # Real login implementation would go here
        login_data = {
            'username': username,
            'password': password,
            'device_id': self._generate_device_id(),
            'enc_password': self._encrypt_password(password)
        }
        
        result = self._make_request('POST', 'accounts/login/', login_data)
        
        if result and result.get('authenticated'):
            self.logged_in = True
            self.username = username
            logger.info(f"✅ Successfully logged in to {username}")
            return True
        else:
            logger.error(f"❌ Failed to login to {username}")
            return False
    
    def post(self, text: str) -> bool:
        """Post text content"""
        if not self.logged_in:
            logger.error("❌ Not logged in")
            return False
        
        logger.info(f"📝 Posting text: {text[:50]}...")
        
        # Add human-like delays
        self._human_delay(1.0, 3.0)
        
        # Mock posting for development
        if not self._is_production():
            success = random.random() > 0.1  # 90% success rate
            if success:
                logger.info(f"✅ Mock post successful for {self.username}")
            else:
                logger.error(f"❌ Mock post failed for {self.username}")
            return success
        
        # Real posting implementation
        post_data = {
            'text': text,
            'device_id': self._generate_device_id(),
            'source_type': '4',
            'caption': text
        }
        
        result = self._make_request('POST', 'media/configure_text_only/', post_data)
        
        if result and result.get('status') == 'ok':
            logger.info(f"✅ Posted successfully for {self.username}")
            return True
        else:
            logger.error(f"❌ Failed to post for {self.username}")
            return False
    
    def post_with_image(self, text: str, image_url: str) -> bool:
        """Post content with image"""
        if not self.logged_in:
            logger.error("❌ Not logged in")
            return False
        
        logger.info(f"📸 Posting with image: {text[:50]}... | {image_url}")
        
        # Add longer delay for image posts
        self._human_delay(2.0, 5.0)
        
        # Mock posting for development
        if not self._is_production():
            success = random.random() > 0.15  # 85% success rate for images
            if success:
                logger.info(f"✅ Mock image post successful for {self.username}")
            else:
                logger.error(f"❌ Mock image post failed for {self.username}")
            return success
        
        # Real image posting implementation
        # First upload the image
        upload_result = self._upload_image(image_url)
        if not upload_result:
            logger.error("❌ Failed to upload image")
            return False
        
        # Then create the post with the uploaded image
        post_data = {
            'text': text,
            'device_id': self._generate_device_id(),
            'source_type': '4',
            'caption': text,
            'media_id': upload_result['media_id']
        }
        
        result = self._make_request('POST', 'media/configure/', post_data)
        
        if result and result.get('status') == 'ok':
            logger.info(f"✅ Posted with image successfully for {self.username}")
            return True
        else:
            logger.error(f"❌ Failed to post with image for {self.username}")
            return False
    
    def _upload_image(self, image_url: str) -> Optional[Dict]:
        """Upload image to Threads"""
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"❌ Failed to download image: {response.status_code}")
                return None
            
            # Mock upload for development
            if not self._is_production():
                return {'media_id': f'mock_media_{random.randint(1000, 9999)}'}
            
            # Real upload implementation would go here
            upload_data = {
                'image': response.content,
                'device_id': self._generate_device_id()
            }
            
            result = self._make_request('POST', 'media/upload_photo/', upload_data)
            return result
            
        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            return None
    
    def _generate_device_id(self) -> str:
        """Generate a device ID"""
        return f"android-{random.randint(100000000, 999999999)}"
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt password for API"""
        # Mock encryption for development
        return f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}"
    
    def _is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv('THREADS_API_PRODUCTION', 'false').lower() == 'true'
    
    def logout(self):
        """Logout from Threads"""
        if self.logged_in:
            logger.info(f"👋 Logging out {self.username}")
            self.logged_in = False
            self.username = None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get current account information"""
        if not self.logged_in:
            return None
        
        result = self._make_request('GET', 'accounts/current_user/')
        return result
    
    def get_followers_count(self) -> Optional[int]:
        """Get followers count"""
        if not self.logged_in:
            return None
        
        account_info = self.get_account_info()
        if account_info:
            return account_info.get('follower_count', 0)
        return None

class ThreadsAPIManager:
    """Manages multiple Threads API instances"""
    
    def __init__(self):
        self.api_instances = {}
        self.config = APIConfig()
    
    def get_api_instance(self, username: str) -> Optional[EnhancedThreadsAPI]:
        """Get or create API instance for username"""
        if username not in self.api_instances:
            api = EnhancedThreadsAPI(self.config)
            self.api_instances[username] = api
        
        return self.api_instances[username]
    
    def login_account(self, username: str, password: str) -> bool:
        """Login to account"""
        api = self.get_api_instance(username)
        return api.login(username, password)
    
    def post_content(self, username: str, text: str, image_url: str = None) -> bool:
        """Post content for account"""
        api = self.get_api_instance(username)
        
        if not api.logged_in:
            logger.error(f"❌ {username} not logged in")
            return False
        
        if image_url:
            return api.post_with_image(text, image_url)
        else:
            return api.post(text)
    
    def logout_all(self):
        """Logout from all accounts"""
        for username, api in self.api_instances.items():
            api.logout()
        self.api_instances.clear()

def main():
    """Test the enhanced API"""
    config = APIConfig()
    api = EnhancedThreadsAPI(config)
    
    # Test login
    success = api.login("test_user", "test_password")
    if success:
        print("✅ Login successful")
        
        # Test posting
        post_success = api.post("Test post from enhanced API!")
        if post_success:
            print("✅ Post successful")
        else:
            print("❌ Post failed")
        
        api.logout()
    else:
        print("❌ Login failed")

if __name__ == "__main__":
    main() 