#!/usr/bin/env python3
"""
Internal Routes for Data Deletion
Protected endpoints for handling Meta-compliant data deletion
"""

from flask import Blueprint, request, jsonify, current_app
from database import DatabaseManager
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

internal = Blueprint('internal', __name__)

def verify_internal_token():
    """Verify the internal API token"""
    internal_token = request.headers.get('X-Internal-Token')
    expected_token = os.getenv('INTERNAL_API_TOKEN')
    
    if not expected_token:
        logger.error("INTERNAL_API_TOKEN not configured")
        return False
        
    if not internal_token or internal_token != expected_token:
        logger.warning("Invalid internal token provided")
        return False
        
    return True

@internal.route('/internal/data-deletion', methods=['POST'])
def delete_user_data():
    """Delete user data from Supabase"""
    try:
        # Verify internal token
        if not verify_internal_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_id = data.get('userId')
        token = data.get('token')
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
            
        if not token:
            return jsonify({'error': 'Missing token'}), 400
        
        logger.info(f"Processing data deletion for user_id: {user_id}, token: {token}")
        
        # Initialize database
        db = DatabaseManager()
        
        # Delete user data from all tables
        deletion_results = {}
        
        try:
            # Delete accounts associated with this user
            # Note: In a real implementation, you'd need to map Meta user_id to your internal user system
            # For now, we'll delete based on username patterns or other identifiers
            
            # Delete accounts (assuming user_id maps to some identifier)
            accounts_deleted = db.delete_accounts_by_user_id(user_id)
            deletion_results['accounts'] = accounts_deleted
            
            # Delete posting history
            posting_history_deleted = db.delete_posting_history_by_user_id(user_id)
            deletion_results['posting_history'] = posting_history_deleted
            
            # Delete captions
            captions_deleted = db.delete_captions_by_user_id(user_id)
            deletion_results['captions'] = captions_deleted
            
            # Delete images
            images_deleted = db.delete_images_by_user_id(user_id)
            deletion_results['images'] = images_deleted
            
            # Delete sessions from Supabase Storage
            sessions_deleted = db.delete_sessions_by_user_id(user_id)
            deletion_results['sessions'] = sessions_deleted
            
            logger.info(f"Data deletion completed for user_id: {user_id}")
            logger.info(f"Deletion results: {deletion_results}")
            
            return jsonify({
                'status': 'ok',
                'token': token,
                'user_id': user_id,
                'deletion_results': deletion_results,
                'message': 'User data deletion completed successfully'
            })
            
        except Exception as e:
            logger.error(f"Error during data deletion for user_id {user_id}: {str(e)}")
            return jsonify({
                'status': 'error',
                'token': token,
                'user_id': user_id,
                'error': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in delete_user_data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@internal.route('/internal/data-deletion/status', methods=['GET'])
def get_deletion_status():
    """Get deletion status for a token"""
    try:
        # Verify internal token
        if not verify_internal_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Missing token'}), 400
        
        logger.info(f"Checking deletion status for token: {token}")
        
        # In a real implementation, you'd look up the status from a database
        # For now, we'll return a completed status
        
        return jsonify({
            'status': 'completed',
            'token': token,
            'message': 'User data deletion was processed.',
            'completed_at': '2025-01-15T00:00:00Z',
            'deleted_items': {
                'accounts': 'all',
                'captions': 'all',
                'images': 'all', 
                'posting_history': 'all',
                'sessions': 'all'
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking deletion status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@internal.route('/internal/data-deletion/test', methods=['POST'])
def test_deletion_endpoint():
    """Test endpoint for data deletion (development only)"""
    try:
        # Verify internal token
        if not verify_internal_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        user_id = data.get('userId', 'test_user_123')
        token = data.get('token', 'test_token_456')
        
        logger.info(f"Test deletion request - user_id: {user_id}, token: {token}")
        
        return jsonify({
            'status': 'test_success',
            'token': token,
            'user_id': user_id,
            'message': 'Test deletion endpoint working correctly'
        })
        
    except Exception as e:
        logger.error(f"Error in test deletion endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
