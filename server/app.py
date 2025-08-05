#!/usr/bin/env python3
"""
Enhanced Threads Bot Dashboard API
Flask backend for managing bot accounts, content, and monitoring
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
IMAGES_FOLDER = 'images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Bot status tracking
bot_status = {
    'running': False,
    'start_time': None,
    'accounts_processed': 0,
    'posts_created': 0,
    'errors': [],
    'last_activity': None
}

# Shadowban detection stub
shadowban_status = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_accounts():
    """Load accounts from JSON file"""
    try:
        with open('config/accounts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.error(f"Error loading accounts: {e}")
        return []

def save_accounts(accounts):
    """Save accounts to JSON file"""
    try:
        with open('config/accounts.json', 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving accounts: {e}")
        return False

def load_captions():
    """Load captions from text file"""
    try:
        with open('captions.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.error(f"Error loading captions: {e}")
        return []

def save_captions(captions):
    """Save captions to text file"""
    try:
        with open('captions.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(captions))
        return True
    except Exception as e:
        logger.error(f"Error saving captions: {e}")
        return False

def get_images():
    """Get list of images in images directory"""
    try:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        images = []
        for file in Path(IMAGES_FOLDER).iterdir():
            if file.suffix.lower() in image_extensions:
                images.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        return images
    except Exception as e:
        logger.error(f"Error getting images: {e}")
        return []

def check_shadowban_status(username):
    """Check shadowban status for an account (stub implementation)"""
    # This would integrate with the enhanced bot's shadowban detection
    # For now, return a mock status
    return {
        'shadowbanned': False,
        'confidence': 0.8,
        'last_check': datetime.now().isoformat(),
        'reasons': []
    }

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': bot_status,
        'accounts_count': len(load_accounts()),
        'captions_count': len(load_captions()),
        'images_count': len(get_images())
    })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts"""
    accounts = load_accounts()
    # Add shadowban status for each account
    for account in accounts:
        account['shadowban_status'] = check_shadowban_status(account.get('username', ''))
    return jsonify(accounts)

@app.route('/api/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    try:
        data = request.get_json()
        accounts = load_accounts()
        
        new_account = {
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
                'anti_detection_level': 'high',
                'session_timeout': 3600,
                'max_retries': 3
            },
            'fingerprint_config': {
                'device_type': 'iPhone',
                'os_version': '17.0',
                'browser_version': 'Safari/604.1',
                'screen_resolution': '1170x2532',
                'timezone': 'UTC'
            }
        }
        
        accounts.append(new_account)
        
        if save_accounts(accounts):
            return jsonify({'success': True, 'message': 'Account created successfully'}), 201
        else:
            return jsonify({'success': False, 'message': 'Failed to save account'}), 500
            
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/accounts/<username>', methods=['PUT'])
def update_account(username):
    """Update an account"""
    try:
        data = request.get_json()
        accounts = load_accounts()
        
        for account in accounts:
            if account.get('username') == username:
                # Update account fields
                for key, value in data.items():
                    if key in account:
                        account[key] = value
                
                if save_accounts(accounts):
                    return jsonify({'success': True, 'message': 'Account updated successfully'})
                else:
                    return jsonify({'success': False, 'message': 'Failed to save account'}), 500
        
        return jsonify({'success': False, 'message': 'Account not found'}), 404
        
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/accounts/<username>/toggle', methods=['POST'])
def toggle_account(username):
    """Toggle account enabled/disabled status"""
    try:
        accounts = load_accounts()
        
        for account in accounts:
            if account.get('username') == username:
                account['enabled'] = not account.get('enabled', True)
                
                if save_accounts(accounts):
                    status = 'enabled' if account['enabled'] else 'disabled'
                    return jsonify({
                        'success': True, 
                        'message': f'Account {status} successfully',
                        'enabled': account['enabled']
                    })
                else:
                    return jsonify({'success': False, 'message': 'Failed to save account'}), 500
        
        return jsonify({'success': False, 'message': 'Account not found'}), 404
        
    except Exception as e:
        logger.error(f"Error toggling account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/accounts/<username>', methods=['DELETE'])
def delete_account(username):
    """Delete an account"""
    try:
        accounts = load_accounts()
        accounts = [acc for acc in accounts if acc.get('username') != username]
        
        if save_accounts(accounts):
            return jsonify({'success': True, 'message': 'Account deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save accounts'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/captions', methods=['GET'])
def get_captions():
    """Get all captions"""
    captions = load_captions()
    return jsonify(captions)

@app.route('/api/captions', methods=['POST'])
def add_caption():
    """Add a new caption"""
    try:
        data = request.get_json()
        caption = data.get('caption', '').strip()
        
        if not caption:
            return jsonify({'success': False, 'message': 'Caption cannot be empty'}), 400
        
        captions = load_captions()
        captions.append(caption)
        
        if save_captions(captions):
            return jsonify({'success': True, 'message': 'Caption added successfully'}), 201
        else:
            return jsonify({'success': False, 'message': 'Failed to save captions'}), 500
            
    except Exception as e:
        logger.error(f"Error adding caption: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/captions/<int:index>', methods=['DELETE'])
def delete_caption(index):
    """Delete a caption by index"""
    try:
        captions = load_captions()
        
        if 0 <= index < len(captions):
            del captions[index]
            
            if save_captions(captions):
                return jsonify({'success': True, 'message': 'Caption deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Failed to save captions'}), 500
        else:
            return jsonify({'success': False, 'message': 'Invalid caption index'}), 400
            
    except Exception as e:
        logger.error(f"Error deleting caption: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/images', methods=['GET'])
def get_images_list():
    """Get list of images"""
    images = get_images()
    return jsonify(images)

@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    """Upload an image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(IMAGES_FOLDER, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                return jsonify({'success': False, 'message': 'File already exists'}), 400
            
            file.save(filepath)
            
            return jsonify({
                'success': True, 
                'message': 'Image uploaded successfully',
                'filename': filename
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/images/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Delete an image"""
    try:
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Image deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Image not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    try:
        global bot_status
        
        if bot_status['running']:
            return jsonify({'success': False, 'message': 'Bot is already running'}), 400
        
        # Start bot in background thread
        def run_bot():
            try:
                # Import and run the enhanced bot
                from core.bot import EnhancedThreadsBot, BotConfig
                
                config = BotConfig()
                bot = EnhancedThreadsBot(config)
                bot.run()
                
            except Exception as e:
                logger.error(f"Bot error: {e}")
                bot_status['errors'].append(str(e))
                bot_status['running'] = False
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        bot_status['running'] = True
        bot_status['start_time'] = datetime.now().isoformat()
        bot_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    try:
        global bot_status
        
        if not bot_status['running']:
            return jsonify({'success': False, 'message': 'Bot is not running'}), 400
        
        bot_status['running'] = False
        bot_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get bot status"""
    return jsonify(bot_status)

@app.route('/api/shadowban/check/<username>', methods=['POST'])
def check_shadowban(username):
    """Check shadowban status for an account"""
    try:
        status = check_shadowban_status(username)
        shadowban_status[username] = status
        
        return jsonify({
            'success': True,
            'username': username,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error checking shadowban: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/shadowban/status', methods=['GET'])
def get_shadowban_status():
    """Get all shadowban statuses"""
    return jsonify(shadowban_status)

@app.route('/api/images/usage', methods=['GET'])
def get_image_usage():
    """Get image usage statistics"""
    try:
        # Import the enhanced bot to access image usage tracker
        from core.bot import EnhancedThreadsBot, BotConfig
        
        # Create a temporary bot instance to access the tracker
        config = BotConfig()
        bot = EnhancedThreadsBot(config)
        
        # Get image usage statistics
        usage_stats = {}
        images_dir = Path('assets/images/')
        
        if images_dir.exists():
            for image_file in images_dir.iterdir():
                if image_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif'}:
                    stats = bot.media_variation_manager.image_usage_tracker.get_image_stats(str(image_file))
                    usage_stats[image_file.name] = {
                        'total_uses': stats['total_uses'],
                        'last_used': stats['last_used'],
                        'account_count': stats['account_count'],
                        'available': stats['available'],
                        'file_size': image_file.stat().st_size,
                        'modified': datetime.fromtimestamp(image_file.stat().st_mtime).isoformat()
                    }
        
        return jsonify({
            'success': True,
            'usage_stats': usage_stats,
            'total_images': len(usage_stats)
        })
        
    except Exception as e:
        logger.error(f"Error getting image usage: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Serve static files for React app
@app.route('/')
def serve_react_app():
    return send_from_directory('../client/build', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../client/build', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 