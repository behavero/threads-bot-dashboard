#!/usr/bin/env python3
"""
Enhanced Threads Bot Startup Script
This script starts the enhanced bot with proper configuration and monitoring.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add server directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_threads_bot import EnhancedThreadsBot, PostingConfig
from bot_monitor import BotMonitor

def load_config(config_file: str = "bot_config.json") -> dict:
    """Load configuration from JSON file"""
    config_path = Path(__file__).parent / config_file
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        print(f"⚠️ Config file {config_file} not found, using defaults")
        return {}

def create_posting_config(config_data: dict) -> PostingConfig:
    """Create PostingConfig from configuration data"""
    posting_config = config_data.get('posting', {})
    
    return PostingConfig(
        min_interval=posting_config.get('min_interval', 3600),
        max_interval=posting_config.get('max_interval', 7200),
        human_delay_min=posting_config.get('human_delay_min', 2.0),
        human_delay_max=posting_config.get('human_delay_max', 8.0),
        max_posts_per_day=posting_config.get('max_posts_per_day', 8),
        max_posts_per_account=posting_config.get('max_posts_per_account', 3),
        cooldown_hours=posting_config.get('cooldown_hours', 6),
        retry_attempts=posting_config.get('retry_attempts', 3),
        success_rate_threshold=posting_config.get('success_rate_threshold', 0.7)
    )

def setup_logging(log_level: str = "INFO", log_file: str = "threads_bot.log"):
    """Setup logging configuration"""
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    logging.basicConfig(
        level=log_levels.get(log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Threads Bot")
    parser.add_argument("--config", default="bot_config.json", help="Configuration file path")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    parser.add_argument("--log-file", default="threads_bot.log", help="Log file path")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual posting)")
    parser.add_argument("--test", action="store_true", help="Run in test mode with limited cycles")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    print("🚀 Starting Enhanced Threads Bot...")
    print(f"📁 Config file: {args.config}")
    print(f"📝 Log level: {args.log_level}")
    print(f"📄 Log file: {args.log_file}")
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No actual posting will occur")
    
    if args.test:
        print("🧪 TEST MODE - Limited cycles for testing")
    
    # Load configuration
    config_data = load_config(args.config)
    posting_config = create_posting_config(config_data)
    
    # Create and run bot
    bot = EnhancedThreadsBot(posting_config)
    
    if args.test:
        # Test mode - run limited cycles
        logger.info("🧪 Running in test mode")
        
        if not bot.initialize():
            logger.error("❌ Failed to initialize bot")
            return
        
        # Run a few test cycles
        for i in range(3):
            logger.info(f"🧪 Test cycle {i + 1}/3")
            bot.run_posting_cycle()
            bot.dashboard.print_dashboard()
            
            if i < 2:  # Don't wait after last cycle
                logger.info("⏳ Waiting 30 seconds for next test cycle...")
                import time
                time.sleep(30)
        
        logger.info("✅ Test mode completed")
        bot.monitor.export_metrics("test_metrics.json")
        
    else:
        # Normal mode - run continuously
        bot.run_continuously()

if __name__ == "__main__":
    main() 