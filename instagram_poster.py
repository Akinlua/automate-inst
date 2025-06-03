#!/usr/bin/env python3
"""
Instagram Auto Poster
Automatically posts content from monthly folders to Instagram using Selenium
"""

import os
import sys
import time
import random
import logging
import schedule
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import base64
import ssl
import urllib3
import csv

# Third-party imports
from dotenv import load_dotenv
from PIL import Image
import openai

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_poster.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_chrome_user_data_dir():
    """Get the default Chrome user data directory for the current OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    elif system == "Windows":
        return os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    else:  # Linux
        return os.path.expanduser("~/.config/google-chrome")

class InstagramPoster:
    def __init__(self):
        """Initialize the Instagram poster with credentials and settings"""
        self.content_dir = Path(os.getenv('CONTENT_DIR', 'content'))
        self.use_chatgpt = os.getenv('USE_CHATGPT', 'false').lower() == 'true'
        
        # Chrome profile settings
        self.chrome_profile_path = os.getenv('CHROME_PROFILE_PATH')
        self.chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR') or get_chrome_user_data_dir()
        self.chrome_profile_name = os.getenv('CHROME_PROFILE_NAME', 'InstagramBot')
        
        # Selenium driver
        self.driver = None
        self.wait = None
        
        # Initialize OpenAI if enabled
        if self.use_chatgpt:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                logger.warning("OpenAI API key not found. ChatGPT enhancement disabled.")
                self.use_chatgpt = False
        
        # Track posted content to avoid duplicates
        self.posted_log_file = Path('posted_content.json')
        self.posted_content = self.load_posted_content()
        
        # Settings file for scheduler configuration
        self.settings_file = Path('scheduler_settings.json')
        self.settings = self.load_settings()
        
        # New file for image ordering
        self.image_order_file = Path('image_order.json')
        self.image_order = self.load_image_order()
        
        logger.info("Instagram Poster initialized successfully")
    
    def load_posted_content(self) -> Dict:
        """Load the log of previously posted content"""
        if self.posted_log_file.exists():
            try:
                with open(self.posted_log_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading posted content log: {e}")
        return {}
    
    def save_posted_content(self):
        """Save the log of posted content"""
        try:
            with open(self.posted_log_file, 'w') as f:
                json.dump(self.posted_content, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving posted content log: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            'enabled': True,
            'num_images': 1,
            'post_interval_hours': 4,
            'use_sequential_images': True,  # New setting for image selection order
            'chatgpt_enabled': False,
            'chatgpt_api_key': '',
            'instagram_username': '',
            'instagram_password': ''
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            except Exception as e:
                logger.warning(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save scheduler settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def update_setting(self, key: str, value):
        """Update a specific setting"""
        self.settings[key] = value
        self.save_settings()
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting"""
        return self.settings.get(key, default)
    
    def setup_chrome_driver(self):
        """Setup Chrome driver with saved profile"""
        chrome_options = Options()
        
        # Use the saved profile path (V1 compatibility) or Chrome's built-in profile system (V2)
        if self.chrome_profile_path and os.path.exists(self.chrome_profile_path):
            # V1 approach - custom profile directory
            chrome_options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
            chrome_options.add_argument("--profile-directory=Default")
            logger.info(f"Using V1 Chrome profile: {self.chrome_profile_path}")
        else:
            # V2 approach - Chrome's built-in profile system
            chrome_options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={self.chrome_profile_name}")
            logger.info(f"Using V2 Chrome profile: {self.chrome_profile_name}")
        
        # Essential options for automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Disable various Chrome features that might cause issues
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Preferences to avoid popups and notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Uncomment for headless mode
        # chrome_options.add_argument("--headless")

        # Essential anti-detection options
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        # chrome_options.add_argument('--disable-extensions')

        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        
        try:
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Create unverified SSL context
            ssl._create_default_https_context = ssl._create_unverified_context

            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')

            options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
            options.add_argument("--profile-directory=Default")
            logger.info(f"Using V1 Chrome profile: {self.chrome_profile_path}")

            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument("--headless")


            self.driver = uc.Chrome(version_main=136, options=options)
            # self.driver = webdriver.Chrome(options=chrome_options)
            # self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Chrome driver setup successful")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def navigate_to_instagram(self):
        """Navigate to Instagram (should already be logged in)"""
        try:
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)  # Wait for page to load
            
            # Check if we're logged in by looking for navigation elements
            try:
                # Wait for home page elements to load
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//a[@href='/']")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@aria-label, 'New post')]")),
                ))
                logger.info("Successfully navigated to Instagram and confirmed login status")
                return True
                
            except Exception as e:
                logger.error(f"Appears not logged in or page not loaded properly: {e}")
                logger.error("Please run setup_chrome.py first to set up the profile!")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False

    def click_new_post_icon(self):
        """Click on the + icon for new post"""
        try:
            # Use the specific XPath provided for the + icon
            new_post_icon = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div[7]/div/span/div/a/div/div[1]/div'
            )))
            new_post_icon.click()
            logger.info("Clicked new post icon (+)")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Could not find or click new post icon: {e}")
            # Fallback to more generic selector
            try:
                fallback_icon = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//div[@role='button']//svg[@aria-label='New post' or @aria-label='Create']/../.."
                )))
                fallback_icon.click()
                logger.info("Clicked new post icon (+ - fallback selector)")
                time.sleep(2)
                return True
            except Exception as e2:
                logger.error(f"Fallback selector also failed: {e2}")
                return False
    
    def click_post_button(self):
        """Click on the Post button"""
        try:
            # Use the specific XPath provided for the Post button
            post_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div[7]/div/span/div/div/div/div[1]/a[1]/div[1]/div/div/div[1]/div/div"
            )))
            post_button.click()
            logger.info("Clicked Post button")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Could not find or click Post button: {e}")
            # Fallback to text-based selector
            try:
                fallback_post = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(text(), 'Post')] | //div[contains(text(), 'Post')]"
                )))
                fallback_post.click()
                logger.info("Clicked Post button (fallback selector)")
                time.sleep(2)
                return True
            except Exception as e2:
                logger.error(f"Fallback Post button selector also failed: {e2}")
                return False
    
    def click_select_from_computer(self):
        """Click on Select from computer button"""
        try:
            # Use the specific XPath provided for select from computer
            select_computer = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[12]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button"
            )))
            select_computer.click()
            logger.info("Clicked Select from computer button")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Could not find or click Select from computer button: {e}")
            # Fallback to text-based selector
            try:
                fallback_select = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(text(), 'Select from computer')]"
                )))
                fallback_select.click()
                logger.info("Clicked Select from computer button (fallback selector)")
                time.sleep(2)
                return True
            except Exception as e2:
                logger.error(f"Fallback Select from computer selector also failed: {e2}")
                return False
    
    def upload_multiple_images(self, image_paths: List[Path]) -> bool:
        """Upload multiple images using JavaScript File API for Instagram carousel"""
        try:
            if not image_paths:
                logger.error("No image paths provided")
                return False
            
            logger.info(f"Uploading {len(image_paths)} images for carousel post")
            
            # Prepare files data
            files_data = []
            for image_path in image_paths:
                absolute_path = os.path.abspath(str(image_path))
                
                # Read file and encode to base64
                with open(absolute_path, 'rb') as file:
                    file_content = base64.b64encode(file.read()).decode()
                
                # Get filename and determine MIME type
                filename = os.path.basename(absolute_path)
                file_ext = os.path.splitext(filename)[1].lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.gif': 'image/gif'
                }.get(file_ext, 'image/jpeg')
                
                files_data.append({
                    'content': file_content,
                    'filename': filename,
                    'mime_type': mime_type
                })
            
            # JavaScript to create multiple files and upload
            script = f"""
            var input = document.querySelector('input[type="file"]');
            if (!input) {{
                throw new Error('File input not found');
            }}
            
            var dataTransfer = new DataTransfer();
            """
            
            # Add each file to the script
            for i, file_data in enumerate(files_data):
                script += f"""
            var file{i} = new File([Uint8Array.from(atob('{file_data["content"]}'), c => c.charCodeAt(0))], 
                                '{file_data["filename"]}', {{type: '{file_data["mime_type"]}'}});
            dataTransfer.items.add(file{i});
            """
            
            script += """
            input.files = dataTransfer.files;
            
            // Trigger change event
            input.dispatchEvent(new Event('change', {bubbles: true}));
            input.dispatchEvent(new Event('input', {bubbles: true}));
            
            return true;
            """
            
            # Execute the script
            result = self.driver.execute_script(script)
            time.sleep(5)
            
            # Wait for images to be processed
            try:
                # Wait for image processing interface
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//canvas")),  # Image canvas
                    EC.presence_of_element_located((By.XPATH, "//img[contains(@style, 'object-fit')]")),  # Image preview
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")),  # Next button
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'crop')]"))  # Crop interface
                ))
                logger.info(f"Successfully uploaded {len(image_paths)} images for carousel")
                time.sleep(3)  # Give it a moment to fully load
                return True
                
            except Exception as e:
                logger.error(f"Images didn't load properly after upload: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to upload multiple images: {e}")
            return False

    def upload_image(self, image_path):
        """Upload a single image using JavaScript File API"""
        try:
            # Convert single image to list and use multiple upload method
            if isinstance(image_path, (str, Path)):
                return self.upload_multiple_images([Path(image_path)])
            else:
                return self.upload_multiple_images(image_path)
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return False
    
    def click_next_button(self, step_name=""):
        """Click the Next button"""
        try:
            # Use the class selector for Next button
            next_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[contains(@class, 'x1i10hfl') and contains(text(), 'Next')]"
            )))
            next_button.click()
            logger.info(f"Clicked Next button {step_name}")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Could not find or click Next button {step_name}: {e}")
            # Fallback to text-based selector
            try:
                fallback_next = self.wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1lku1pv.x1a2a7pz.x6s0dn4.xjyslct.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x9f619.x1ypdohk.x1f6kntn.xwhw2v2.xl56j7k.x17ydfre.x2b8uid.xlyipyv.x87ps6o.x14atkfc.xcdnw81.x1i0vuye.xjbqb8w.xm3z3ea.x1x8b98j.x131883w.x16mih1h.x972fbf.xcfux6l.x1qhh985.xm0m39n.xt0psk2.xt7dq6l.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x1n5bzlp.x173jzuc.x1yc6y37"
                )))
                fallback_next.click()
                logger.info(f"Clicked Next button {step_name} (fallback selector)")
                time.sleep(3)
                return True
            except Exception as e2:
                logger.error(f"Fallback Next button selector also failed: {e2}")
                return False
    def click_next_button_2(self, step_name=""):
        """Click the Next button"""
        try:
            # Use the class selector for Next button
            next_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[contains(@class, 'x1i10hfl') and contains(text(), 'Next')]"
            )))
            next_button.click()
            logger.info(f"Clicked Next button {step_name}")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Could not find or click Next button {step_name}: {e}")
            # Fallback to text-based selector
            try:
                fallback_next = self.wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1lku1pv.x1a2a7pz.x6s0dn4.xjyslct.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x9f619.x1ypdohk.x1f6kntn.xwhw2v2.xl56j7k.x17ydfre.x2b8uid.xlyipyv.x87ps6o.x14atkfc.xcdnw81.x1i0vuye.xjbqb8w.xm3z3ea.x1x8b98j.x131883w.x16mih1h.x972fbf.xcfux6l.x1qhh985.xm0m39n.xt0psk2.xt7dq6l.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x1n5bzlp.x173jzuc.x1yc6y37"
                )))
                fallback_next.click()
                logger.info(f"Clicked Next button {step_name} (fallback selector)")
                time.sleep(3)
                return True
            except Exception as e2:
                logger.error(f"Fallback Next button selector also failed: {e2}")
                return False
    
    def add_caption(self, caption):
        """Add caption to the contenteditable div"""
        try:
            # Use class selector for caption div
            # caption_element = self.wait.until(EC.element_to_be_clickable((
            #     By.CSS_SELECTOR, "div.xw2csxc.x1odjw0f.x1n2onr6.x1hnll1o.xpqswwc.xl565be.x5dp1im.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1w2wdq1.xen30ot.x1swvt13.x1pi30zi.xh8yej3.x5n08af.notranslate"
            # )))
            
            # Click on the element to focus it
            # caption_element.click()
            # logger.info("Clicked on caption area")
            # time.sleep(1)

            # Use arguments to pass the caption safely (no string interpolation)
            script = """
                const editableDiv = document.querySelector('div.xw2csxc.x1odjw0f.x1n2onr6.x1hnll1o.xpqswwc.xl565be.x5dp1im.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1w2wdq1.xen30ot.x1swvt13.x1pi30zi.xh8yej3.x5n08af.notranslate[contenteditable="true"]');
                
                if (editableDiv) {
                    editableDiv.focus();
                    document.execCommand('insertText', false, arguments[0]);
                    return 'Caption inserted successfully (alternative method)';
                } else {
                    return 'Contenteditable div not found (alternative method)';
                }
            """
            
            result = self.driver.execute_script(script, caption)
            logger.info(f"JavaScript result: {result}")
            
            logger.info("Added caption using contenteditable approach")
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add caption using contenteditable approach: {e}")
            # Alternative approach using arguments to pass the caption safely
            try:
                logger.info("Trying alternative JavaScript approach...")
                
                # Properly escape the caption for JavaScript
                escaped_caption = caption.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                print(escaped_caption)
                # Use JavaScript to focus the contenteditable div and insert text
                script = f"""
                const editableDiv = document.querySelector('div.xw2csxc.x1odjw0f.x1n2onr6.x1hnll1o.xpqswwc.xl565be.x5dp1im.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1w2wdq1.xen30ot.x1swvt13.x1pi30zi.xh8yej3.x5n08af.notranslate[contenteditable="true"]');
                console.log('Found editable div:', editableDiv);
                
                if (editableDiv) {{
                    // Focus the div
                    editableDiv.focus();
                    
                    // Insert the caption text
                    document.execCommand('insertText', false, '{escaped_caption}');
                    
                    return 'Caption inserted successfully';
                }} else {{
                    return 'Contenteditable div not found';
                }}
                """
                
                # # Execute the script
                result = self.driver.execute_script(script)
                logger.info(f"JavaScript result (alternative): {result}")
                logger.info("Added caption using alternative JavaScript approach")
                time.sleep(2)
                return True
                
            except Exception as e2:
                logger.error(f"Alternative JavaScript approach also failed: {e2}")
                # Fallback to textarea selector
                try:
                    fallback_caption = self.wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//textarea[@aria-label='Write a caption...'] | //div[@aria-label='Write a caption...']"
                    )))
                    fallback_caption.click()
                    time.sleep(1)
                    fallback_caption.clear()
                    fallback_caption.send_keys(caption)
                    logger.info("Added caption to post (fallback selector)")
                    time.sleep(2)
                    return True
                except Exception as e3:
                    logger.error(f"Fallback caption selector also failed: {e3}")
                    return False
    
    def click_share_button(self):
        """Click the Share button"""
        try:
            # Use the specific XPath provided for Share button
            share_button = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1a2a7pz.x6s0dn4.xjyslct.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x9f619.x1ypdohk.x1f6kntn.xl56j7k.x17ydfre.x2b8uid.xlyipyv.x87ps6o.x14atkfc.x5c86q.x18br7mf.x1i0vuye.xl0gqc1.xr5sc7.xlal1re.x14jxsvd.xt0b8zv.xjbqb8w.xm3z3ea.x1x8b98j.x131883w.x16mih1h.x972fbf.xcfux6l.x1qhh985.xm0m39n.xt0psk2.xt7dq6l.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x1n5bzlp"
            )))
            share_button.click()
            logger.info("Clicked Share button - Post published!")
            time.sleep(30)  # Wait for post to process
            return True
        except Exception as e:
            logger.error(f"Could not find or click Share button: {e}")
            # Fallback to text-based selector
            try:
                fallback_share = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//div[contains(text(), 'Share')]"
                )))
                fallback_share.click()
                logger.info("Clicked Share button - Post published! (fallback selector)")
                time.sleep(30)
                return True
            except Exception as e2:
                logger.error(f"Fallback Share button selector also failed: {e2}")
                return False

    def get_monthly_folders(self) -> List[Path]:
        """Get all monthly folders sorted by number"""
        if not self.content_dir.exists():
            logger.error(f"Content directory {self.content_dir} does not exist")
            return []
        
        folders = []
        for item in self.content_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                folders.append(item)
        
        # Sort by month number
        folders.sort(key=lambda x: int(x.name))
        return folders
    
    def get_images_from_folder(self, folder: Path) -> List[Path]:
        """Get all image files from a folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = []
        
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in image_extensions:
                images.append(file)
        
        return sorted(images)
    
    def get_text_files_from_folder(self, folder: Path) -> List[Path]:
        """Get all text files from a folder"""
        text_files = []
        
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.txt':
                text_files.append(file)
        
        return sorted(text_files)
    
    def read_text_file(self, file_path: Path) -> str:
        """Read content from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def enhance_text_with_chatgpt(self, text: str) -> str:
        """Enhance text using ChatGPT"""
        if not self.use_chatgpt:
            return text
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert. Enhance the given text to make it more engaging for Instagram posts. Keep it authentic and add relevant hashtags. Keep the original message but make it more appealing."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            logger.info("Text enhanced with ChatGPT")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Error enhancing text with ChatGPT: {e}")
            return text
    
    def prepare_image(self, image_path: Path) -> Path:
        """Prepare image for Instagram (resize if needed)"""
        try:
            with Image.open(image_path) as img:
                # Instagram prefers square or 4:5 ratio
                width, height = img.size
                
                # If image is too large, resize it
                max_size = 1080
                if width > max_size or height > max_size:
                    if width > height:
                        new_width = max_size
                        new_height = int((height * max_size) / width)
                    else:
                        new_height = max_size
                        new_width = int((width * max_size) / height)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save resized image
                    temp_path = image_path.parent / f"resized_{image_path.name}"
                    img.save(temp_path, quality=95)
                    return temp_path
                
                return image_path
                
        except Exception as e:
            logger.error(f"Error preparing image {image_path}: {e}")
            return image_path
    
    def post_to_instagram(self, image_paths, caption: str) -> bool:
        """Post images with caption to Instagram using Selenium"""
        try:
            # Handle both single image and multiple images
            if isinstance(image_paths, (str, Path)):
                image_paths = [Path(image_paths)]
            elif not isinstance(image_paths, list):
                image_paths = [image_paths]
            
            # Prepare images
            prepared_images = []
            for image_path in image_paths:
                prepared_image = self.prepare_image(Path(image_path))
                prepared_images.append(prepared_image)
            
            logger.info(f"Posting {len(prepared_images)} images to Instagram")
            
            # Complete workflow to create and upload a post
            # Step 1: Click the + icon for new post
            if not self.click_new_post_icon():
                return False
            
            # Step 2: Click the Post button
            if not self.click_post_button():
                return False
            
            # Step 3: Click Select from computer
            # if not self.click_select_from_computer():
            #     return False
            
            # Step 4: Upload images (single or multiple)
            if not self.upload_multiple_images(prepared_images):
                return False
            
            # Step 5: Click Next button (first time)
            if not self.click_next_button("(crop/filter step)"):
                return False
            # time.sleep(10000)
            
            # Step 6: Click Next button (second time)
            if not self.click_next_button_2("(final step)"):
                return False
            
            # Step 7: Add caption
            if not self.add_caption(caption):
                return False
            
            # Step 8: Click Share button
            if not self.click_share_button():
                return False
            
            # Clean up temporary resized images if created
            for original, prepared in zip(image_paths, prepared_images):
                if prepared != original and prepared.exists():
                    prepared.unlink()
            
            logger.info(f"Successfully posted {len(prepared_images)} images to Instagram using Selenium")
            return True
            
        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            return False
    
    def get_csv_from_folder(self, folder: Path) -> Optional[Path]:
        """Get CSV file from a folder"""
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                return file
        return None
    
    def read_csv_captions(self, csv_path: Path) -> List[Tuple[str, str]]:
        """Read captions from CSV file with ID,caption format"""
        try:
            captions = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2 and row[1].strip():  # ID,caption format
                        captions.append((row[0].strip(), row[1].strip()))
                    elif row and len(row) == 1 and row[0].strip():  # Legacy caption-only format
                        # Convert to ID,caption format (use index as ID)
                        captions.append((str(len(captions) + 1), row[0].strip()))
            return captions
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_path}: {e}")
            return []
    
    def get_next_available_post(self, month: int) -> Optional[Tuple[str, str]]:
        """Get the next available post ID and caption for a month"""
        month_folder = self.content_dir / str(month)
        if not month_folder.exists():
            return None
        
        csv_file = self.get_csv_from_folder(month_folder)
        if not csv_file:
            logger.warning(f"No CSV file found in month {month}")
            return None
        
        captions = self.read_csv_captions(csv_file)
        if not captions:
            return None
        
        # Check which post IDs have been used
        month_key = f"month_{month}"
        posted_data = self.posted_content.get(month_key, {})
        used_post_ids = set(posted_data.get('used_posts', []))
        
        # Find next available post by ID (in order they appear in CSV)
        for post_id, caption in captions:
            if post_id not in used_post_ids:
                return post_id, caption
        
        logger.info(f"All posts for month {month} have been used")
        return None
    
    def select_random_images(self, month_folder, num_images=1):
        """Select random images from month folder that haven't been used, respecting the defined order"""
        # Get ordered list of images for this month
        month_num = int(month_folder.name)
        ordered_images = self.get_month_image_order(month_num)
        
        if not ordered_images:
            return []
        
        # Get used images for this month
        month_key = f"month_{month_num}"
        used_images = set(self.posted_content.get(month_key, {}).get('used_images', []))
        
        # Filter out used images, maintaining order
        available_images = [img for img in ordered_images if img not in used_images]
        
        if len(available_images) < num_images:
            raise ValueError(f"Not enough images available. Need {num_images}, but only {len(available_images)} unused images available.")
        
        # Take the first N images from the ordered list (or random selection)
        import random
        if self.settings.get('use_sequential_images', True):
            # Use sequential order
            selected_images = available_images[:num_images]
        else:
            # Use random selection
            selected_images = random.sample(available_images, num_images)
        
        # Convert to Path objects
        return [month_folder / img for img in selected_images]
    
    def mark_content_as_posted(self, month: int, post_id: str, image_names: List[str]):
        """Mark content as posted to avoid repetition"""
        month_key = f"month_{month}"
        
        if month_key not in self.posted_content:
            self.posted_content[month_key] = {
                'used_posts': [],
                'used_images': [],
                'post_history': []
            }
        
        # Mark post and images as used
        self.posted_content[month_key]['used_posts'].append(post_id)
        self.posted_content[month_key]['used_images'].extend(image_names)
        
        # Add to history
        self.posted_content[month_key]['post_history'].append({
            'posted_at': datetime.now().isoformat(),
            'post_id': post_id,
            'images': image_names
        })
        
        self.save_posted_content()
    
    def get_current_month_content_new(self, num_images=1):
        """
        Get content for the current month using the new CSV-based structure
        Returns (folder, images, caption, post_number) or None if no content available
        """
        import datetime
        current_month = datetime.datetime.now().month
        
        # Get next available post
        post_data = self.get_next_available_post(current_month)
        if not post_data:
            logger.info("No available posts for current month")
            return None
        
        post_id, caption = post_data
        
        # Get the month folder
        month_folder = self.content_dir / str(current_month)
        
        # Select images (in order, not random)
        images = self.select_random_images(month_folder, num_images)
        if not images:
            # Check if it's because of insufficient images
            all_images = self.get_images_from_folder(month_folder)
            month_key = f"month_{current_month}"
            posted_data = self.posted_content.get(month_key, {})
            used_images = set(posted_data.get('used_images', []))
            available_images = [img for img in all_images if img.name not in used_images]
            
            if len(available_images) > 0 and len(available_images) < num_images:
                error_msg = f"Insufficient unused images. Need: {num_images}, Available: {len(available_images)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info("No available images for current month")
            return None
        
        return (month_folder, images, caption, post_id)
    
    def post_monthly_content(self):
        """Post content for the current month"""
        logger.info("Starting monthly content posting...")
        
        # Reload settings to pick up any changes made through web interface
        self.settings = self.load_settings()
        logger.info("Settings reloaded from file")
        
        # Check if scheduler is enabled
        if not self.get_setting('enabled', True):
            logger.info("Scheduler is disabled")
            return
        
        if not self.setup_chrome_driver():
            logger.error("Failed to setup Chrome driver")
            self.save_scheduler_error("Failed to setup Chrome driver")
            return
        
        try:
            if not self.navigate_to_instagram():
                logger.error("Failed to navigate to Instagram")
                self.save_scheduler_error("Failed to navigate to Instagram")
                return
        
            # Get number of images from settings (freshly loaded)
            num_images = self.get_setting('num_images', 1)
            logger.info(f"Using {num_images} images per post (from current settings)")
        
            try:
                content = self.get_current_month_content_new(num_images)
            except ValueError as e:
                # Handle insufficient images error
                error_msg = str(e)
                logger.error(f"Scheduler error: {error_msg}")
                self.save_scheduler_error(error_msg)
                return
            
            if not content:
                error_msg = "No content available for current month"
                logger.error(error_msg)
                self.save_scheduler_error(error_msg)
                return
            
            folder, images, caption, post_id = content
            current_month = int(folder.name)
            
            # Enhance text with ChatGPT if enabled
            enhanced_text = self.enhance_text_with_chatgpt(caption)
            print(f"Enhanced text: {enhanced_text}")
            
            # Add month info to caption
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            month_name = month_names[current_month - 1]
            
            final_caption = f"{enhanced_text}\n\n❤️ {month_name} Content\n\n#instagram #monthly #content"
            print(f"Final caption: {final_caption}")
            print(f"Images: {images}")
            
            # Post to Instagram
            if self.post_to_instagram(images, final_caption):
                # Mark as posted
                self.mark_content_as_posted(current_month, post_id, [img.name for img in images])
                logger.info(f"Successfully posted content: {post_id} with {len(images)} images")
                self.clear_scheduler_errors()  # Clear errors on successful post
            else:
                error_msg = f"Failed to post content: {post_id}"
                logger.error(error_msg)
                self.save_scheduler_error(error_msg)
                
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_scheduler_error(self, error_message: str):
        """Save scheduler error to be displayed on dashboard"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'month': datetime.now().month
        }
        
        # Load existing errors
        errors_file = Path('scheduler_errors.json')
        errors = []
        if errors_file.exists():
            try:
                with open(errors_file, 'r') as f:
                    errors = json.load(f)
            except:
                errors = []
        
        # Add new error
        errors.append(error_data)
        
        # Keep only last 10 errors
        errors = errors[-10:]
        
        # Save errors
        try:
            with open(errors_file, 'w') as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save scheduler error: {e}")
    
    def clear_scheduler_errors(self):
        """Clear scheduler errors"""
        errors_file = Path('scheduler_errors.json')
        if errors_file.exists():
            try:
                errors_file.unlink()
            except Exception as e:
                logger.error(f"Failed to clear scheduler errors: {e}")
    
    def get_scheduler_errors(self) -> List[Dict]:
        """Get scheduler errors for dashboard display"""
        errors_file = Path('scheduler_errors.json')
        if not errors_file.exists():
            return []
        
        try:
            with open(errors_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def run_scheduler(self):
        """Run the posting scheduler with dynamic settings reload"""
        # Clear any existing jobs
        schedule.clear()
        
        # Track current settings to detect changes
        last_interval = None
        
        logger.info("Scheduler started with dynamic settings reload")
        logger.info("Settings will be checked and reloaded every minute")
        
        while True:
            try:
                # Reload settings to pick up any changes
                self.settings = self.load_settings()
                current_interval = self.get_setting('post_interval_hours', 4)
                
                # Check if scheduler is disabled
                if not self.get_setting('enabled', True):
                    logger.info("Scheduler is disabled - waiting for re-enable...")
                    schedule.clear()
                    last_interval = None
                    time.sleep(60)
                    continue
                
                # If interval has changed, reschedule
                if last_interval != current_interval:
                    schedule.clear()
                    
                    # Set up the new schedule based on interval
                    # if current_interval >= 24:
                    #     # Daily posting
                    #     schedule.every().day.at("09:00").do(self.post_monthly_content)
                    #     logger.info(f"Rescheduled to post daily at 9:00 AM (interval: {current_interval}h)")
                    # elif current_interval >= 12:
                    #     # Twice daily
                    #     schedule.every().day.at("09:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("21:00").do(self.post_monthly_content)
                    #     logger.info(f"Rescheduled to post twice daily at 9:00 AM and 9:00 PM (interval: {current_interval}h)")
                    # elif current_interval >= 6:
                    #     # Four times daily
                    #     schedule.every().day.at("06:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("12:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("18:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("23:00").do(self.post_monthly_content)
                    #     logger.info(f"Rescheduled to post 4 times daily (interval: {current_interval}h)")
                    # elif current_interval >= 4:
                    #     # 6 times daily
                    #     schedule.every().day.at("00:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("04:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("08:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("12:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("16:00").do(self.post_monthly_content)
                    #     schedule.every().day.at("20:00").do(self.post_monthly_content)
                    #     logger.info(f"Rescheduled to post 6 times daily (interval: {current_interval}h)")
                    # elif current_interval >= 2:
                    #     # 12 times daily
                    #     for hour in range(0, 24, 2):
                    #         schedule.every().day.at(f"{hour:02d}:00").do(self.post_monthly_content)
                    #     logger.info(f"Rescheduled to post every 2 hours (interval: {current_interval}h)")
                    # else:
                        # Every hour or more frequent
                    # schedule.every().minute.do(self.post_monthly_content)
                    schedule.every(current_interval).hours.do(self.post_monthly_content)
                    logger.info(f"Rescheduled to post every hour (interval: {current_interval}h)")
                    
                    last_interval = current_interval
                    logger.info(f"Current settings: {self.get_setting('num_images', 1)} images per post")
                
                # Run pending jobs
                schedule.run_pending()
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Wait 60 seconds before next check
            time.sleep(60)

    def load_image_order(self):
        """Load image order configuration"""
        if self.image_order_file.exists():
            try:
                with open(self.image_order_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_image_order(self):
        """Save image order configuration"""
        try:
            with open(self.image_order_file, 'w', encoding='utf-8') as f:
                json.dump(self.image_order, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving image order: {e}")
    
    def get_month_image_order(self, month):
        """Get the ordered list of image filenames for a specific month"""
        month_key = f"month_{month}"
        month_folder = self.content_dir / str(month)
        
        if not month_folder.exists():
            return []
        
        # Get all image files in the folder
        all_images = [f.name for f in month_folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}]
        
        # Get stored order for this month
        stored_order = self.image_order.get(month_key, [])
        
        # Filter stored order to only include existing files
        existing_ordered = [img for img in stored_order if img in all_images]
        
        # Add any new images that aren't in the stored order (at the end)
        new_images = [img for img in all_images if img not in existing_ordered]
        new_images.sort()  # Sort new images alphabetically
        
        # Combine existing order with new images
        final_order = existing_ordered + new_images
        
        # Update stored order if there are new images
        if new_images:
            self.image_order[month_key] = final_order
            self.save_image_order()
        
        return final_order
    
    def update_month_image_order(self, month, new_order):
        """Update the image order for a specific month"""
        month_key = f"month_{month}"
        month_folder = self.content_dir / str(month)
        
        if not month_folder.exists():
            return False
        
        # Verify all images in new_order actually exist
        existing_images = {f.name for f in month_folder.iterdir() 
                          if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}}
        
        valid_order = [img for img in new_order if img in existing_images]
        
        if valid_order:
            self.image_order[month_key] = valid_order
            self.save_image_order()
            return True
        
        return False

def create_sample_structure():
    """Create sample folder structure for testing"""
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    
    # Create folders for months 1-12
    for month in range(1, 13):
        month_dir = content_dir / str(month)
        month_dir.mkdir(exist_ok=True)
        
        # Create sample CSV file with captions
        csv_file = month_dir / 'captions.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([f"First amazing post for month {month}! 🌟 #month{month} #content"])
            writer.writerow([f"Second incredible post for month {month}! ✨ #instagram #amazing"])
            writer.writerow([f"Third fantastic post for month {month}! 🚀 #social #media"])
            writer.writerow([f"Fourth wonderful post for month {month}! 💫 #creative #content"])
            writer.writerow([f"Fifth awesome post for month {month}! 🎯 #engagement #growth"])
        
        logger.info(f"Created sample structure for month {month}")
    
    logger.info("Sample folder structure created with CSV files. Add your images to the monthly folders!")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'create-sample':
            create_sample_structure()
            return
        elif sys.argv[1] == 'post-now':
            poster = InstagramPoster()
            poster.post_monthly_content()
            return
        elif sys.argv[1] == 'schedule':
            poster = InstagramPoster()
            poster.run_scheduler()
            return
    
    print("Instagram Auto Poster (Selenium Version)")
    print("========================================")
    print()
    print("🌟 Web Interface (Recommended):")
    print("  python run.py                     # Start web interface at http://localhost:5000")
    print()
    print("📱 Command Line Usage:")
    print("  python instagram_poster.py create-sample   # Create sample folder structure")
    print("  python instagram_poster.py post-now        # Post content immediately")
    print("  python instagram_poster.py schedule        # Run scheduler (deprecated)")
    print()
    print("⏰ Scheduler (Background Service):")
    print("  python run_scheduler.py                    # Run scheduler as background service")
    print()
    print("💡 Configure settings via web interface:")
    print("  • Number of images per post (1-5)")
    print("  • Posting interval (1-24 hours)")
    print("  • Enable/disable automatic posting")
    print("  • ChatGPT integration")
    print()
    print("📝 Note: Make sure to set up your Chrome profile and content first!")
    print("     Visit the web interface for easy management.")

if __name__ == "__main__":
    main() 