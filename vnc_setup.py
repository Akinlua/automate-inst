#!/usr/bin/env python3
"""
Selenium Driverless Setup for Remote Chrome Browser Access
This module sets up a headless Chrome browser using Selenium WebDriver
for automated Instagram interaction with anti-detection measures and proxy support.
"""

import os
import sys
import time
import logging
import subprocess
import signal
import psutil
import threading
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("selenium_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("selenium_setup")

PROXY_SERVER = "http://ng.decodo.com:42032"

class SeleniumBrowserManager:
    def __init__(self, proxy_server: Optional[str] = None):
        self.proxy_server = None
        self.driver = None
        self.profile_path = None
        
    def set_proxy(self, proxy_server: str):
        """Set proxy server for Chrome"""
        self.proxy_server = proxy_server
        logger.info(f"Proxy server set to: {proxy_server}")
        
    def check_system_compatibility(self) -> bool:
        """Check if the system supports Chrome and Selenium"""
        try:
            # Check for Chrome installation
            chrome_executables = ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']
            chrome_found = False
            
            for executable in chrome_executables:
                try:
                    result = subprocess.run([executable, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"Found Chrome: {executable} - {result.stdout.strip()}")
                        chrome_found = True
                        break
                except FileNotFoundError:
                    continue
                    
            if not chrome_found:
                logger.error("Chrome browser not found")
                return False
                
            return True
        except Exception as e:
            logger.error(f"System compatibility check failed: {e}")
            return False
            
    def install_dependencies(self) -> bool:
        """Install Chrome and Selenium dependencies"""
        try:
            logger.info("Installing Chrome and Selenium dependencies...")
            
            # Update package list
            subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
            
            # Install Chrome and dependencies
            packages = [
                'wget',
                'curl',
                'unzip',
                'libnss3',
                'libatk-bridge2.0-0',
                'libdrm2',
                'libxcomposite1',
                'libxdamage1',
                'libxrandr2',
                'libgbm1',
                'libxss1',
                'libasound2'
            ]
            
            # Install packages
            subprocess.run(['apt-get', 'install', '-y'] + packages, check=True, capture_output=True)
            
            # Install Chrome if not present
            self._install_chrome()
            
            # Install ChromeDriver
            self._install_chromedriver()
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing dependencies: {e}")
            return False
    
    def _install_chrome(self):
        """Install Google Chrome"""
        try:
            logger.info("Installing Google Chrome...")
            
            # Download Chrome
            subprocess.run([
                'wget', '-q', '-O', '/tmp/google-chrome.deb',
                'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
            ], check=True)
            
            # Install Chrome
            subprocess.run(['dpkg', '-i', '/tmp/google-chrome.deb'], capture_output=True)
            subprocess.run(['apt-get', 'install', '-f', '-y'], capture_output=True)
            
            # Clean up
            os.remove('/tmp/google-chrome.deb')
            
            logger.info("Google Chrome installed successfully")
            
        except Exception as e:
            logger.warning(f"Chrome installation had issues: {e}")
            
    def _install_chromedriver(self):
        """Install ChromeDriver"""
        try:
            logger.info("Installing ChromeDriver...")
            
            # Get Chrome version
            chrome_version = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            version = chrome_version.stdout.split()[2].split('.')[0]
            
            # Download ChromeDriver
            subprocess.run([
                'wget', '-q', '-O', '/tmp/chromedriver.zip',
                f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}/chromedriver_linux64.zip'
            ], check=True)
            
            # Extract and install
            subprocess.run(['unzip', '-o', '/tmp/chromedriver.zip', '-d', '/tmp/'], check=True)
            subprocess.run(['mv', '/tmp/chromedriver', '/usr/local/bin/'], check=True)
            subprocess.run(['chmod', '+x', '/usr/local/bin/chromedriver'], check=True)
            
            # Clean up
            os.remove('/tmp/chromedriver.zip')
            
            logger.info("ChromeDriver installed successfully")
            
        except Exception as e:
            logger.warning(f"ChromeDriver installation had issues: {e}")
            
    def setup_chrome_profile(self, profile_path: str):
        """Setup Chrome profile with minimal configuration"""
        try:
            self.profile_path = profile_path
            
            # Create profile directory
            os.makedirs(profile_path, exist_ok=True)
            
            # Create downloads directory
            download_dir = os.path.abspath(os.path.join(os.path.dirname(profile_path), "downloads"))
            os.makedirs(download_dir, exist_ok=True)
            
            logger.info(f"Chrome profile setup at: {profile_path}")
            logger.info(f"Downloads directory: {download_dir}")
            
            return download_dir
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome profile: {e}")
            return None
            
    def create_chrome_driver(self, profile_path: str) -> bool:
        """Create Chrome WebDriver with minimal flags"""
        try:
            logger.info("Creating Chrome WebDriver with driverless configuration...")
            
            # Setup profile and downloads
            download_dir = self.setup_chrome_profile(profile_path)
            if not download_dir:
                return False
            
            # Chrome options with minimal necessary flags
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--log-level=3")  # Minimal logging
            
            # Use the custom profile directory (commented out as per original)
            # options.add_argument(f"--user-data-dir={profile_path}")
            
            # Add proxy if configured
            if self.proxy_server:
                if self.proxy_server.startswith('socks'):
                    options.add_argument(f'--proxy-server={self.proxy_server}')
                elif self.proxy_server.startswith('http'):
                    options.add_argument(f'--proxy-server={self.proxy_server}')
                else:
                    options.add_argument(f'--proxy-server=http://{self.proxy_server}')
                logger.info(f"Using proxy: {self.proxy_server}")
            
            # Set download preferences
            prefs = {
                "download.default_directory": download_dir.replace("\\", "/"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "plugins.always_open_pdf_externally": True,
                "browser.download.folderList": 2,
                "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,text/plain,text/html",
                "browser.download.manager.showWhenStarting": False
            }
            options.add_experimental_option("prefs", prefs)
            
            # Create WebDriver
            service = Service()  # Use default ChromeDriver path
            self.driver = webdriver.Chrome(service=service, options=options)
            
            logger.info("Chrome WebDriver created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Chrome WebDriver: {e}")
            return False
            
    def navigate_to_instagram(self) -> bool:
        """Navigate to Instagram login page"""
        try:
            if not self.driver:
                logger.error("WebDriver not initialized")
                return False
                
            logger.info("Navigating to Instagram...")
            self.driver.get("https://www.instagram.com")
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            logger.info(f"Successfully navigated to Instagram. Current URL: {self.driver.current_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get current browser status"""
        status = {
            'driver_running': False,
            'current_url': None,
            'page_title': None,
            'proxy_enabled': bool(self.proxy_server),
            'proxy_server': self.proxy_server,
            'profile_path': self.profile_path
        }
        
        try:
            if self.driver:
                status['driver_running'] = True
                status['current_url'] = self.driver.current_url
                status['page_title'] = self.driver.title
        except Exception as e:
            logger.warning(f"Error checking driver status: {e}")
            
        return status
        
    def get_access_info(self) -> Dict[str, Any]:
        """Get browser access information"""
        return {
            'type': 'selenium_headless',
            'proxy_server': self.proxy_server,
            'profile_path': self.profile_path,
            'status': self.get_status(),
            'message': 'Headless Chrome browser running with Selenium'
        }
        
    def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            
    def restart_browser(self, profile_path: str) -> bool:
        """Restart browser with fresh session"""
        try:
            logger.info("Restarting browser with fresh session...")
            
            # Close current browser
            self.close_browser()
            
            # Wait a moment
            time.sleep(2)
            
            # Create new driver
            return self.create_chrome_driver(profile_path)
            
        except Exception as e:
            logger.error(f"Failed to restart browser: {e}")
            return False
            
    def setup_and_start(self, profile_path: str) -> Dict[str, Any]:
        """Complete browser setup and start process"""
        try:
            logger.info("Starting Selenium browser setup...")
            
            # Check system compatibility
            if not self.check_system_compatibility():
                return {
                    'success': False,
                    'error': 'System not compatible with Chrome/Selenium'
                }
                
            # Install dependencies if needed
            try:
                # Try to create driver first, install dependencies if it fails
                if not self.create_chrome_driver(profile_path):
                    logger.info("Installing dependencies...")
                    if not self.install_dependencies():
                        return {
                            'success': False,
                            'error': 'Failed to install dependencies'
                        }
                    
                    # Try again after installing dependencies
                    if not self.create_chrome_driver(profile_path):
                        return {
                            'success': False,
                            'error': 'Failed to create Chrome WebDriver after installing dependencies'
                        }
            except Exception as e:
                logger.error(f"Driver creation failed: {e}")
                return {
                    'success': False,
                    'error': f'Failed to create WebDriver: {str(e)}'
                }
                
            # Navigate to Instagram
            if not self.navigate_to_instagram():
                return {
                    'success': False,
                    'error': 'Failed to navigate to Instagram'
                }
                
            return {
                'success': True,
                'access_info': self.get_access_info(),
                'message': 'Selenium headless browser started successfully'
            }
            
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return {
                'success': False,
                'error': f'Browser setup failed: {str(e)}'
            }

# Global browser manager instance
browser_manager = SeleniumBrowserManager()

def start_browser_session(profile_path: str, proxy_server: Optional[str] = None) -> Dict[str, Any]:
    """Start browser session with Chrome for automation"""
    global browser_manager
    if proxy_server:
        browser_manager.set_proxy(proxy_server)
    return browser_manager.setup_and_start(profile_path)
    
def get_browser_status() -> Dict[str, Any]:
    """Get current browser status"""
    return browser_manager.get_status()
    
def get_browser_access_info() -> Dict[str, Any]:
    """Get browser access information"""
    return browser_manager.get_access_info()
    
def stop_browser_session():
    """Stop browser session"""
    browser_manager.close_browser()

def restart_browser_fresh_session(profile_path: str) -> bool:
    """Restart browser with fresh session"""
    return browser_manager.restart_browser(profile_path)

def set_browser_proxy(proxy_server: str):
    """Set proxy server for browser sessions"""
    browser_manager.set_proxy(proxy_server)

def get_driver():
    """Get the current WebDriver instance"""
    return browser_manager.driver

if __name__ == "__main__":
    # Test browser setup
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    result = start_browser_session(profile_path)
    print(f"Browser setup result: {result}") 