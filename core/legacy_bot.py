#!/usr/bin/env python3
"""
Threads Bot - A Python bot for posting images with captions to Threads
Handles multiple accounts with random caption and image selection
"""

import json
import os
import random
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from threads_api.src.threads_api import ThreadsAPI
    THREADS_API_AVAILABLE = True
except ImportError:
    print("Warning: threads-api package not installed. Install with: pip install -r requirements.txt")
    THREADS_API_AVAILABLE = False


class ThreadsBot:
    def __init__(self, accounts_file: str = "accounts.json", captions_file: str = "captions.txt", images_dir: str = "images/"):
        """
        Initialize the ThreadsBot with configuration files and directories.
        
        Args:
            accounts_file: Path to the JSON file containing account information
            captions_file: Path to the text file containing captions (one per line)
            images_dir: Path to the directory containing images
        """
        self.accounts_file = accounts_file
        self.captions_file = captions_file
        self.images_dir = Path(images_dir)
        
        # Load accounts
        self.accounts = self._load_accounts()
        
        # Load captions
        self.captions = self._load_captions()
        
        # Get available images
        self.images = self._get_images()
        
        # Initialize API (will be done in async context)
        self.api = None
    
    def _load_accounts(self) -> List[Dict]:
        """Load account information from JSON file."""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.accounts_file} not found. Creating empty accounts file.")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.accounts_file}: {e}")
            return []
    
    def _load_captions(self) -> List[str]:
        """Load captions from text file."""
        try:
            with open(self.captions_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: {self.captions_file} not found. Creating empty captions file.")
            return []
    
    def _get_images(self) -> List[Path]:
        """Get list of available images from the images directory."""
        if not self.images_dir.exists():
            print(f"Warning: {self.images_dir} directory not found. Creating it.")
            self.images_dir.mkdir(exist_ok=True)
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png'}
        images = []
        
        for file_path in self.images_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                images.append(file_path)
        
        return images
    
    def get_random_caption(self) -> Optional[str]:
        """Get a random caption from the loaded captions."""
        if not self.captions:
            return None
        return random.choice(self.captions)
    
    def get_random_image(self) -> Optional[Path]:
        """Get a random image from the images directory."""
        if not self.images:
            return None
        return random.choice(self.images)
    
    async def login_to_account(self, account: Dict) -> bool:
        """
        Login to a Threads account using the threads-api.
        
        Args:
            account: Account dictionary with username and password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        if not THREADS_API_AVAILABLE:
            print("Error: threads-api package not available")
            return False
        
        try:
            username = account.get('username')
            password = account.get('password')
            
            if not username or not password:
                print(f"Error: Missing username or password for account")
                return False
            
            # Use cached token path for this account
            cached_token_path = f".token_{username}"
            
            await self.api.login(username, password, cached_token_path=cached_token_path)
            print(f"✅ Successfully logged in as {username}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging in to account {account.get('username', 'unknown')}: {e}")
            return False
    
    async def post_content(self, caption: str, image_path: Optional[Path] = None) -> bool:
        """
        Post content to Threads using the threads-api.
        
        Args:
            caption: The caption text to post
            image_path: Optional path to the image file
            
        Returns:
            bool: True if posting was successful, False otherwise
        """
        if not THREADS_API_AVAILABLE:
            print("❌ Error: threads-api package not available")
            return False
        
        try:
            if image_path and image_path.exists():
                # Post with image
                print(f"📸 Attempting to post with image: {image_path.name}")
                result = await self.api.post(caption=caption, image_path=str(image_path))
            else:
                # Post text only
                print("📝 Attempting to post text only")
                result = await self.api.post(caption=caption)
            
            if result:
                print(f"🎉 SUCCESS! Posted to Threads successfully!")
                print(f"📝 Caption: {caption[:50]}{'...' if len(caption) > 50 else ''}")
                if image_path and image_path.exists():
                    print(f"🖼️  Image: {image_path.name}")
                return True
            else:
                print("💥 FAILED! Posting to Threads was unsuccessful")
                print(f"❌ The API returned False/None for the post request")
                return False
                
        except Exception as e:
            print("💥 ERROR! Exception occurred while posting to Threads")
            print(f"❌ Error details: {e}")
            return False
    
    async def process_account(self, account: Dict) -> bool:
        """
        Process a single account: login, post content, and logout.
        
        Args:
            account: Account dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        username = account.get('username', 'unknown')
        enabled = account.get('enabled', False)
        
        print(f"\n{'='*60}")
        print(f"🔄 Processing account: {username}")
        print(f"📊 Status: {'✅ Enabled' if enabled else '❌ Disabled'}")
        print(f"{'='*60}")
        
        if not enabled:
            print(f"⏭️  Skipping disabled account: {username}")
            return False
        
        # Login to account
        if not await self.login_to_account(account):
            print(f"💥 LOGIN FAILED! Could not authenticate to account: {username}")
            print(f"❌ Please check your username and password in accounts.json")
            return False
        
        # Get random caption and image
        caption = self.get_random_caption()
        image = self.get_random_image()
        
        if not caption:
            print(f"💥 NO CAPTIONS! No captions available for account: {username}")
            print(f"❌ Please add captions to captions.txt file")
            return False
        
        print(f"📝 Selected caption: {caption[:50]}{'...' if len(caption) > 50 else ''}")
        if image:
            print(f"🖼️  Selected image: {image.name}")
        else:
            print(f"⚠️  No images available - posting text only")
        
        # Post content
        success = await self.post_content(caption, image)
        
        if success:
            print(f"🎉 ACCOUNT SUCCESS! Successfully posted to Threads account: {username}")
            print(f"✅ Content has been published and is now live on Threads")
        else:
            print(f"💥 ACCOUNT FAILED! Failed to post to Threads account: {username}")
            print(f"❌ The post was not published - please check your account settings")
        
        return success
    
    async def run_async(self):
        """Main bot execution method (async version)."""
        # Initialize API in async context
        if THREADS_API_AVAILABLE:
            self.api = ThreadsAPI()
        
        print("🚀 Threads Bot Starting...")
        print(f"📋 Loaded {len(self.accounts)} accounts")
        print(f"💬 Loaded {len(self.captions)} captions")
        print(f"🖼️  Found {len(self.images)} images")
        
        if not self.accounts:
            print("❌ No accounts configured. Please add accounts to accounts.json")
            return
        
        if not self.captions:
            print("❌ No captions available. Please add captions to captions.txt")
            return
        
        if not self.images:
            print("⚠️  No images available. Posts will be text-only.")
        
        # Get enabled accounts
        enabled_accounts = [acc for acc in self.accounts if acc.get('enabled', False)]
        if not enabled_accounts:
            print("❌ No enabled accounts found. Please enable at least one account in accounts.json")
            return
        
        print(f"✅ Found {len(enabled_accounts)} enabled accounts")
        print("🔄 Starting continuous posting every 5 minutes...")
        
        # Continuous posting loop - 1 post every 5 minutes 24/7
        post_count = 0
        print("🔄 Starting 24/7 posting: 1 post every 5 minutes to each account")
        
        while True:
            post_count += 1
            current_time = time.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"\n{'='*60}")
            print(f"📊 POSTING ROUND #{post_count} - {current_time}")
            print(f"🕐 24/7 Operation: 1 post every 5 minutes to each account")
            print(f"{'='*60}")
            
            successful_posts = 0
            total_accounts = len(enabled_accounts)
            
            for i, account in enumerate(enabled_accounts, 1):
                print(f"\n📊 Progress: {i}/{total_accounts}")
                
                # Process the account
                success = await self.process_account(account)
                if success:
                    successful_posts += 1
                
                # Wait 30 seconds between accounts (except for the last one)
                if i < total_accounts:
                    print(f"⏳ Waiting 30 seconds before next account...")
                    await asyncio.sleep(30)
            
            # Round summary
            print(f"\n📊 ROUND #{post_count} SUMMARY - {current_time}")
            print(f"✅ Successful posts: {successful_posts}/{total_accounts}")
            print(f"❌ Failed posts: {total_accounts - successful_posts}")
            print(f"📈 Success rate: {(successful_posts/total_accounts)*100:.1f}%")
            
            if successful_posts == total_accounts:
                print(f"🎉 PERFECT ROUND! All accounts posted successfully!")
            elif successful_posts > 0:
                print(f"⚠️  PARTIAL SUCCESS! Some accounts failed to post")
            else:
                print(f"💥 COMPLETE FAILURE! No accounts posted successfully")
                print(f"❌ Please check your accounts.json, captions.txt, and network connection")
            
            # Wait exactly 5 minutes before next round
            print(f"\n⏳ Waiting exactly 5 minutes before next posting round...")
            next_round_time = time.strftime("%H:%M:%S", time.localtime(time.time() + 300))
            print(f"🕐 Next round will start at: {next_round_time}")
            await asyncio.sleep(300)  # Exactly 5 minutes = 300 seconds
    
    def run(self):
        """Main bot execution method (synchronous wrapper)."""
        if not THREADS_API_AVAILABLE:
            print("❌ Error: threads-api package not available")
            print("💡 Please install it with: pip install -r requirements.txt")
            return
        
        try:
            # Run the async version
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user (Ctrl+C)")
            print("✅ Graceful shutdown completed")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("🔄 Restarting bot in 30 seconds...")
            import time
            time.sleep(30)
            self.run()  # Restart the bot


def main():
    """Main function to run the bot."""
    bot = ThreadsBot()
    bot.run()


if __name__ == "__main__":
    main() 