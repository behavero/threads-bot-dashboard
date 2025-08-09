#!/usr/bin/env python3
"""
Simple in-memory rate limiter
Tracks request counts per account/IP with time-based windows
"""

import time
import logging
from typing import Dict, Tuple
from threading import Lock

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = Lock()
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is allowed for given key
        Returns (allowed, remaining_requests)
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Initialize or get existing requests for this key
            if key not in self.requests:
                self.requests[key] = []
            
            # Remove old requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key] 
                if req_time > window_start
            ]
            
            current_count = len(self.requests[key])
            
            if current_count >= max_requests:
                remaining = 0
                allowed = False
            else:
                # Add current request
                self.requests[key].append(now)
                remaining = max_requests - current_count - 1
                allowed = True
            
            return allowed, remaining
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests without consuming one"""
        with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            if key not in self.requests:
                return max_requests
            
            # Count requests in current window
            current_requests = [
                req_time for req_time in self.requests[key] 
                if req_time > window_start
            ]
            
            return max(0, max_requests - len(current_requests))
    
    def reset_key(self, key: str):
        """Reset rate limit for a specific key"""
        with self.lock:
            if key in self.requests:
                del self.requests[key]
    
    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """Clean up old entries to prevent memory leaks"""
        with self.lock:
            now = time.time()
            cutoff = now - max_age_seconds
            
            keys_to_remove = []
            for key, request_times in self.requests.items():
                # Keep only recent requests
                recent_requests = [
                    req_time for req_time in request_times 
                    if req_time > cutoff
                ]
                
                if recent_requests:
                    self.requests[key] = recent_requests
                else:
                    keys_to_remove.append(key)
            
            # Remove empty entries
            for key in keys_to_remove:
                del self.requests[key]
            
            logger.info(f"🧹 Rate limiter cleanup: removed {len(keys_to_remove)} old entries")

# Global rate limiter instance
rate_limiter = RateLimiter()

# Rate limiting constants
TEST_POST_LIMIT = 3  # Max 3 test posts
TEST_POST_WINDOW = 3600  # Per hour (3600 seconds)
