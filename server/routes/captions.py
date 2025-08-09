#!/usr/bin/env python3
"""
Captions API Routes
Handles caption management, CSV upload, and reset functionality
"""

import os
import csv
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)
captions = Blueprint('captions', __name__)

@captions.route('/api/captions', methods=['GET'])
def get_captions():
    """Get all captions"""
    try:
        db = DatabaseManager()
        response = db._make_request(
            'GET',
            f"{db.supabase_url}/rest/v1/captions",
            params={'select': '*', 'order': 'created_at.desc'}
        )
        
        if response.status_code == 200:
            captions_data = response.json()
            return jsonify({
                "ok": True,
                "captions": captions_data
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to fetch captions"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error fetching captions: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@captions.route('/api/captions', methods=['POST'])
def create_caption():
    """Create a new caption"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        text = data.get('text')
        if not text:
            return jsonify({
                "ok": False,
                "error": "Caption text is required"
            }), 400
        
        caption_data = {
            "text": text.strip(),
            "category": data.get('category'),
            "tags": data.get('tags'),
            "used": False,
            "created_at": datetime.now().isoformat()
        }
        
        db = DatabaseManager()
        response = db._make_request(
            'POST',
            f"{db.supabase_url}/rest/v1/captions",
            json=caption_data
        )
        
        if response.status_code == 201:
            return jsonify({
                "ok": True,
                "message": "Caption created successfully"
            }), 201
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to create caption"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error creating caption: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@captions.route('/api/captions/<int:caption_id>', methods=['PUT'])
def update_caption(caption_id):
    """Update a caption"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        text = data.get('text')
        if not text:
            return jsonify({
                "ok": False,
                "error": "Caption text is required"
            }), 400
        
        update_data = {
            "text": text.strip(),
            "category": data.get('category'),
            "tags": data.get('tags'),
            "updated_at": datetime.now().isoformat()
        }
        
        db = DatabaseManager()
        response = db._make_request(
            'PATCH',
            f"{db.supabase_url}/rest/v1/captions?id=eq.{caption_id}",
            json=update_data
        )
        
        if response.status_code == 204:
            return jsonify({
                "ok": True,
                "message": "Caption updated successfully"
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to update caption"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error updating caption: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@captions.route('/api/captions/<int:caption_id>', methods=['DELETE'])
def delete_caption(caption_id):
    """Delete a caption"""
    try:
        db = DatabaseManager()
        response = db._make_request(
            'DELETE',
            f"{db.supabase_url}/rest/v1/captions?id=eq.{caption_id}"
        )
        
        if response.status_code == 204:
            return jsonify({
                "ok": True,
                "message": "Caption deleted successfully"
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to delete caption"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error deleting caption: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@captions.route('/api/captions/upload', methods=['POST'])
def upload_captions_csv():
    """Upload captions from CSV file"""
    try:
        if 'csv_file' not in request.files:
            return jsonify({
                "ok": False,
                "error": "No CSV file provided"
            }), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({
                "ok": False,
                "error": "No file selected"
            }), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                "ok": False,
                "error": "File must be a CSV"
            }), 400
        
        # Parse CSV
        try:
            csv_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(csv_content.splitlines())
            
            captions_to_add = []
            for row in csv_reader:
                text = row.get('text', '').strip()
                if text:
                    caption_data = {
                        "text": text,
                        "category": row.get('category', '').strip() or None,
                        "tags": row.get('tags', '').strip().split(',') if row.get('tags', '').strip() else None,
                        "used": False,
                        "created_at": datetime.now().isoformat()
                    }
                    captions_to_add.append(caption_data)
            
            if not captions_to_add:
                return jsonify({
                    "ok": False,
                    "error": "No valid captions found in CSV"
                }), 400
            
            # Insert captions in batches
            db = DatabaseManager()
            success_count = 0
            
            for caption_data in captions_to_add:
                try:
                    response = db._make_request(
                        'POST',
                        f"{db.supabase_url}/rest/v1/captions",
                        json=caption_data
                    )
                    if response.status_code == 201:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Failed to insert caption: {e}")
                    continue
            
            return jsonify({
                "ok": True,
                "count": success_count,
                "message": f"Successfully uploaded {success_count} captions"
            }), 200
            
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": f"Failed to parse CSV: {str(e)}"
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error uploading CSV: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@captions.route('/api/captions/reset', methods=['POST'])
def reset_all_captions():
    """Mark all captions as unused"""
    try:
        db = DatabaseManager()
        
        update_data = {
            "used": False,
            "used_at": None,
            "updated_at": datetime.now().isoformat()
        }
        
        response = db._make_request(
            'PATCH',
            f"{db.supabase_url}/rest/v1/captions",
            json=update_data
        )
        
        if response.status_code == 204:
            return jsonify({
                "ok": True,
                "message": "All captions marked as unused"
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to reset captions"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error resetting captions: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
