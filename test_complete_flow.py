#!/usr/bin/env python3
"""
Test complete captions flow
"""

import requests
import json

def test_complete_captions_flow():
    """Test the complete captions flow"""
    print("🚀 Testing Complete Captions Flow...")
    print("=" * 60)
    
    # Test 1: Get existing captions
    print("1️⃣ Testing GET captions...")
    try:
        response = requests.get("https://threads-bot-dashboard-3.onrender.com/api/captions")
        if response.status_code == 200:
            data = response.json()
            captions = data.get('captions', [])
            print(f"✅ GET captions successful: {len(captions)} captions found")
        else:
            print(f"❌ GET captions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET captions error: {e}")
        return False
    
    # Test 2: Add a new caption
    print("\n2️⃣ Testing ADD caption...")
    try:
        caption_data = {
            "text": "Test caption from complete flow",
            "category": "test",
            "tags": ["complete", "flow", "test"]
        }
        
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ ADD caption successful")
        else:
            print(f"❌ ADD caption failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ADD caption error: {e}")
        return False
    
    # Test 3: Verify the new caption was added
    print("\n3️⃣ Testing GET captions again to verify...")
    try:
        response = requests.get("https://threads-bot-dashboard-3.onrender.com/api/captions")
        if response.status_code == 200:
            data = response.json()
            captions = data.get('captions', [])
            print(f"✅ GET captions successful: {len(captions)} captions found")
            
            # Check if our new caption is there
            new_caption = next((c for c in captions if "Test caption from complete flow" in c.get('text', '')), None)
            if new_caption:
                print("✅ New caption found in database")
                return True
            else:
                print("⚠️ New caption not found in database")
                return False
        else:
            print(f"❌ GET captions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET captions error: {e}")
        return False

def main():
    """Run complete flow test"""
    success = test_complete_captions_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Complete captions flow is working perfectly!")
        print("\n💡 Summary:")
        print("✅ Backend is fully functional")
        print("✅ Captions can be fetched")
        print("✅ Captions can be created")
        print("✅ Database integration is working")
        print("\n📝 Next steps:")
        print("1. Disable any remaining Vercel protection settings")
        print("2. Test the frontend in your browser")
        print("3. The frontend should work by calling the backend directly")
    else:
        print("❌ Complete captions flow has issues")
        print("Check the backend deployment and configuration")

if __name__ == "__main__":
    main()
