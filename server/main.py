#!/usr/bin/env python3
"""
Enhanced Threads Bot - Backend Entry Point
Deployed on Railway for 24/7 bot operation
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment variables and paths"""
    # Platform detection
    platform = os.getenv('PLATFORM', 'railway')
    logger.info(f"🚀 Starting on platform: {platform}")
    
    # Set Python path for Railway
    if platform == 'railway':
        os.environ['PYTHONPATH'] = str(backend_dir)
        logger.info("✅ Railway environment configured")
    
    # Set port for web server
    port = int(os.getenv('PORT', 8000))
    os.environ['PORT'] = str(port)
    logger.info(f"🌐 Web server port: {port}")
    
    # Update file paths for new structure
    os.environ['ACCOUNTS_FILE'] = 'config/accounts.json'
    os.environ['CAPTIONS_FILE'] = 'assets/captions.txt'
    os.environ['IMAGES_DIR'] = 'assets/images/'
    os.environ['USER_AGENTS_FILE'] = 'config/user_agents.txt'

def check_required_files():
    """Check if required files exist"""
    required_files = [
        'config/accounts.json',
        'assets/captions.txt',
        'config/user_agents.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"⚠️  Missing files: {missing_files}")
        logger.info("📝 Creating sample files...")
        
        # Create config directory
        Path('config').mkdir(exist_ok=True)
        Path('assets').mkdir(exist_ok=True)
        Path('assets/images').mkdir(exist_ok=True)
        
        # Create sample accounts.json
        if not Path('config/accounts.json').exists():
            sample_accounts = [
                {
                    "username": "sample_user",
                    "email": "sample@example.com",
                    "password": "your_password_here",
                    "enabled": False,
                    "description": "Sample account - update with real credentials",
                    "posting_schedule": {
                        "frequency": "every_5_minutes",
                        "interval_minutes": 5,
                        "timezone": "UTC",
                        "start_time": "00:00",
                        "end_time": "23:59"
                    },
                    "posting_config": {
                        "use_random_caption": True,
                        "use_random_image": True,
                        "max_posts_per_day": 288,
                        "delay_between_posts_seconds": 300,
                        "user_agent_rotation": True,
                        "random_delays": True,
                        "media_variation": True,
                        "anti_detection_level": "high"
                    },
                    "fingerprint_config": {
                        "device_rotation": True,
                        "session_rotation": True,
                        "proxy_rotation": False,
                        "user_agent_rotation": True
                    }
                }
            ]
            import json
            with open('config/accounts.json', 'w') as f:
                json.dump(sample_accounts, f, indent=2)
            logger.info("✅ Created sample accounts.json")
        
        # Create sample captions.txt
        if not Path('assets/captions.txt').exists():
            sample_captions = [
                "🚀 Exciting times ahead! #Threads #SocialMedia",
                "✨ Building something amazing #Innovation #Tech",
                "🌟 Every day is a new opportunity #Motivation #Success",
                "💡 Great ideas come from great minds #Creativity #Inspiration",
                "🎯 Focus on your goals #Productivity #Growth"
            ]
            with open('assets/captions.txt', 'w') as f:
                f.write('\n'.join(sample_captions))
            logger.info("✅ Created sample captions.txt")
        
        # Create sample user_agents.txt
        if not Path('config/user_agents.txt').exists():
            sample_user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
            with open('config/user_agents.txt', 'w') as f:
                f.write('\n'.join(sample_user_agents))
            logger.info("✅ Created sample user_agents.txt")

async def main():
    """Main entry point for the backend bot"""
    try:
        logger.info("🚀 Enhanced Threads Bot Backend Starting...")
        
        # Setup environment
        setup_environment()
        
        # Check required files
        check_required_files()
        
        # Initialize database
        logger.info("🗄️  Initializing database...")
        from config.db import init_database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Import and run the bot
        logger.info("🤖 Initializing bot...")
        from core.bot import EnhancedThreadsBot, BotConfig
        
        # Create configuration
        config = BotConfig()
        
        # Create and run bot
        bot = EnhancedThreadsBot(config)
        logger.info("✅ Bot initialized successfully")
        
        # Run the bot
        logger.info("🔄 Starting bot execution...")
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ Bot startup failed: {e}")
        raise

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 