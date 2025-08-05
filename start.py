#!/usr/bin/env python3
"""
Startup script for Enhanced Threads Bot
Handles environment setup and starts the bot in production
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """Setup environment for production"""
    # Set default environment variables if not set
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'production'
    
    if not os.getenv('LOG_LEVEL'):
        os.environ['LOG_LEVEL'] = 'INFO'
    
    if not os.getenv('PLATFORM'):
        os.environ['PLATFORM'] = 'production'
    
    # Platform-specific setup
    platform = os.getenv('PLATFORM', 'production')
    print(f"🚀 Deploying on platform: {platform}")
    
    # Ensure required files exist
    required_files = [
        'config/accounts.json',
        'assets/captions.txt',
        'config/user_agents.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are present before deployment.")
        sys.exit(1)
    
    # Create images directory if it doesn't exist
    images_dir = Path('assets/images/')
    if not images_dir.exists():
        images_dir.mkdir(parents=True, exist_ok=True)
        print("📁 Created images directory")
    
    # Platform-specific configurations
    if platform == 'replit':
        # Replit specific setup
        print("🔧 Configuring for Replit...")
        os.environ['PYTHONPATH'] = "/home/runner/$REPL_SLUG/.config/planck/installs/python/3.11.0/lib/python3.11/site-packages"
    elif platform == 'railway':
        # Railway specific setup
        print("🔧 Configuring for Railway...")
        os.environ['PORT'] = os.getenv('PORT', '5000')
    elif platform == 'render':
        # Render specific setup
        print("🔧 Configuring for Render...")
        os.environ['PORT'] = os.getenv('PORT', '5000')
    
    print("✅ Environment setup completed")

def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Threads Bot...")
    
    # Setup environment
    setup_environment()
    
    # Import and run the bot
    try:
        from core.bot import EnhancedThreadsBot, BotConfig
        
        # Create configuration
        config = BotConfig()
        
        # Create and run bot
        bot = EnhancedThreadsBot(config)
        print("🤖 Bot initialized successfully")
        
        # Run the bot
        bot.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 