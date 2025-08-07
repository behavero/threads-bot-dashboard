#!/usr/bin/env python3
"""
Test Pillow installation and functionality
"""

def test_pillow_installation():
    """Test if Pillow is properly installed"""
    print("🧪 Testing Pillow installation...")
    
    try:
        from PIL import Image
        print(f"✅ Pillow installed successfully")
        print(f"📦 Version: {Image.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Pillow not installed: {e}")
        print("💡 Install with: pip install Pillow>=8.1.1")
        return False

def test_image_processing():
    """Test basic image processing functionality"""
    print("\n🧪 Testing image processing...")
    
    try:
        from PIL import Image
        import io
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Test saving to bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        print("✅ Image processing test passed")
        print(f"📏 Test image size: {test_image.size}")
        print(f"💾 Bytes generated: {len(img_byte_arr.getvalue())}")
        return True
        
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        return False

def test_instagrapi_compatibility():
    """Test if Pillow works with instagrapi"""
    print("\n🧪 Testing instagrapi compatibility...")
    
    try:
        from instagrapi import Client
        print("✅ instagrapi imported successfully")
        
        # Test if we can create a client (this will test PIL dependency)
        client = Client()
        print("✅ Client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ instagrapi compatibility test failed: {e}")
        return False

def main():
    """Run all Pillow tests"""
    print("🧪 Pillow Installation and Compatibility Tests")
    print("=" * 50)
    
    tests = [
        ("Pillow Installation", test_pillow_installation),
        ("Image Processing", test_image_processing),
        ("instagrapi Compatibility", test_instagrapi_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print("📊 PILLOW TEST RESULTS")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All Pillow tests passed!")
        print("✅ Image processing is ready for Threads bot")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("❌ Image processing may not work properly")

if __name__ == "__main__":
    main()
