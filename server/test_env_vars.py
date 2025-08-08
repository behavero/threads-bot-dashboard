#!/usr/bin/env python3
"""
Environment Variables Test Script
Tests that all required environment variables are properly configured
"""

import os
import sys
from typing import Dict, List, Tuple

def check_env_vars() -> Tuple[bool, List[str]]:
    """Check all required environment variables"""
    
    # Backend environment variables (Render)
    backend_vars = {
        'SUPABASE_URL': 'Database connection URL',
        'SUPABASE_SERVICE_ROLE_KEY': 'Database service role key',
        'SUPABASE_ANON_KEY': 'Database anonymous key',
        'META_APP_ID': 'Meta app ID',
        'META_APP_SECRET': 'Meta app secret (should be rotated)',
        'OAUTH_REDIRECT_URI': 'OAuth redirect URI',
        'APP_BASE_URL': 'Frontend base URL',
        'BACKEND_BASE_URL': 'Backend base URL',
        'GRAPH_API_BASE_URL': 'Graph API base URL',
        'GRAPH_API_VERSION': 'Graph API version',
        'INTERNAL_API_TOKEN': 'Internal API token for webhooks',
    }
    
    # Frontend environment variables (Vercel)
    frontend_vars = {
        'NEXT_PUBLIC_BACKEND_URL': 'Backend URL for frontend',
        'NEXT_PUBLIC_META_APP_ID': 'Meta app ID for frontend',
        'NEXT_PUBLIC_OAUTH_REDIRECT_URI': 'OAuth redirect URI for frontend',
        'NEXT_PUBLIC_APP_BASE_URL': 'Frontend base URL',
    }
    
    missing_vars = []
    all_good = True
    
    print("🔍 Checking Backend Environment Variables (Render):")
    print("=" * 50)
    
    for var, description in backend_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: MISSING - {description}")
            missing_vars.append(var)
            all_good = False
    
    print("\n🔍 Checking Frontend Environment Variables (Vercel):")
    print("=" * 50)
    
    for var, description in frontend_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: MISSING - {description}")
            missing_vars.append(var)
            all_good = False
    
    return all_good, missing_vars

def check_security() -> bool:
    """Check for security issues"""
    print("\n🔒 Security Checks:")
    print("=" * 30)
    
    security_issues = []
    
    # Check for hardcoded secrets
    secret_vars = ['META_APP_SECRET', 'SUPABASE_SERVICE_ROLE_KEY']
    for var in secret_vars:
        value = os.getenv(var)
        if value and value.startswith('your_'):
            security_issues.append(f"⚠️  {var} appears to be a placeholder value")
    
    # Check for default values
    if os.getenv('META_APP_SECRET') == '50d1453dc80f9b6cc06c9e3f70c50109':
        security_issues.append("⚠️  META_APP_SECRET is using the default value - should be rotated")
    
    if security_issues:
        for issue in security_issues:
            print(issue)
        return False
    else:
        print("✅ No obvious security issues detected")
        return True

def main():
    """Main test function"""
    print("🚀 Environment Variables Test")
    print("=" * 40)
    
    # Check environment variables
    all_good, missing_vars = check_env_vars()
    
    # Check security
    security_ok = check_security()
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 20)
    
    if all_good and security_ok:
        print("✅ All environment variables are properly configured!")
        print("✅ No security issues detected!")
        print("\n🎉 Ready for deployment!")
        return 0
    else:
        print("❌ Issues found:")
        if missing_vars:
            print(f"   - Missing variables: {', '.join(missing_vars)}")
        if not security_ok:
            print("   - Security issues detected")
        
        print("\n🔧 Next steps:")
        print("   1. Set missing environment variables in your deployment platform")
        print("   2. Rotate any default/placeholder secrets")
        print("   3. Run this test again")
        return 1

if __name__ == "__main__":
    sys.exit(main())
