#!/usr/bin/env python3
"""
Test script for Instagram Auto Poster
Verifies installation and configuration
"""

import os
import sys
from pathlib import Path

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'instagrapi',
        'PIL',
        'dotenv',
        'schedule',
        'openai',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def test_configuration():
    """Test configuration file"""
    print("\n🔍 Testing configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run: python setup.py")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['INSTAGRAM_USERNAME', 'INSTAGRAM_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"  ❌ {var}")
        else:
            print(f"  ✅ {var}")
    
    # Optional variables
    optional_vars = ['OPENAI_API_KEY', 'CONTENT_DIR', 'POST_HOUR', 'POST_MINUTE', 'USE_CHATGPT']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} (optional)")
        else:
            print(f"  ⚠️  {var} (optional, not set)")
    
    if missing_vars:
        print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Configuration looks good!")
        return True

def test_content_structure():
    """Test content directory structure"""
    print("\n🔍 Testing content structure...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    content_dir = Path(os.getenv('CONTENT_DIR', 'content'))
    
    if not content_dir.exists():
        print(f"❌ Content directory '{content_dir}' not found")
        print("💡 Run: python instagram_poster.py create-sample")
        return False
    
    print(f"✅ Content directory '{content_dir}' exists")
    
    # Check for monthly folders
    monthly_folders = []
    for i in range(1, 13):
        month_dir = content_dir / str(i)
        if month_dir.exists():
            monthly_folders.append(i)
            
            # Check for content
            images = list(month_dir.glob('*.jpg')) + list(month_dir.glob('*.jpeg')) + \
                    list(month_dir.glob('*.png')) + list(month_dir.glob('*.webp'))
            texts = list(month_dir.glob('*.txt'))
            
            print(f"  📁 Month {i}: {len(images)} images, {len(texts)} texts")
    
    if monthly_folders:
        print(f"✅ Found {len(monthly_folders)} monthly folders")
        return True
    else:
        print("❌ No monthly folders found")
        print("💡 Run: python instagram_poster.py create-sample")
        return False

def test_instagram_connection():
    """Test Instagram connection (without posting)"""
    print("\n🔍 Testing Instagram connection...")
    
    try:
        from dotenv import load_dotenv
        from instagrapi import Client
        
        load_dotenv()
        
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            print("❌ Instagram credentials not configured")
            return False
        
        print("  🔐 Attempting login...")
        client = Client()
        client.delay_range = [1, 3]
        
        # Try to login
        client.login(username, password)
        client.set_proxy("http://user-spar5fi090-sessionduration-1440:t9tTW7a0_bheTly4mH@ng.decodo.com:42002")  
        print("  ✅ Login successful!")
        
        # Get basic account info
        user_info = client.user_info_by_username(username)
        print(f"  📊 Account: @{user_info.username} ({user_info.full_name})")
        print(f"  👥 Followers: {user_info.follower_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Login failed: {e}")
        print("  💡 Check your credentials and try logging in manually first")
        return False

def test_chatgpt_connection():
    """Test ChatGPT connection if enabled"""
    print("\n🔍 Testing ChatGPT connection...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    use_chatgpt = os.getenv('USE_CHATGPT', 'false').lower() == 'true'
    
    if not use_chatgpt:
        print("  ⚠️  ChatGPT disabled in configuration")
        return True
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("  ❌ OpenAI API key not configured")
        return False
    
    try:
        import openai
        openai.api_key = api_key
        
        # Test with a simple request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("  ✅ ChatGPT connection successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ ChatGPT connection failed: {e}")
        print("  💡 Check your OpenAI API key and billing status")
        return False

def main():
    """Run all tests"""
    print("🧪 Instagram Auto Poster - System Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("Content Structure", test_content_structure),
        ("Instagram Connection", test_instagram_connection),
        ("ChatGPT Connection", test_chatgpt_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your Instagram Auto Poster is ready to use.")
        print("\n📋 Next steps:")
        print("  1. Add your content to the monthly folders")
        print("  2. Test posting: python instagram_poster.py post-now")
        print("  3. Start scheduler: python instagram_poster.py schedule")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before using the poster.")

if __name__ == "__main__":
    main() 