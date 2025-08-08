from flask import Blueprint, jsonify
from config.env import load_meta_oauth_config, missing_oauth_vars

bp = Blueprint("config_status", __name__, url_prefix="/config")

@bp.get("/status")
def status():
    cfg = load_meta_oauth_config()
    missing = missing_oauth_vars(cfg)
    return jsonify({
        "meta_oauth_configured": cfg.is_configured,
        "missing": missing,  # safe: only names
    })
