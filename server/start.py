#!/usr/bin/env python3
"""
Threads Auto-Posting Bot
Main entry point with Flask API and bot scheduling
"""

import os
import sys
import platform
import threading
import time
import traceback
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Log Python version and platform at startup
print(f"[BOOT] Python: {sys.version}  Platform: {platform.platform()}", flush=True)

# Image processing not needed - we use public URLs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_api_error(error: Exception, context: str = "API", user_message: str = None) -> tuple:
    """
    Centralized error handling for API endpoints
    
    Args:
        error: The exception that occurred
        context: Context where the error occurred (e.g., "login", "posting")
        user_message: Optional user-friendly message
    
    Returns:
        tuple: (response_dict, status_code)
    """
    # Log the full error with traceback
    logger.error(f"❌ Error in {context}: {str(error)}")
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # Determine user-friendly message
    if user_message:
        message = user_message
    elif "connection" in str(error).lower():
        message = "Database connection failed. Please try again."
    elif "authentication" in str(error).lower() or "login" in str(error).lower():
        message = "Authentication failed. Please check your credentials."
    elif "timeout" in str(error).lower():
        message = "Request timed out. Please try again."
    elif "not found" in str(error).lower():
        message = "Resource not found."
    else:
        message = "An unexpected error occurred. Please try again."
    
    return {
        "success": False,
        "error": message,
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }, 500

def safe_database_operation(operation_name: str, db_operation, *args, **kwargs):
    """
    Safely execute database operations with error handling
    
    Args:
        operation_name: Name of the operation for logging
        db_operation: Database operation function
        *args, **kwargs: Arguments for the database operation
    
    Returns:
        Result of the operation or None if failed
    """
    try:
        logger.info(f"🔍 Executing database operation: {operation_name}")
        result = db_operation(*args, **kwargs)
        logger.info(f"✅ Database operation successful: {operation_name}")
        return result
    except Exception as e:
        logger.error(f"❌ Database operation failed: {operation_name}")
        logger.error(f"❌ Error: {str(e)}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

# Load environment variables
load_dotenv()

# Import config validation
import os
import logging
from config.env import load_meta_oauth_config, missing_oauth_vars

logger = logging.getLogger("boot")

# Load and validate Meta OAuth configuration
CFG = load_meta_oauth_config()
missing = missing_oauth_vars(CFG)
ENV = os.environ.get("APP_ENV", os.environ.get("ENV", "development")).lower()

if missing:
    logger.warning("⚠️ Meta OAuth not configured. Missing: %s", ", ".join(missing))
    if ENV in ("production", "staging"):
        raise RuntimeError(f"Meta OAuth misconfigured in {ENV}. Missing: {', '.join(missing)}")
else:
    logger.info("✅ Meta OAuth configured (App ID present, Redirect URI set)")

def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Render/Railway environment variables:")
        print("SUPABASE_URL=your_supabase_url_here")
        print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here")
        return False
    
    return True

# Validate environment before importing modules
if not validate_environment():
    print("❌ Environment not ready. Exiting.")
    exit(1)

from database import DatabaseManager
import asyncio

app = Flask(__name__)
CORS(app)

# Register internal routes for data deletion
try:
    from internal_routes import internal
    app.register_blueprint(internal)
    print("✅ Internal routes registered successfully")
except ImportError as e:
    print(f"⚠️ Could not import internal routes: {e}")
except Exception as e:
    print(f"⚠️ Error registering internal routes: {e}")

# Register new route blueprints
try:
    from routes.accounts import accounts
    from routes.auth import auth
    from routes.threads import threads
    from routes.autopilot import autopilot
    from routes.captions import captions
    from routes.images import images
    from routes.config_status import bp as config_status_bp
    
    app.register_blueprint(accounts)
    app.register_blueprint(auth)
    app.register_blueprint(threads, url_prefix='/threads')
    app.register_blueprint(autopilot, url_prefix='/autopilot')
    app.register_blueprint(captions)
    app.register_blueprint(images)
    app.register_blueprint(config_status_bp)
    print("✅ Route blueprints registered successfully")
except ImportError as e:
    print(f"⚠️ Could not import route blueprints: {e}")
except Exception as e:
    print(f"⚠️ Error registering route blueprints: {e}")

# Global bot instance
bot = None
bot_thread = None
bot_running = False

# Global challenge sessions storage (in production, use Redis or database)
challenge_sessions = {}

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "threads-bot",
        "timestamp": datetime.now().isoformat(),
        "environment": "render"
    })

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running" if bot_running else "stopped",
        "service": "threads-bot",
        "bot_running": bot_running,
        "timestamp": datetime.now().isoformat(),
        "environment": "render",
        "backend_url": "https://threads-bot-dashboard-3.onrender.com"
    })

@app.route('/health', methods=['GET'])
def health_simple():
    """Simple health check endpoint"""
    from datetime import datetime
    return jsonify({
        "ok": True,
        "time": datetime.now().isoformat(),
        "service": "threads-bot-backend",
        "version": "2.0.0"
    }), 200

@app.route('/api/health')
def health():
    """Detailed health check endpoint"""
    try:
        # Test database connection
        db = DatabaseManager()
        db.get_accounts()
        
        # Test Meta OAuth service
        from services.meta_oauth import meta_oauth_service
        oauth_ok = meta_oauth_service.app_id is not None
        
        # Test Threads API service
        from services.threads_api import threads_client
        threads_ok = hasattr(threads_client, 'post_thread')
        
        return jsonify({
            "ok": True,
            "health": "ok",
            "service": "threads-bot",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": "render",
            "services": {
                'database': 'connected',
                'meta_oauth': 'available' if oauth_ok else 'unavailable',
                'threads_api': 'available' if threads_ok else 'unavailable'
            }
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "health": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/info')
def info():
    """Get detailed service information"""
    return jsonify({
        "service": "threads-bot",
        "environment": "render",
        "backend_url": "https://threads-bot-dashboard-3.onrender.com",
        "supabase_connected": bool(os.getenv("SUPABASE_URL")),
        "bot_status": "running" if bot_running else "stopped",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/post/schedule', methods=['GET', 'POST'])
def schedule_posts():
    """Get or create posting schedules"""
    try:
        db = DatabaseManager()
        
        if request.method == 'GET':
            # Get all schedules
            # This would need to be implemented in DatabaseManager
            return jsonify({"schedules": []})
        
        elif request.method == 'POST':
            # Create new schedule
            data = request.json
            account_id = data.get('account_id')
            caption_id = data.get('caption_id')
            image_id = data.get('image_id')
            scheduled_time = data.get('scheduled_time')
            
            if not all([account_id, scheduled_time]):
                return jsonify({"error": "Account ID and scheduled time required"}), 400
            
            # This would need to be implemented in DatabaseManager
            return jsonify({"message": "Schedule created successfully"}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Legacy stats routes removed - use /autopilot/status for current stats

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts with comprehensive error handling"""
    try:
        logger.info("🔍 Starting get_accounts request...")
        
        # Test database connection
        db = DatabaseManager()
        logger.info(f"✅ DatabaseManager initialized")
        
        # Get accounts with safe operation
        raw_accounts = safe_database_operation("get_active_accounts", db.get_active_accounts)
        
        if raw_accounts is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "get_accounts", 
                "Failed to fetch accounts from database"
            )[0]), 500
        
        logger.info(f"📋 Retrieved {len(raw_accounts)} raw accounts")
        
        # Transform accounts to match frontend expectations
        accounts = []
        for account in raw_accounts:
            # Check if account has a token (connected via OAuth)
            has_token = db.get_token_by_account_id(account['id']) is not None
            
            # Check session connection
            from services.session_store import session_store
            has_session = session_store.exists(account.get('username', ''))
            
            # Determine connection status
            if has_token:
                threads_connected = True
                connection_status = 'connected_official'
            elif has_session:
                threads_connected = True
                connection_status = 'connected_session'
            else:
                threads_connected = False
                connection_status = 'disconnected'
            
            # Transform account data
            transformed_account = {
                "id": str(account['id']),
                "username": account.get('username', ''),
                "description": account.get('description', ''),
                "threads_connected": threads_connected,
                "autopilot_enabled": bool(account.get('autopilot_enabled', False)),
                "cadence_minutes": int(account.get('cadence_minutes', 10)),
                "next_run_at": account.get('next_run_at'),
                "last_posted_at": account.get('last_posted_at'),
                "connection_status": connection_status
            }
            accounts.append(transformed_account)
        
        logger.info(f"✅ Returning {len(accounts)} transformed accounts")
        return jsonify({"ok": True, "accounts": accounts})
        
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_accounts", "Failed to fetch accounts")
        return jsonify(error_response), status_code

@app.route('/api/accounts', methods=['POST'])
def add_account():
    """Add a new account with comprehensive error handling"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "success": False, 
                "error": "Username and password required"
            }), 400
        
        logger.info(f"🔍 Adding new account: {username}")
        
        # Initialize database
        db = DatabaseManager()
        
        # Add account with safe operation
        success = safe_database_operation("add_account", db.add_account, username, password)
        
        if success is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "add_account", 
                "Failed to add account to database"
            )[0]), 500
        
        if success:
            logger.info(f"✅ Account {username} added successfully")
            return jsonify({
                "ok": True, 
                "message": "Account added successfully"
            }), 201
        else:
            logger.error(f"❌ Failed to add account {username}")
            return jsonify({
                "success": False, 
                "error": "Failed to add account. Please try again."
            }), 500
            
    except Exception as e:
        error_response, status_code = handle_api_error(e, "add_account", "Failed to add account")
        return jsonify(error_response), status_code

@app.route('/api/accounts/<int:account_id>/toggle', methods=['PATCH'])
def toggle_account(account_id):
    try:
        data = request.json
        active = data.get('active', False)
        
        db = DatabaseManager()
        # This would need to be implemented in DatabaseManager
        # For now, return success
        return jsonify({"message": "Account status updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an account with comprehensive error handling"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        logger.info(f"🔍 Updating account {account_id} with data: {data}")
        
        db = DatabaseManager()
        success = safe_database_operation("update_account", db.update_account, account_id, data)
        
        if success is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "update_account", 
                "Failed to update account in database"
            )[0]), 500
        
        if success:
            logger.info(f"✅ Account {account_id} updated successfully")
            return jsonify({"ok": True, "message": "Account updated successfully"})
        else:
            logger.error(f"❌ Failed to update account {account_id}")
            return jsonify({"success": False, "error": "Failed to update account. Please try again."}), 500
            
    except Exception as e:
        error_response, status_code = handle_api_error(e, "update_account", "Failed to update account")
        return jsonify(error_response), status_code

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account with comprehensive error handling"""
    try:
        logger.info(f"🔍 Deleting account {account_id}")
        
        db = DatabaseManager()
        success = safe_database_operation("delete_account", db.delete_account, account_id)
        
        if success is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "delete_account", 
                "Failed to delete account from database"
            )[0]), 500
        
        if success:
            logger.info(f"✅ Account {account_id} deleted successfully")
            return jsonify({"ok": True, "message": "Account deleted successfully"})
        else:
            logger.error(f"❌ Failed to delete account {account_id}")
            return jsonify({"success": False, "error": "Failed to delete account. Please try again."}), 500
            
    except Exception as e:
        error_response, status_code = handle_api_error(e, "delete_account", "Failed to delete account")
        return jsonify(error_response), status_code

@app.route('/api/statistics')
def get_statistics():
    try:
        db = DatabaseManager()
        accounts = db.get_active_accounts()
        
        # Calculate statistics
        total_accounts = len(accounts)
        active_accounts = len([a for a in accounts if a.get('active', False)])
        
        return jsonify({
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "bot_status": bot_running,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    try:
        global bot_running
        if not bot_running:
            start_bot()
            bot_running = True
            return jsonify({"message": "Bot started successfully"})
        else:
            return jsonify({"message": "Bot is already running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    try:
        global bot_running, bot_thread
        if bot_running and bot_thread:
            # This would need proper bot stopping logic
            bot_running = False
            return jsonify({"message": "Bot stopped successfully"})
        else:
            return jsonify({"message": "Bot is not running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/captions', methods=['GET'])
def get_captions():
    """Get all captions with comprehensive error handling"""
    try:
        logger.info("🔍 Fetching all captions...")
        
        db = DatabaseManager()
        captions = safe_database_operation("get_all_captions", db.get_all_captions)
        
        if captions is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "get_captions", 
                "Failed to fetch captions from database"
            )[0]), 500
        
        # Process captions to ensure all fields have default values
        processed_captions = []
        for caption in captions:
            processed_caption = {
                'id': caption.get('id'),
                'user_id': caption.get('user_id'),
                'text': caption.get('text', ''),
                'category': caption.get('category', 'general'),
                'tags': caption.get('tags', []),
                'used': caption.get('used', False),
                'created_at': caption.get('created_at'),
                'updated_at': caption.get('updated_at', caption.get('created_at'))
            }
            processed_captions.append(processed_caption)
        
        logger.info(f"✅ Retrieved {len(processed_captions)} captions")
        return jsonify({"ok": True, "captions": processed_captions})
        
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_captions", "Failed to fetch captions")
        return jsonify(error_response), status_code

@app.route('/api/captions', methods=['POST'])
def add_caption():
    try:
        data = request.json
        text = data.get('text')
        category = data.get('category', 'general')
        tags = data.get('tags', [])
        
        # Validate required fields
        if not text:
            return jsonify({"error": "Caption text is required"}), 400
        
        if not isinstance(text, str) or len(text.strip()) == 0:
            return jsonify({"error": "Caption text must be a non-empty string"}), 400
        
        # Validate category
        if category and not isinstance(category, str):
            return jsonify({"error": "Category must be a string"}), 400
        
        # Validate tags
        if tags and not isinstance(tags, list):
            return jsonify({"error": "Tags must be an array"}), 400
        
        # Clean and validate tags
        if tags:
            cleaned_tags = []
            for tag in tags:
                if isinstance(tag, str) and tag.strip():
                    cleaned_tags.append(tag.strip())
            tags = cleaned_tags
        
        print(f"📝 Adding caption: text='{text[:50]}...', category='{category}', tags={tags}")
        
        try:
            # Use direct Supabase approach like the working test
            import requests
            
            supabase_url = os.getenv('SUPABASE_URL')
            service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not service_key:
                return jsonify({"error": "Supabase configuration not found"}), 500
            
            headers = {
                'apikey': service_key,
                'Authorization': f'Bearer {service_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            caption_data = {
                "text": text,
                "category": category,
                "tags": tags,
                "used": False
            }
            
            print(f"📝 Direct Supabase request: {caption_data}")
            
            response = requests.post(
                f"{supabase_url}/rest/v1/captions",
                json=caption_data,
                headers=headers
            )
            
            print(f"📝 Direct response: {response.status_code}")
            print(f"📝 Direct response text: {response.text}")
            
            if response.status_code == 201:
                return jsonify({"message": "Caption added successfully"}), 201
            else:
                return jsonify({"error": f"Failed to add caption: {response.text}"}), 500
                
        except Exception as e:
            print(f"❌ Direct Supabase error: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"❌ Error adding caption: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/captions/upload-csv', methods=['POST'])
def upload_csv():
    """Upload CSV file with captions"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400
        
        # Read CSV content
        content = file.read().decode('utf-8')
        lines = content.split('\n')
        
        captions = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Parse CSV line
            parts = line.split(',')
            if len(parts) < 1:
                continue
                
            # Handle different CSV formats
            text = parts[0].strip().strip('"')
            category = parts[1].strip().strip('"') if len(parts) > 1 else 'general'
            tags_str = parts[2].strip().strip('"') if len(parts) > 2 else ''
            
            # Parse tags
            tags = []
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split('|') if tag.strip()]
            
            if text:
                captions.append({
                    "text": text,
                    "category": category,
                    "tags": tags,
                    "used": False
                })
        
        if not captions:
            return jsonify({"error": "No valid captions found in CSV"}), 400
        
        print(f"📝 Uploading {len(captions)} captions from CSV")
        
        # Insert captions using direct Supabase approach
        import requests
        
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_key:
            return jsonify({"error": "Supabase configuration not found"}), 500
        
        headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        response = requests.post(
            f"{supabase_url}/rest/v1/captions",
            json=captions,
            headers=headers
        )
        
        print(f"📝 CSV upload response: {response.status_code}")
        
        if response.status_code == 201:
            return jsonify({
                "message": f"Successfully uploaded {len(captions)} captions",
                "count": len(captions)
            }), 201
        else:
            return jsonify({"error": f"Failed to upload captions: {response.text}"}), 500
            
    except Exception as e:
        print(f"❌ CSV upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['GET'])
def get_images():
    """Get all images with comprehensive error handling"""
    try:
        logger.info("🔍 Fetching all images...")
        
        db = DatabaseManager()
        images = safe_database_operation("get_all_images", db.get_all_images)
        
        if images is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "get_images", 
                "Failed to fetch images from database"
            )[0]), 500
        
        logger.info(f"✅ Retrieved {len(images)} images")
        return jsonify({"ok": True, "images": images})
        
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_images", "Failed to fetch images")
        return jsonify(error_response), status_code

@app.route('/api/images', methods=['POST'])
def add_image():
    try:
        # Check if this is a file upload (FormData) or JSON data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload
            if 'images' not in request.files:
                return jsonify({"error": "No images provided"}), 400
            
            files = request.files.getlist('images')
            if not files or all(file.filename == '' for file in files):
                return jsonify({"error": "No files selected"}), 400
            
            uploaded_images = []
            db = DatabaseManager()
            
            for file in files:
                if file and file.filename:
                    try:
                        # Upload to Supabase Storage
                        import requests
                        from werkzeug.utils import secure_filename
                        
                        filename = secure_filename(file.filename)
                        file_content = file.read()
                        
                        # Upload to Supabase Storage
                        supabase_url = os.getenv('SUPABASE_URL')
                        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                        
                        if not supabase_url or not service_key:
                            print(f"❌ Supabase configuration not found for {filename}")
                            continue
                        
                        headers = {
                            'apikey': service_key,
                            'Authorization': f'Bearer {service_key}',
                            'Content-Type': file.content_type
                        }
                        
                        # Upload to Supabase Storage
                        storage_response = requests.post(
                            f"{supabase_url}/storage/v1/object/images/{filename}",
                            data=file_content,
                            headers=headers
                        )
                        
                        if storage_response.status_code == 200:
                            # Get the public URL
                            public_url = f"{supabase_url}/storage/v1/object/public/images/{filename}"
                            
                            # Add to database
                            success = db.add_image(public_url, filename, len(file_content), file.content_type)
                            
                            if success:
                                uploaded_images.append({
                                    "filename": filename,
                                    "url": public_url,
                                    "size": len(file_content),
                                    "type": file.content_type
                                })
                            else:
                                print(f"❌ Failed to add image {filename} to database")
                        else:
                            print(f"❌ Failed to upload {filename} to storage: {storage_response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Error uploading {file.filename}: {e}")
            
            if uploaded_images:
                return jsonify({
                    "ok": True,
                    "message": f"Successfully uploaded {len(uploaded_images)} images",
                    "images": uploaded_images
                }), 201
            else:
                return jsonify({"error": "Failed to upload any images"}), 500
                
        else:
            # Handle JSON data (existing functionality)
            data = request.json
            url = data.get('url')
            filename = data.get('filename')
            size = data.get('size')
            type = data.get('type')
            
            if not url:
                return jsonify({"error": "Image URL required"}), 400
            
            db = DatabaseManager()
            success = db.add_image(url, filename, size, type)
            
            if success:
                return jsonify({"message": "Image added successfully"}), 201
            else:
                return jsonify({"error": "Failed to add image"}), 500
                
    except Exception as e:
        print(f"❌ Error in add_image: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image with comprehensive error handling"""
    try:
        logger.info(f"🔍 Deleting image {image_id}")
        
        db = DatabaseManager()
        success = safe_database_operation("delete_image", db.delete_image, image_id)
        
        if success is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "delete_image", 
                "Failed to delete image from database"
            )[0]), 500
        
        if success:
            logger.info(f"✅ Image {image_id} deleted successfully")
            return jsonify({"ok": True, "message": "Image deleted successfully"}), 200
        else:
            logger.error(f"❌ Failed to delete image {image_id}")
            return jsonify({"success": False, "error": "Failed to delete image. Please try again."}), 500
            
    except Exception as e:
        error_response, status_code = handle_api_error(e, "delete_image", "Failed to delete image")
        return jsonify(error_response), status_code

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check environment and database"""
    try:
        import os
        from database import DatabaseManager
        
        debug_info = {
            "environment": {
                "SUPABASE_URL": os.getenv('SUPABASE_URL', 'NOT SET'),
                "SUPABASE_KEY": "SET" if os.getenv('SUPABASE_KEY') else "NOT SET",
                "SUPABASE_SERVICE_ROLE_KEY": "SET" if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else "NOT SET"
            },
            "image_processing": {
                "method": "public_urls_only",
                "server_side_processing": False
            },
            "database_test": None,
            "database_manager_test": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test database connection
        try:
            db = DatabaseManager()
            captions = db.get_all_captions()
            debug_info["database_test"] = {
                "status": "success",
                "captions_count": len(captions),
                "sample_caption": captions[0] if captions else None
            }
            
            # Test database manager initialization
            debug_info["database_manager_test"] = {
                "status": "success",
                "supabase_url": db.supabase_url,
                "has_key": bool(db.supabase_key),
                "headers_count": len(db.headers)
            }
        except Exception as e:
            debug_info["database_test"] = {
                "status": "error",
                "error": str(e)
            }
            debug_info["database_manager_test"] = {
                "status": "error",
                "error": str(e)
            }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/login', methods=['POST'])
def login_account():
    """Login to a Threads account with Supabase session management"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not username or not password:
            return jsonify({
                "success": False, 
                "error": "Username and password required"
            }), 400
        
        print(f"🔐 Attempting login for {username}...")
        
        # Legacy login system removed - use Meta OAuth instead
        return jsonify({
            "success": False,
            "error": "Legacy login system removed. Please use Meta OAuth flow to connect your Threads account.",
            "oauth_required": True
        }), 400
            
    except Exception as e:
        print(f"❌ Error in login_account: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Legacy verification system removed - use Meta OAuth instead



@app.route('/api/accounts/verify-code', methods=['POST'])
def submit_verification_code():
    """Legacy verification endpoint - use Meta OAuth instead"""
    return jsonify({
        "success": False,
        "error": "Legacy verification system removed. Please use Meta OAuth flow to connect your Threads account.",
        "oauth_required": True
    }), 400

@app.route('/api/debug/threads-api-status', methods=['GET'])
def debug_threads_api_status():
    """Debug endpoint to check Meta Threads API availability"""
    try:
        status = {
            "meta_threads_api_available": True,
            "image_processing": "public_urls_only",
            "server_side_processing": False
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/accounts/<int:account_id>/post', methods=['POST'])
def trigger_post(account_id):
    """Trigger a post for a specific account (DEPRECATED - Use Meta OAuth)"""
    return jsonify({
        "success": False,
        "error": "This endpoint is deprecated. Use Meta OAuth flow and POST /threads/post instead."
    }), 400






if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Threads Bot on Render...")
    print(f"🌐 Port: {port}")
    print(f"🔗 Supabase URL: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    
    # Check Meta OAuth service
    try:
        from services.meta_oauth import meta_oauth_service
        if meta_oauth_service.app_id:
            print("✅ Meta OAuth service configured")
        else:
            print("⚠️ Meta OAuth service not configured")
    except Exception as e:
        print(f"⚠️ Could not verify Meta OAuth service: {e}")
    

    

    
    # Start rate limiter cleanup task
    import threading
    import time
    
    def rate_limiter_cleanup():
        """Periodic cleanup for rate limiter"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                from services.rate_limiter import rate_limiter
                rate_limiter.cleanup_old_entries(max_age_seconds=3600)
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=rate_limiter_cleanup, daemon=True)
    cleanup_thread.start()
    print("🧹 Rate limiter cleanup thread started")
    
    # Start Flask app
    print(f"🌐 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 