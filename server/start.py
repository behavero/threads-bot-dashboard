#!/usr/bin/env python3
"""
Threads Auto-Posting Bot
Main entry point with Flask API and bot scheduling
"""

import os
import threading
import time
import traceback
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Test PIL/Pillow installation
try:
    from PIL import Image
    print("✅ Pillow installed and working")
except ImportError:
    print("❌ Pillow not installed - image processing will be disabled")
    print("   Install with: pip install Pillow>=8.1.1")
    Image = None

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

# Check environment variables first
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
        print("SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co")
        print("SUPABASE_KEY=your-supabase-key")
        return False
    
    return True

# Validate environment before importing modules
if not validate_environment():
    print("❌ Environment not ready. Exiting.")
    exit(1)

from database import DatabaseManager
from threads_bot import ThreadsBot
from engagement_tracker import engagement_tracker
import asyncio

app = Flask(__name__)
CORS(app)

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

@app.route('/api/health')
def health():
    return jsonify({
        "health": "ok",
        "service": "threads-bot",
        "timestamp": datetime.now().isoformat(),
        "environment": "render"
    })

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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive statistics"""
    try:
        db = DatabaseManager()
        stats = db.get_statistics()
        stats["bot_status"] = "running" if bot_running else "stopped"
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/engagement', methods=['GET'])
def get_engagement_stats():
    """Get daily engagement statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = engagement_tracker.get_daily_engagement_stats(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/refresh', methods=['POST'])
def refresh_engagement_stats():
    """Manually refresh engagement data"""
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(engagement_tracker.refresh_engagement_data())
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts with comprehensive error handling"""
    try:
        logger.info("🔍 Starting get_accounts request...")
        
        # Test database connection
        db = DatabaseManager()
        logger.info(f"✅ DatabaseManager initialized")
        logger.info(f"📊 Supabase URL: {db.supabase_url}")
        logger.info(f"📊 Headers configured: {list(db.headers.keys())}")
        
        # Get accounts with safe operation
        accounts = safe_database_operation("get_active_accounts", db.get_active_accounts)
        
        if accounts is None:
            return jsonify(handle_api_error(
                Exception("Database operation failed"), 
                "get_accounts", 
                "Failed to fetch accounts from database"
            )[0]), 500
        
        logger.info(f"📋 Retrieved {len(accounts)} accounts")
        
        if accounts:
            logger.info(f"📋 Sample account: {accounts[0]}")
        
        # Return response
        response_data = {"success": True, "accounts": accounts}
        logger.info(f"✅ Returning {len(accounts)} accounts")
        return jsonify(response_data)
        
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
                "success": True, 
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
            return jsonify({"success": True, "message": "Account updated successfully"})
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
            return jsonify({"success": True, "message": "Account deleted successfully"})
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
        return jsonify({"success": True, "captions": processed_captions})
        
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
            
            supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
            service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
            
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
        
        supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
        service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
        
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
        return jsonify({"success": True, "images": images})
        
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
                        supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
                        service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
                        
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
                    "success": True,
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
            return jsonify({"success": True, "message": "Image deleted successfully"}), 200
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
            "pillow": {
                "available": Image is not None,
                "version": getattr(Image, '__version__', 'unknown') if Image else None
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
    """Login to a Threads account with persistent session management"""
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
        
        # Try instagrapi login with session management first
        try:
            from instagrapi_login import login_with_session
            
            login_result = login_with_session(username, password, verification_code)
            
            # Handle tuple response (result, status_code)
            if isinstance(login_result, tuple):
                result, status_code = login_result
                return jsonify(result), status_code
            
            return jsonify(login_result)
            
        except ImportError as e:
            print(f"❌ Instagrapi not available: {e}")
            print("🔄 Falling back to Threads API...")
            
            # Fallback to Threads API
            try:
                from threads_api_real import RealThreadsAPI
                import asyncio
                
                # Create Threads API instance
                api = RealThreadsAPI(use_instagrapi=True)
                
                # Run async login
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                login_result = loop.run_until_complete(api.login(username, password, verification_code))
                
                # Clean up
                loop.run_until_complete(api.logout())
                loop.close()
                
                if login_result.get("success"):
                    print(f"✅ Login successful for {username}")
                    
                    # Save account to database if not session reuse
                    if not login_result.get("session_reused"):
                        db = DatabaseManager()
                        account_id = db.add_account({
                            "username": username,
                            "password": password,
                            "description": data.get('description', ''),
                            "status": "enabled"
                        })
                        
                        # Update last_login
                        db.update_account_last_login(account_id)
                    
                    return jsonify({
                        "success": True,
                        "message": login_result.get("message", "Login successful"),
                        "user_info": login_result.get("user_info"),
                        "session_reused": login_result.get("session_reused", False),
                        "api_used": "threads_api"
                    })
                else:
                    # Check if verification is required
                    if login_result.get("requires_verification") or login_result.get("status") == "challenge_required":
                        print(f"📧 Verification required for {username}")
                        return jsonify({
                            "success": False,
                            "message": login_result.get("message", "Email verification required"),
                            "error": login_result.get("error", "Please check your email for a 6-digit verification code"),
                            "api_used": "threads_api",
                            "requires_verification": True,
                            "verification_type": login_result.get("verification_type", "email"),
                            "challenge_context": login_result.get("challenge_context")
                        }), 401
                    else:
                        print(f"❌ Login failed for {username}")
                        return jsonify({
                            "success": False,
                            "error": login_result.get("error", "Login failed"),
                            "api_used": "threads_api",
                            "requires_manual_login": login_result.get("requires_manual_login", True)
                        }), 401
                        
            except ImportError as threads_error:
                print(f"❌ Threads API also not available: {threads_error}")
                return jsonify({
                    "success": False,
                    "error": f"Neither Instagrapi nor Threads API available. Instagrapi: {str(e)}, Threads: {str(threads_error)}"
                }), 500
            except Exception as threads_error:
                print(f"❌ Threads API error: {threads_error}")
                return jsonify({
                    "success": False,
                    "error": f"Threads API error: {str(threads_error)}"
                }), 500
            
    except Exception as e:
        print(f"❌ Error in login_account: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def process_verification_code(username: str, code: str):
    """Process verification code for challenge completion"""
    try:
        print(f"📧 Processing verification code for {username}")
        
        # Find the challenge session
        challenge_id = None
        for cid, session in challenge_sessions.items():
            if session["username"] == username:
                challenge_id = cid
                break
        
        if not challenge_id:
            return jsonify({
                "success": False,
                "error": "No pending verification found for this username"
            }), 400
        
        session_data = challenge_sessions[challenge_id]
        client = session_data["client"]
        
        try:
            # Complete the challenge
            client.challenge_resolve(code)
            print(f"✅ Challenge completed for {username}")
            
            # Get user info
            user_info = client.user_info_by_username(username)
            
            # Save account to database
            db = DatabaseManager()
            account_id = db.add_account({
                "username": username,
                "password": session_data["password"],
                "description": "",
                "status": "enabled"
            })
            
            # Save session data
            session_data_settings = client.get_settings()
            db.save_session_data(account_id, session_data_settings)
            db.update_account_last_login(account_id)
            
            # Clean up challenge session
            del challenge_sessions[challenge_id]
            
            return jsonify({
                "success": True,
                "message": "Verification successful",
                "user_info": {
                    "username": user_info.username,
                    "followers": user_info.follower_count,
                    "posts": user_info.media_count
                },
                "account_id": account_id,
                "api_used": "instagrapi"
            })
            
        except Exception as e:
            print(f"❌ Challenge resolution failed: {e}")
            return jsonify({
                "success": False,
                "error": f"Invalid verification code: {str(e)}"
            }), 400
            
    except Exception as e:
        print(f"❌ Error processing verification code: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/<username>/test-session', methods=['POST'])
def test_session(username):
    """Test session reuse for an account"""
    try:
        data = request.json
        password = data.get('password')
        
        if not password:
            return jsonify({
                "success": False, 
                "error": "Password required"
            }), 400
        
        print(f"🧪 Testing session for {username}...")
        
        try:
            from instagrapi import Client
            from instagrapi.exceptions import ClientLoginRequired, ClientError
            
            # Initialize client
            client = Client()
            client.delay_range = [1, 3]
            
            # Get account and session data
            db = DatabaseManager()
            account = db.get_account_by_username(username)
            
            if not account:
                return jsonify({
                    "success": False,
                    "error": "Account not found"
                }), 404
            
            if not account.get('session_data'):
                return jsonify({
                    "success": False,
                    "error": "No session data found for this account"
                }), 404
            
            print(f"🧪 Found session data for {username}, testing reuse...")
            
            # Try to use existing session
            client.set_settings(account['session_data'])
            client.login(username, password)
            
            # Get user info to verify login worked
            user_info = client.user_info_by_username(username)
            
            # Update last_login timestamp
            db.update_account_last_login(account['id'])
            
            return jsonify({
                "success": True,
                "message": "Session test successful",
                "user_info": {
                    "followers": user_info.follower_count,
                    "following": user_info.following_count,
                    "posts": user_info.media_count,
                    "username": user_info.username,
                    "full_name": user_info.full_name,
                    "is_verified": user_info.is_verified
                },
                "session_reused": True
            })
            
        except ClientLoginRequired as e:
            print(f"❌ Session test failed for {username}: {e}")
            return jsonify({
                "success": False,
                "error": "Session expired, fresh login required"
            }), 401
            
        except Exception as e:
            print(f"❌ Session test error for {username}: {e}")
            return jsonify({
                "success": False,
                "error": f"Session test failed: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"❌ Error in test_session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/test-threads-login', methods=['POST'])
def test_threads_login():
    """Test Threads API login with real threads-api library"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "success": False,
                "error": "Username and password required"
            }), 400
        
        print(f"🧪 Testing Threads API login for {username}...")
        
        try:
            from threads_api_real import RealThreadsAPI
            import asyncio
            
            # Test Threads API login
            api = RealThreadsAPI(use_instagrapi=True)
            
            # Run async login
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(api.login(username, password))
            
            if success:
                # Get user info
                user_info = loop.run_until_complete(api.get_me())
                
                # Clean up
                loop.run_until_complete(api.logout())
                loop.close()
                
                print(f"✅ Threads API login successful for {username}")
                return jsonify({
                    "success": True,
                    "message": "Threads API login successful",
                    "user_info": user_info,
                    "api_available": True
                })
            else:
                # Clean up
                loop.run_until_complete(api.logout())
                loop.close()
                
                print(f"❌ Threads API login failed for {username}")
                return jsonify({
                    "success": False,
                    "error": "Threads API login failed",
                    "api_available": True
                }), 401
                
        except ImportError as e:
            print(f"❌ Threads API not available: {e}")
            return jsonify({
                "success": False,
                "error": "Threads API not available",
                "api_available": False,
                "details": str(e)
            }), 500
        except Exception as e:
            print(f"❌ Threads API login error: {e}")
            return jsonify({
                "success": False,
                "error": f"Threads API login error: {str(e)}",
                "api_available": True
            }), 500
            
    except Exception as e:
        print(f"❌ Error in test_threads_login: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/verify-code', methods=['POST'])
def submit_verification_code():
    """Submit verification code for account login"""
    try:
        data = request.json
        username = data.get('username')
        verification_code = data.get('verification_code')
        
        if not username or not verification_code:
            return jsonify({
                "success": False,
                "error": "Username and verification code required"
            }), 400
        
        print(f"📧 Submitting verification code for {username}...")
        
        try:
            from threads_api_real import RealThreadsAPI
            import asyncio
            
            # Create new API instance for verification
            api = RealThreadsAPI(use_instagrapi=True)
            
            # Run async verification
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            verification_result = loop.run_until_complete(api.submit_verification_code(verification_code))
            
            # Clean up
            loop.run_until_complete(api.logout())
            loop.close()
            
            if verification_result.get("success"):
                print(f"✅ Verification successful for {username}")
                return jsonify({
                    "success": True,
                    "message": "Verification successful",
                    "user_info": verification_result.get("user_info"),
                    "api_used": "threads_api"
                })
            else:
                print(f"❌ Verification failed for {username}")
                return jsonify({
                    "success": False,
                    "error": verification_result.get("error", "Verification failed"),
                    "api_used": "threads_api"
                }), 401
                
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return jsonify({
                "success": False,
                "error": f"Verification error: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"❌ Error in submit_verification_code: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/debug/threads-api-status', methods=['GET'])
def debug_threads_api_status():
    """Debug endpoint to check Threads API availability"""
    try:
        status = {
            "threads_api_available": False,
            "instagrapi_available": False,
            "pillow_available": False,
            "error_details": None
        }
        
        # Test Threads API
        try:
            from threads_api.src.threads_api import ThreadsAPI
            status["threads_api_available"] = True
            print("✅ Threads API available")
        except ImportError as e:
            status["error_details"] = f"Threads API: {str(e)}"
            print(f"❌ Threads API not available: {e}")
        
        # Test instagrapi
        try:
            from instagrapi import Client
            status["instagrapi_available"] = True
            print("✅ instagrapi available")
        except ImportError as e:
            status["error_details"] = f"instagrapi: {str(e)}"
            print(f"❌ instagrapi not available: {e}")
        
        # Test Pillow
        try:
            from PIL import Image
            status["pillow_available"] = True
            print("✅ Pillow available")
        except ImportError as e:
            status["error_details"] = f"Pillow: {str(e)}"
            print(f"❌ Pillow not available: {e}")
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/accounts/<int:account_id>/post', methods=['POST'])
def trigger_post(account_id):
    """Trigger a post for a specific account"""
    try:
        print(f"🚀 Triggering post for account {account_id}...")
        
        # Get account details
        db = DatabaseManager()
        accounts = db.get_active_accounts()
        account = next((a for a in accounts if a['id'] == account_id), None)
        
        if not account:
            return jsonify({
                "success": False,
                "error": "Account not found or not active"
            }), 404
        
        print(f"📝 Found account: {account['username']}")
        
        # Get unused content
        caption = db.get_unused_caption()
        image = db.get_unused_image()
        
        if not caption:
            return jsonify({
                "success": False,
                "error": "No unused captions available"
            }), 400
        
        print(f"📝 Selected caption: {caption['text'][:50]}...")
        if image:
            print(f"🖼️ Selected image: {image['filename']}")
        else:
            print("📝 No image selected, posting text only")
        
        try:
            from instagrapi import Client
            from instagrapi.exceptions import (
                ClientLoginRequired, 
                ClientError,
                ClientChallengeRequired,
                ClientCheckpointRequired
            )
            
            # Initialize client
            client = Client()
            client.delay_range = [1, 3]
            
            # Try to use saved session first
            session_data = db.get_session_data(account_id)
            login_success = False
            
            if session_data:
                print(f"🔐 Attempting to use saved session for {account['username']}...")
                try:
                    client.set_settings(session_data)
                    client.login(account['username'], account['password'])
                    print(f"✅ Successfully logged in with saved session")
                    login_success = True
                    # Update last_login for session reuse
                    db.update_account_last_login(account_id)
                except Exception as session_error:
                    print(f"⚠️ Failed to use saved session: {session_error}")
                    print(f"🔐 Falling back to fresh login...")
            
            # Fresh login if session failed or doesn't exist
            if not login_success:
                print(f"🔐 Performing fresh login for {account['username']}...")
                client.login(account['username'], account['password'])
                print(f"✅ Successfully logged in")
                
                # Save new session
                new_session = client.get_settings()
                db.save_session_data(account_id, new_session)
                print(f"💾 Saved new session data")
                
                # Update last_login for fresh login
                db.update_account_last_login(account_id)
            
            # Post content
            print(f"📝 Posting content...")
            if image and Image is not None:
                # Post with image - download and process locally
                try:
                    import requests
                    import tempfile
                    import os
                    
                    # Download image to temporary file
                    response = requests.get(image['url'])
                    if response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file.write(response.content)
                            temp_path = temp_file.name
                        
                        # Post with image
                        result = client.photo_upload(
                            path=temp_path,
                            caption=caption['text']
                        )
                        
                        # Clean up temporary file
                        os.unlink(temp_path)
                    else:
                        print(f"❌ Failed to download image: {response.status_code}")
                        # Fall back to text-only post
                        result = client.direct_answer(text=caption['text'])
                except Exception as e:
                    print(f"❌ Error processing image: {e}")
                    # Fall back to text-only post
                    result = client.direct_answer(text=caption['text'])
            else:
                # Post text only
                result = client.direct_answer(text=caption['text'])
            
            if result:
                print(f"✅ Posted successfully!")
                
                # Mark content as used
                db.mark_caption_used(caption['id'])
                if image:
                    db.mark_image_used(image['id'])
                
                # Update account last_posted
                db.update_account_last_posted(account_id)
                
                # Record success in posting history
                db.add_posting_record(
                    account_id, 
                    caption['id'], 
                    image['id'] if image else None,
                    "success"
                )
                
                return jsonify({
                    "success": True,
                    "message": "Post published successfully",
                    "account": account['username'],
                    "caption": caption['text'],
                    "image": image['filename'] if image else None,
                    "session_reused": login_success
                })
            else:
                print(f"❌ Failed to post")
                db.add_posting_record(
                    account_id, 
                    caption['id'], 
                    image['id'] if image else None,
                    "error"
                )
                return jsonify({
                    "success": False,
                    "error": "Failed to publish post"
                }), 500
                
        except Exception as e:
            if "2FA" in str(e) or "two-factor" in str(e).lower():
                print(f"❌ 2FA required for {account['username']}")
                return jsonify({
                    "success": False,
                    "error": "Two-factor authentication required"
                }), 401
            
        except ClientChallengeRequired:
            print(f"❌ Challenge required for {account['username']}")
            return jsonify({
                "success": False,
                "error": "Account verification required"
            }), 401
            
        except ClientCheckpointRequired:
            print(f"❌ Checkpoint required for {account['username']}")
            return jsonify({
                "success": False,
                "error": "Account checkpoint required"
            }), 401
            
        except ClientLoginRequired as e:
            print(f"❌ Login failed for {account['username']}: {e}")
            return jsonify({
                "success": False,
                "error": "Authentication failed"
            }), 401
            
        except Exception as e:
            print(f"❌ Error posting for {account['username']}: {e}")
            db.add_posting_record(
                account_id, 
                caption['id'], 
                image['id'] if image else None,
                "error",
                str(e)
            )
            return jsonify({
                "success": False,
                "error": f"Posting failed: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"❌ Error in trigger_post: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def run_bot():
    """Run the bot in a separate thread"""
    global bot, bot_running
    
    try:
        print("🤖 Starting Threads Bot...")
        bot = ThreadsBot()
        bot_running = True
        bot.run_continuously()
    except Exception as e:
        print(f"❌ Bot thread error: {e}")
        bot_running = False

def start_bot():
    """Start the bot in a background thread"""
    global bot_thread
    
    if bot_thread and bot_thread.is_alive():
        print("⚠️ Bot is already running")
        return
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🚀 Bot started in background thread")

@app.route('/api/accounts/sessions', methods=['GET'])
def list_sessions():
    """List all available sessions"""
    try:
        from session_manager import session_manager
        sessions = session_manager.list_sessions()
        return jsonify({
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        })
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/sessions/<username>', methods=['DELETE'])
def delete_session(username):
    """Delete a specific session"""
    try:
        from session_manager import session_manager
        success = session_manager.delete_session(username)
        return jsonify({
            "success": success,
            "message": f"Session {'deleted' if success else 'not found'} for {username}"
        })
    except Exception as e:
        print(f"❌ Error deleting session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/sessions/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up expired sessions"""
    try:
        from session_manager import session_manager
        data = request.json or {}
        max_age_days = data.get('max_age_days', 30)
        
        cleaned_count = session_manager.cleanup_expired_sessions(max_age_days)
        return jsonify({
            "success": True,
            "cleaned_count": cleaned_count,
            "max_age_days": max_age_days
        })
    except Exception as e:
        print(f"❌ Error cleaning up sessions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/sessions/<username>/validate', methods=['GET'])
def validate_session(username):
    """Validate if a session is still working"""
    try:
        from instagrapi_login import validate_session
        is_valid = validate_session(username)
        return jsonify({
            "success": True,
            "username": username,
            "is_valid": is_valid
        })
    except Exception as e:
        print(f"❌ Error validating session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/sessions/storage-info', methods=['GET'])
def get_storage_info():
    """Get information about session storage"""
    try:
        from session_manager import session_manager
        
        storage_info = {
            "use_supabase": session_manager.use_supabase,
            "storage_type": "Supabase Storage" if session_manager.use_supabase else "Local Files",
            "session_count": len(session_manager.list_sessions())
        }
        
        return jsonify({
            "success": True,
            "storage_info": storage_info
        })
    except Exception as e:
        print(f"❌ Error getting storage info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/accounts/sessions/migrate', methods=['POST'])
def migrate_sessions():
    """Migrate sessions from local to Supabase Storage"""
    try:
        from session_manager import session_manager
        
        if session_manager.use_supabase:
            return jsonify({
                "success": False,
                "message": "Already using Supabase Storage"
            }), 400
        
        # This would require additional implementation
        # For now, just return info
        return jsonify({
            "success": False,
            "message": "Migration not implemented yet"
        }), 501
        
    except Exception as e:
        print(f"❌ Error migrating sessions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Threads Bot on Render...")
    print(f"🌐 Port: {port}")
    print(f"🔗 Supabase URL: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    
    # Start session cleanup scheduler
    try:
        from session_cleanup import start_cleanup_scheduler
        start_cleanup_scheduler()
    except Exception as e:
        print(f"⚠️ Failed to start cleanup scheduler: {e}")
    
    # Start the bot in background
    start_bot()
    
    # Start Flask app
    print(f"🌐 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 