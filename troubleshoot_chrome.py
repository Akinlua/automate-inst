#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_chrome_installation():
    """Check if Chrome is installed and get version"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Chrome found: {result.stdout.strip()}")
                return True
            else:
                print("❌ Chrome not found in /Applications/")
                return False
        else:
            result = subprocess.run(["google-chrome", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Chrome found: {result.stdout.strip()}")
                return True
            else:
                print("❌ Chrome not found")
                return False
    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is available and get version"""
    try:
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ ChromeDriver found: {result.stdout.strip()}")
            return True
        else:
            print("❌ ChromeDriver not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking ChromeDriver: {e}")
        return False

def kill_chrome_processes():
    """Kill any existing Chrome processes"""
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
        print("✅ Killed existing Chrome/ChromeDriver processes")
    except Exception as e:
        print(f"⚠️  Could not kill processes: {e}")

def test_basic_chrome():
    """Test basic Chrome startup"""
    print("\n🧪 Testing basic Chrome startup...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # Use headless for testing
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"✅ Basic Chrome test successful - Page title: {title}")
        return True
    except Exception as e:
        print(f"❌ Basic Chrome test failed: {e}")
        return False

def test_profile_chrome():
    """Test Chrome with profile directory"""
    print("\n🧪 Testing Chrome with profile...")
    
    chrome_user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    profile_name = "InstagramBot"
    
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_name}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # Use headless for testing
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"✅ Profile Chrome test successful - Page title: {title}")
        return True
    except Exception as e:
        print(f"❌ Profile Chrome test failed: {e}")
        return False

def main():
    print("🔍 Chrome/ChromeDriver Troubleshooting Tool")
    print("=" * 50)
    
    # Step 1: Kill existing processes
    print("\n1. Cleaning up existing processes...")
    kill_chrome_processes()
    
    # Step 2: Check Chrome installation
    print("\n2. Checking Chrome installation...")
    chrome_ok = check_chrome_installation()
    
    # Step 3: Check ChromeDriver
    print("\n3. Checking ChromeDriver...")
    chromedriver_ok = check_chromedriver()
    
    if not chrome_ok:
        print("\n❌ Chrome is not properly installed!")
        print("Please install Google Chrome from: https://www.google.com/chrome/")
        return
    
    if not chromedriver_ok:
        print("\n❌ ChromeDriver is not in PATH!")
        print("Please install ChromeDriver:")
        print("  brew install chromedriver  # On macOS with Homebrew")
        print("  Or download from: https://chromedriver.chromium.org/")
        return
    
    # Step 4: Test basic Chrome
    basic_ok = test_basic_chrome()
    
    # Step 5: Test with profile
    profile_ok = test_profile_chrome()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"Chrome Installation: {'✅' if chrome_ok else '❌'}")
    print(f"ChromeDriver: {'✅' if chromedriver_ok else '❌'}")
    print(f"Basic Chrome Test: {'✅' if basic_ok else '❌'}")
    print(f"Profile Chrome Test: {'✅' if profile_ok else '❌'}")
    
    if all([chrome_ok, chromedriver_ok, basic_ok, profile_ok]):
        print("\n🎉 All tests passed! Your setup should work.")
        print("Try running setup_chrome_v2.py again.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        
        if not basic_ok:
            print("\n💡 Suggestions:")
            print("- Make sure Chrome is not already running")
            print("- Try updating Chrome and ChromeDriver")
            print("- Check if antivirus is blocking Chrome")
        
        if not profile_ok:
            print("\n💡 Profile suggestions:")
            print("- Make sure Chrome user data directory exists")
            print("- Try deleting the InstagramBot profile folder")

if __name__ == "__main__":
    main() 


next document.querySelector("body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div > div > div > div._ap97 > div > div > div > div._ac7b._ac7d > div > div")