import os
from flask import Blueprint, jsonify
from config.env import load_meta_oauth_config, missing_oauth_vars

bp = Blueprint("config_status", __name__, url_prefix="/config")

@bp.get("/status")
def status():
    cfg = load_meta_oauth_config()
    missing = missing_oauth_vars(cfg)
    
    # Get current scopes from Meta OAuth service
    try:
        from services.meta_oauth import MetaOAuthService
        oauth_service = MetaOAuthService()
        current_scopes = oauth_service.scopes
    except Exception:
        current_scopes = ['threads_business_basic']  # Default scope
    
    # Check if publishing is enabled
    publish_enabled = os.getenv('META_THREADS_PUBLISH_ENABLED', 'false').lower() == 'true'
    
    return jsonify({
        "meta_oauth_configured": cfg.is_configured,
        "missing": missing,  # safe: only names
        "oauthConfigured": cfg.is_configured,  # For frontend compatibility
        "scopes": current_scopes,
        "publishEnabled": publish_enabled
    })
