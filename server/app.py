"""
Enhanced Threads Bot - Flask API Server
Serves API endpoints for the frontend dashboard
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
from threading import Thread
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global bot instance
bot_instance = None
bot_thread = None
bot_running = False

# Configuration
IMAGES_FOLDER = 'assets/images'
CAPTIONS_FILE = 'assets/captions.txt'
ACCOUNTS_FILE = 'config/accounts.json'

def load_captions():
    """Load captions from database with fallback to file"""
    try:
        from core.db_manager import DatabaseOperations
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        captions = loop.run_until_complete(DatabaseOperations.get_captions())
        loop.close()
        return captions
    except Exception as e:
        logger.error(f"Error loading captions from database: {e}")
        # Fallback to file
        try:
            with open(CAPTIONS_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error loading captions from file: {e}")
            return []

def save_captions(captions):
    """Save captions to database with fallback to file"""
    try:
        from core.db_manager import DatabaseOperations
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # For now, save to file as fallback
        # TODO: Implement database save
        with open(CAPTIONS_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(captions))
        loop.close()
        return True
    except Exception as e:
        logger.error(f"Error saving captions: {e}")
        return False

def get_images():
    """Get list of images in images directory"""
    try:
        from core.db_manager import DatabaseOperations
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        images = loop.run_until_complete(DatabaseOperations.get_images())
        loop.close()
        return images
    except Exception as e:
        logger.error(f"Error getting images from database: {e}")
        # Fallback to file system
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            images = []
            for file in Path(IMAGES_FOLDER).iterdir():
                if file.suffix.lower() in image_extensions:
                    images.append({
                        'id': len(images) + 1,
                        'filename': file.name,
                        'file_path': str(file),
                        'file_size': file.stat().st_size,
                        'mime_type': f'image/{file.suffix.lower()[1:]}',
                        'last_used': None,
                        'use_count': 0,
                        'created_at': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            return images
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []

def load_accounts():
    """Load accounts from database with fallback to file"""
    try:
        from core.db_manager import DatabaseOperations
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        accounts = loop.run_until_complete(DatabaseOperations.get_accounts())
        loop.close()
        return accounts
    except Exception as e:
        logger.error(f"Error loading accounts from database: {e}")
        # Fallback to file
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error loading accounts from file: {e}")
            return []

def save_accounts(accounts):
    """Save accounts to database with fallback to file"""
    try:
        from core.db_manager import DatabaseOperations
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # For now, save to file as fallback
        # TODO: Implement database save
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2)
        loop.close()
        return True
    except Exception as e:
        logger.error(f"Error saving accounts: {e}")
        return False

def run_bot():
    """Run the bot in a separate thread"""
    global bot_instance, bot_running
    try:
        from core.bot import EnhancedThreadsBot, BotConfig
        from config.db import init_database
        
        # Initialize database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(init_database())
        loop.close()
        
        # Create and run bot
        config = BotConfig()
        bot_instance = EnhancedThreadsBot(config)
        bot_running = True
        bot_instance.run()
    except Exception as e:
        logger.error(f"Bot execution failed: {e}")
        bot_running = False

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': 'running' if bot_running else 'stopped',
        'accounts_count': len(load_accounts()),
        'captions_count': len(load_captions()),
        'images_count': len(get_images())
    })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts"""
    accounts = load_accounts()
    return jsonify(accounts)

@app.route('/api/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    try:
        data = request.get_json()
        accounts = load_accounts()
        
        new_account = {
            'id': str(len(accounts) + 1),
            'username': data.get('username', ''),
            'email': data.get('email', ''),
            'password': data.get('password', ''),
            'enabled': data.get('enabled', True),
            'description': data.get('description', ''),
            'posting_schedule': {
                'frequency': 'every_5_minutes',
                'interval_minutes': 5,
                'timezone': 'UTC',
                'start_time': '00:00',
                'end_time': '23:59'
            },
            'posting_config': {
                'use_random_caption': True,
                'use_random_image': True,
                'max_posts_per_day': 288,
                'delay_between_posts_seconds': 300,
                'user_agent_rotation': True,
                'random_delays': True,
                'media_variation': True,
                'anti_detection_level': 'high'
            },
            'fingerprint_config': {
                'device_rotation': True,
                'session_rotation': True,
                'proxy_rotation': False,
                'user_agent_rotation': True
            }
        }
        
        accounts.append(new_account)
        if save_accounts(accounts):
            return jsonify(new_account), 201
        else:
            return jsonify({'error': 'Failed to save account'}), 500
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/captions', methods=['GET'])
def get_captions():
    """Get all captions"""
    captions = load_captions()
    return jsonify([{'id': i, 'text': caption} for i, caption in enumerate(captions)])

@app.route('/api/captions', methods=['POST'])
def add_caption():
    """Add a new caption"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Caption text is required'}), 400
        
        captions = load_captions()
        captions.append(text)
        
        if save_captions(captions):
            return jsonify({'id': len(captions) - 1, 'text': text}), 201
        else:
            return jsonify({'error': 'Failed to save caption'}), 500
    except Exception as e:
        logger.error(f"Error adding caption: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/images', methods=['GET'])
def get_images_list():
    """Get all images"""
    images = get_images()
    return jsonify(images)

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    global bot_thread, bot_running
    
    if bot_running:
        return jsonify({'error': 'Bot is already running'}), 400
    
    try:
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Wait a moment to check if bot started successfully
        time.sleep(2)
        
        if bot_running:
            return jsonify({'message': 'Bot started successfully'}), 200
        else:
            return jsonify({'error': 'Failed to start bot'}), 500
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    global bot_running
    
    if not bot_running:
        return jsonify({'error': 'Bot is not running'}), 400
    
    try:
        bot_running = False
        # TODO: Implement proper bot shutdown
        return jsonify({'message': 'Bot stopped successfully'}), 200
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get bot status"""
    return jsonify({
        'status': 'running' if bot_running else 'stopped',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 