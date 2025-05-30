#!/usr/bin/env python3
"""
Test script for Instagram Auto Poster (Selenium Version)
Verifies installation and configuration
"""

import os
import sys
import platform
from pathlib import Path

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'selenium',
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
    
    # Check optional variables
    optional_vars = ['OPENAI_API_KEY', 'CONTENT_DIR', 'POST_HOUR', 'POST_MINUTE', 'USE_CHATGPT']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}")
        else:
            print(f"  ⚠️  {var} (not set)")
    
    # Check Chrome profile settings
    chrome_vars = ['CHROME_PROFILE_PATH', 'CHROME_USER_DATA_DIR', 'CHROME_PROFILE_NAME']
    chrome_configured = False
    for var in chrome_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}")
            chrome_configured = True
        else:
            print(f"  ⚠️  {var} (not set)")
    
    if not chrome_configured:
        print("⚠️  No Chrome profile settings found. Run setup_chrome.py first!")
    
    print("✅ Configuration file exists!")
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

def test_chrome_setup():
    """Test Chrome and ChromeDriver setup"""
    print("\n🔍 Testing Chrome setup...")
    
    try:
        import subprocess
        
        # Check Chrome installation
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"  ✅ Chrome: {result.stdout.strip()}")
            else:
                print("  ❌ Chrome not found")
                return False
        
        # Check ChromeDriver
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  ✅ ChromeDriver: {result.stdout.strip()}")
        else:
            print("  ❌ ChromeDriver not found")
            print("  💡 Install with: brew install chromedriver")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Chrome setup test failed: {e}")
        return False

def test_selenium_connection():
    """Test Selenium Chrome connection"""
    print("\n🔍 Testing Selenium connection...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        print("  🔐 Testing basic Chrome connection...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"  ✅ Selenium connection successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"  ❌ Selenium connection failed: {e}")
        print("  💡 Make sure ChromeDriver is installed and in PATH")
        return False

def test_chrome_profile():
    """Test Chrome profile setup"""
    print("\n🔍 Testing Chrome profile...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    chrome_profile_path = os.getenv('CHROME_PROFILE_PATH')
    chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
    chrome_profile_name = os.getenv('CHROME_PROFILE_NAME')
    
    if chrome_profile_path and os.path.exists(chrome_profile_path):
        print(f"  ✅ V1 Chrome profile found: {chrome_profile_path}")
        return True
    elif chrome_user_data_dir and chrome_profile_name:
        profile_dir = os.path.join(chrome_user_data_dir, chrome_profile_name)
        if os.path.exists(profile_dir):
            print(f"  ✅ V2 Chrome profile found: {profile_dir}")
            return True
        else:
            print(f"  ⚠️  V2 Chrome profile directory not found: {profile_dir}")
            print("  💡 Run setup_chrome.py to create the profile")
            return False
    else:
        print("  ❌ No Chrome profile configured")
        print("  💡 Run setup_chrome.py to set up Chrome profile")
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
    print("🧪 Instagram Auto Poster - System Test (Selenium Version)")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration", test_configuration),
        ("Content Structure", test_content_structure),
        ("Chrome Setup", test_chrome_setup),
        ("Selenium Connection", test_selenium_connection),
        ("Chrome Profile", test_chrome_profile),
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
    print("\n" + "=" * 60)
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
        print("  1. Make sure you've run setup_chrome.py and logged into Instagram")
        print("  2. Add your content to the monthly folders")
        print("  3. Test posting: python instagram_poster.py post-now")
        print("  4. Start scheduler: python instagram_poster.py schedule")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before using the poster.")
        
        # Specific guidance based on failed tests
        failed_tests = [name for name, result in results if not result]
        if "Chrome Profile" in failed_tests:
            print("\n💡 Chrome Profile Issue:")
            print("  Run: python setup_chrome.py")
            print("  Then log into Instagram manually and keep the browser open")

if __name__ == "__main__":
    main() 