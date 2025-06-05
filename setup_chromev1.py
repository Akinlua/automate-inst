#!/usr/bin/env python3
import os
import sys
import time
import logging
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import ssl
import urllib3
import undetected_chromedriver as uc
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

# Configuration - Use fixed profile path without timestamps
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver")
CUSTOM_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile_instagram")

class ChromeProfileSetup:
    def __init__(self):
        self.driver = None
        
    def _clean_existing_profile(self):
        """Remove existing profile completely and create fresh directory"""
        try:
            if os.path.exists(CUSTOM_PROFILE_PATH):
                logger.info(f"Removing existing Chrome profile: {CUSTOM_PROFILE_PATH}")
                # Force remove the directory and all contents
                shutil.rmtree(CUSTOM_PROFILE_PATH, ignore_errors=True)
                time.sleep(1)  # Give filesystem time to complete the operation
            
            # Create fresh profile directory
            os.makedirs(CUSTOM_PROFILE_PATH, exist_ok=True)
            logger.info(f"Created fresh Chrome profile directory: {CUSTOM_PROFILE_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to clean existing profile: {e}")
            # If we can't clean it, try to work with what we have
            os.makedirs(CUSTOM_PROFILE_PATH, exist_ok=True)
        
    def setup_chrome_with_custom_profile(self):
        """Setup Chrome driver with a custom profile directory"""
        chrome_options = Options()
        
        # Clean existing profile and create fresh one
        self._clean_existing_profile()
        
        # Use custom profile directory
        chrome_options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
        
        # Additional options for better stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)

        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,  # Disable safe browsing which can block downloads
            "plugins.always_open_pdf_externally": True,  # Auto-download PDFs
            "browser.download.folderList": 2,  # 2 means custom location
            "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,text/plain,text/html",
            "browser.download.manager.showWhenStarting": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # service = Service(CHROMEDRIVER_PATH)
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Create unverified SSL context
            ssl._create_default_https_context = ssl._create_unverified_context

            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')

            options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
            # options.add_argument("--profile-directory=Default")
            logger.info(f"Using Chrome profile: {CUSTOM_PROFILE_PATH}")

            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')

            self.driver = uc.Chrome(options=options)

            # self.driver = webdriver.Chrome(options=chrome_options)
            # self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver setup successful with custom profile")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def navigate_to_instagram(self):
        """Navigate to Instagram for manual login"""
        try:
            self.driver.get("https://www.instagram.com/")
            logger.info("Navigated to Instagram - please log in manually")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False
    
    def run_setup(self):
        """Run the Chrome profile setup"""
        logger.info("Starting Chrome Profile Setup for Instagram")
        logger.info("="*50)
        
        if not self.setup_chrome_with_custom_profile():
            logger.error("Failed to setup Chrome driver. Exiting...")
            return
            
        if not self.navigate_to_instagram():
            logger.error("Failed to navigate to Instagram. Exiting...")
            return
        
        logger.info("Chrome browser is now open at Instagram.com")
        logger.info("Please complete the following steps:")
        logger.info("1. Log in to your Instagram account")
        logger.info("2. Complete any two-factor authentication if required")
        logger.info("3. Make sure you see your Instagram home feed")
        logger.info("4. Keep the browser open - DO NOT close it")
        logger.info("")
        logger.info("The browser will stay open with 'detach' mode enabled.")
        logger.info("Your login session will be saved to the custom profile directory.")
        logger.info("")
        logger.info(f"Profile will be saved to: {CUSTOM_PROFILE_PATH}")
        logger.info("")
        logger.info("After logging in successfully, you can close this terminal.")
        logger.info("Then run test.py which will use your saved login session.")
        logger.info("="*50)
        
        # Wait for a long time to allow manual login
        try:
            logger.info("Waiting 30 minutes for you to complete the login process...")
            logger.info("You can close this terminal once you've successfully logged in.")
            time.sleep(1800)  # Wait 30 minutes
        except KeyboardInterrupt:
            logger.info("Setup interrupted by user. Profile should be saved if login was completed.")
        except Exception as e:
            logger.error(f"Error during wait: {e}")
        
        # Update .env file with profile path
        self.update_env_file()
        
    def update_env_file(self):
        """Update the .env file with the custom profile path"""
        try:
            # Read existing .env file
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Check if CHROME_PROFILE_PATH already exists
            profile_path_exists = False
            for i, line in enumerate(env_lines):
                if line.startswith('CHROME_PROFILE_PATH='):
                    env_lines[i] = f'CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}\n'
                    profile_path_exists = True
                    break
            
            # Add CHROME_PROFILE_PATH if it doesn't exist
            if not profile_path_exists:
                env_lines.append(f'CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}\n')
            
            # Write back to .env file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            logger.info(f"Updated .env file with CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to update .env file: {e}")
            logger.info(f"Please manually add this line to your .env file:")
            logger.info(f"CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}")

if __name__ == "__main__":
    setup = ChromeProfileSetup()
    setup.run_setup() 