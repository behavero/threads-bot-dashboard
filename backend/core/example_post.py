#!/usr/bin/env python3
"""
Example script for posting to Threads using threads-api
Based on the official example from https://github.com/Danie1/threads-api
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from threads_api.src.threads_api import ThreadsAPI
except ImportError:
    print("❌ threads-api not installed. Run: pip install git+https://github.com/Danie1/threads-api.git")
    exit(1)

async def post_to_threads():
    """Post content to Threads using threads-api"""
    print("🚀 Starting Threads post example...")
    
    try:
        # Initialize API
        api = ThreadsAPI()
        print("✅ ThreadsAPI initialized")
        
        # Get credentials from environment variables
        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            print("❌ Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables")
            print("💡 Example: export INSTAGRAM_USERNAME=your_username")
            print("💡 Example: export INSTAGRAM_PASSWORD=your_password")
            return
        
        print(f"🔐 Logging in as: {username}")
        
        # Login to Threads
        await api.login(username, password, cached_token_path=".example_token")
        print("✅ Login successful!")
        
        # Post content
        caption = "Hello Threads! This is a test post from the threads-api Python library! 🐍✨"
        print(f"📝 Posting caption: {caption}")
        
        # Check if we have an image to post with
        image_path = "images/sample.jpg"  # You can change this to any image in your images/ folder
        if os.path.exists(image_path):
            print(f"🖼️  Posting with image: {image_path}")
            result = await api.post(caption=caption, image_path=image_path)
        else:
            print("📝 Posting text only (no image found)")
            result = await api.post(caption=caption)
        
        # Check result
        if result:
            print("🎉 Post has been successfully posted to Threads!")
        else:
            print("❌ Unable to post to Threads")
        
        # Close API connection
        await api.close_gracefully()
        print("✅ API connection closed gracefully")
        
    except Exception as e:
        print(f"❌ Error during posting: {e}")

async def main():
    """Main function"""
    await post_to_threads()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main()) 