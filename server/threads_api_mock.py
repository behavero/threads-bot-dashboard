"""
Mock Threads API for development and testing
This simulates the Threads API functionality without external dependencies
"""

import time
import random
from typing import Optional

class ThreadsAPI:
    def __init__(self):
        self.logged_in = False
        self.username = None
        
    def login(self, username: str, password: str) -> bool:
        """Mock login - always succeeds"""
        print(f"🔐 Mock login for {username}")
        self.logged_in = True
        self.username = username
        return True
    
    def post(self, text: str) -> bool:
        """Mock text post"""
        if not self.logged_in:
            print("❌ Not logged in")
            return False
        
        print(f"📝 Mock posting text: {text[:50]}...")
        time.sleep(random.uniform(1, 3))  # Simulate API delay
        
        # 90% success rate for mock
        success = random.random() > 0.1
        if success:
            print(f"✅ Mock post successful for {self.username}")
        else:
            print(f"❌ Mock post failed for {self.username}")
        
        return success
    
    def post_with_image(self, text: str, image_url: str) -> bool:
        """Mock image post"""
        if not self.logged_in:
            print("❌ Not logged in")
            return False
        
        print(f"📸 Mock posting with image: {text[:50]}... | {image_url}")
        time.sleep(random.uniform(2, 4))  # Simulate longer delay for image
        
        # 85% success rate for image posts
        success = random.random() > 0.15
        if success:
            print(f"✅ Mock image post successful for {self.username}")
        else:
            print(f"❌ Mock image post failed for {self.username}")
        
        return success 