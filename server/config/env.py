#!/usr/bin/env python3
"""
Environment Configuration
Centralized config validation for Meta OAuth
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class MetaOAuthConfig:
    app_id: str | None
    app_secret: str | None
    redirect_uri: str | None

    @property
    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_secret and self.redirect_uri)

def load_meta_oauth_config() -> MetaOAuthConfig:
    """Load Meta OAuth configuration from environment variables"""
    return MetaOAuthConfig(
        app_id=os.environ.get("META_APP_ID"),
        app_secret=os.environ.get("META_APP_SECRET"),
        redirect_uri=os.environ.get("OAUTH_REDIRECT_URI"),
    )

def missing_oauth_vars(cfg: MetaOAuthConfig) -> List[str]:
    """Get list of missing OAuth environment variables"""
    missing = []
    if not cfg.app_id: 
        missing.append("META_APP_ID")
    if not cfg.app_secret: 
        missing.append("META_APP_SECRET")
    if not cfg.redirect_uri: 
        missing.append("OAUTH_REDIRECT_URI")
    return missing
