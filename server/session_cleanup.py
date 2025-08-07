#!/usr/bin/env python3
"""
Session Cleanup Scheduler
Automatically cleans up expired sessions
"""

import schedule
import time
import threading
from session_manager import session_manager

def cleanup_expired_sessions():
    """Clean up expired sessions (older than 30 days)"""
    try:
        print("🧹 Running scheduled session cleanup...")
        cleaned_count = session_manager.cleanup_expired_sessions(max_age_days=30)
        print(f"✅ Cleaned up {cleaned_count} expired sessions")
    except Exception as e:
        print(f"❌ Error during scheduled cleanup: {e}")

def start_cleanup_scheduler():
    """Start the session cleanup scheduler"""
    try:
        # Schedule cleanup to run daily at 2 AM
        schedule.every().day.at("02:00").do(cleanup_expired_sessions)
        
        # Also run cleanup every Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(cleanup_expired_sessions)
        
        print("✅ Session cleanup scheduler started")
        print("📅 Cleanup scheduled for daily at 2 AM and Sundays at 3 AM")
        
        # Run in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start cleanup scheduler: {e}")
        return False

if __name__ == "__main__":
    # Test cleanup
    print("🧪 Testing session cleanup...")
    cleanup_expired_sessions()
    
    # Start scheduler
    print("🚀 Starting session cleanup scheduler...")
    start_cleanup_scheduler()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("⏹️ Session cleanup scheduler stopped")
