#!/usr/bin/env python3
"""
Images API Routes
Handles image management, upload, and URL-based addition
"""

import os
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)
images = Blueprint('images', __name__)

@images.route('/api/images', methods=['GET'])
def get_images():
    """Get all images"""
    try:
        db = DatabaseManager()
        response = db._make_request(
            'GET',
            f"{db.supabase_url}/rest/v1/images",
            params={'select': '*', 'order': 'created_at.desc'}
        )
        
        if response.status_code == 200:
            images_data = response.json()
            return jsonify({
                "ok": True,
                "images": images_data
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to fetch images"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error fetching images: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@images.route('/api/images', methods=['POST'])
def add_image_by_url():
    """Add image by URL"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        url = data.get('url')
        if not url:
            return jsonify({
                "ok": False,
                "error": "Image URL is required"
            }), 400
        
        # Validate URL accessibility
        try:
            head_response = requests.head(url, timeout=10)
            if head_response.status_code != 200:
                return jsonify({
                    "ok": False,
                    "error": "Image URL is not accessible"
                }), 400
            
            content_type = head_response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return jsonify({
                    "ok": False,
                    "error": "URL does not point to an image"
                }), 400
                
        except requests.RequestException:
            return jsonify({
                "ok": False,
                "error": "Failed to validate image URL"
            }), 400
        
        # Extract filename from URL
        filename = url.split('/')[-1].split('?')[0] or 'image'
        if '.' not in filename:
            filename += '.jpg'
        
        image_data = {
            "filename": filename,
            "url": url,
            "alt_text": data.get('alt_text'),
            "use_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        db = DatabaseManager()
        response = db._make_request(
            'POST',
            f"{db.supabase_url}/rest/v1/images",
            json=image_data
        )
        
        if response.status_code == 201:
            return jsonify({
                "ok": True,
                "message": "Image added successfully"
            }), 201
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to add image"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error adding image by URL: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@images.route('/api/images/upload', methods=['POST'])
def upload_image():
    """Upload image file to Supabase Storage"""
    try:
        if 'image_file' not in request.files:
            return jsonify({
                "ok": False,
                "error": "No image file provided"
            }), 400
        
        file = request.files['image_file']
        if file.filename == '':
            return jsonify({
                "ok": False,
                "error": "No file selected"
            }), 400
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            return jsonify({
                "ok": False,
                "error": "File must be an image"
            }), 400
        
        # Generate unique filename
        import uuid
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to Supabase Storage
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "ok": False,
                "error": "Supabase configuration missing"
            }), 500
        
        # Upload file
        files = {
            'file': (unique_filename, file.read(), file.content_type)
        }
        
        headers = {
            'Authorization': f'Bearer {supabase_key}'
        }
        
        upload_response = requests.post(
            f"{supabase_url}/storage/v1/object/images/{unique_filename}",
            files=files,
            headers=headers
        )
        
        if upload_response.status_code not in [200, 201]:
            logger.error(f"Upload failed: {upload_response.text}")
            return jsonify({
                "ok": False,
                "error": "Failed to upload image to storage"
            }), 500
        
        # Get public URL
        public_url = f"{supabase_url}/storage/v1/object/public/images/{unique_filename}"
        
        # Save image record to database
        alt_text = request.form.get('alt_text', '').strip() or None
        
        image_data = {
            "filename": file.filename,
            "url": public_url,
            "alt_text": alt_text,
            "use_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        db = DatabaseManager()
        response = db._make_request(
            'POST',
            f"{db.supabase_url}/rest/v1/images",
            json=image_data
        )
        
        if response.status_code == 201:
            return jsonify({
                "ok": True,
                "url": public_url,
                "message": "Image uploaded successfully"
            }), 201
        else:
            # Try to delete uploaded file if database insert failed
            try:
                requests.delete(
                    f"{supabase_url}/storage/v1/object/images/{unique_filename}",
                    headers=headers
                )
            except:
                pass
            
            return jsonify({
                "ok": False,
                "error": "Failed to save image record"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error uploading image: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@images.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image"""
    try:
        db = DatabaseManager()
        
        # Get image info first
        response = db._make_request(
            'GET',
            f"{db.supabase_url}/rest/v1/images?id=eq.{image_id}"
        )
        
        if response.status_code != 200:
            return jsonify({
                "ok": False,
                "error": "Image not found"
            }), 404
        
        images_data = response.json()
        if not images_data:
            return jsonify({
                "ok": False,
                "error": "Image not found"
            }), 404
        
        image = images_data[0]
        
        # Delete from database
        delete_response = db._make_request(
            'DELETE',
            f"{db.supabase_url}/rest/v1/images?id=eq.{image_id}"
        )
        
        if delete_response.status_code == 204:
            # Try to delete from Supabase Storage if it's a stored file
            image_url = image.get('url', '')
            if 'storage/v1/object/public/images/' in image_url:
                try:
                    filename = image_url.split('/')[-1]
                    supabase_url = os.getenv('SUPABASE_URL')
                    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                    
                    headers = {
                        'Authorization': f'Bearer {supabase_key}'
                    }
                    
                    requests.delete(
                        f"{supabase_url}/storage/v1/object/images/{filename}",
                        headers=headers
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete file from storage: {e}")
            
            return jsonify({
                "ok": True,
                "message": "Image deleted successfully"
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to delete image"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error deleting image: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
