#!/usr/bin/env python3
import os
import sys
import time
import logging
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chrome_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("chrome_setup")

# Load environment variables
load_dotenv()

# Configuration
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver")

def get_chrome_user_data_dir():
    """Get the default Chrome user data directory for the current OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    elif system == "Windows":
        return os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    else:  # Linux
        return os.path.expanduser("~/.config/google-chrome")

class ChromeProfileSetupV2:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.profile_name = "InstagramBot"
        self.chrome_user_data_dir = get_chrome_user_data_dir()
        
    def setup_chrome_with_new_profile(self):
        """Setup Chrome driver with a new profile using Chrome's built-in profile system"""
        chrome_options = Options()
        
        # Use Chrome's default user data directory with a new profile
        chrome_options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={self.profile_name}")
        
        # Essential options for automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Disable various Chrome features that might cause issues
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Preferences to avoid popups and notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.geolocation": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            logger.info(f"Chrome driver setup successful with profile: {self.profile_name}")
            
            # Wait for Chrome to fully initialize the new profile
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def navigate_to_instagram(self):
        """Navigate to Instagram for manual login"""
        try:
            self.driver.get("https://www.instagram.com/")
            logger.info("Navigated to Instagram - please log in manually")
            
            # Wait for page to load
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False
    
    def run_setup(self):
        """Run the Chrome profile setup"""
        logger.info("Starting Chrome Profile Setup for Instagram (Version 2)")
        logger.info("="*60)
        logger.info(f"Using Chrome profile: {self.profile_name}")
        logger.info(f"Chrome user data directory: {self.chrome_user_data_dir}")
        logger.info("="*60)
        
        if not self.setup_chrome_with_new_profile():
            logger.error("Failed to setup Chrome driver. Exiting...")
            return
            
        if not self.navigate_to_instagram():
            logger.error("Failed to navigate to Instagram. Exiting...")
            return
        
        logger.info("Chrome browser is now open at Instagram.com")
        logger.info("This setup uses Chrome's built-in profile system - no popups!")
        logger.info("")
        logger.info("Please complete the following steps:")
        logger.info("1. Log in to your Instagram account")
        logger.info("2. Complete any two-factor authentication if required")
        logger.info("3. Make sure you see your Instagram home feed")
        logger.info("4. Keep the browser open - DO NOT close it")
        logger.info("")
        logger.info("The browser will stay open with 'detach' mode enabled.")
        logger.info(f"Your login session will be saved to Chrome profile: {self.profile_name}")
        logger.info("")
        logger.info("After logging in successfully, you can close this terminal.")
        logger.info("Then run test_v2.py which will use your saved login session.")
        logger.info("="*60)
        
        # Wait for a long time to allow manual login
        try:
            logger.info("Waiting 30 minutes for you to complete the login process...")
            logger.info("You can close this terminal once you've successfully logged in.")
            time.sleep(1800)  # Wait 30 minutes
        except KeyboardInterrupt:
            logger.info("Setup interrupted by user. Profile should be saved if login was completed.")
        except Exception as e:
            logger.error(f"Error during wait: {e}")
        
        # Update .env file with profile info
        self.update_env_file()
        
    def update_env_file(self):
        """Update the .env file with the profile information"""
        try:
            # Read existing .env file
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add Chrome profile settings
            settings_to_update = {
                'CHROME_USER_DATA_DIR': self.chrome_user_data_dir,
                'CHROME_PROFILE_NAME': self.profile_name
            }
            
            for setting, value in settings_to_update.items():
                setting_exists = False
                for i, line in enumerate(env_lines):
                    if line.startswith(f'{setting}='):
                        env_lines[i] = f'{setting}={value}\n'
                        setting_exists = True
                        break
                
                if not setting_exists:
                    env_lines.append(f'{setting}={value}\n')
            
            # Write back to .env file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            logger.info(f"Updated .env file with Chrome profile settings")
            logger.info(f"CHROME_USER_DATA_DIR={self.chrome_user_data_dir}")
            logger.info(f"CHROME_PROFILE_NAME={self.profile_name}")
            
        except Exception as e:
            logger.error(f"Failed to update .env file: {e}")
            logger.info(f"Please manually add these lines to your .env file:")
            logger.info(f"CHROME_USER_DATA_DIR={self.chrome_user_data_dir}")
            logger.info(f"CHROME_PROFILE_NAME={self.profile_name}")

if __name__ == "__main__":
    setup = ChromeProfileSetupV2()
    setup.run_setup() 