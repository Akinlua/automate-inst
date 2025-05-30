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
    
    # def upload_image(self, image_path):
    #     """Upload an image file"""
    #     try:
    #         # Look for file input
    #         file_input = self.wait.until(EC.presence_of_element_located((
    #             By.XPATH, "//input[@type='file']"
    #         )))
            
    #         # Upload the file
    #         absolute_path = os.path.abspath(image_path)
    #         file_input.send_keys(absolute_path)
    #         logger.info(f"Uploaded image: {image_path}")
    #         time.sleep(5)  # Wait for image to process
    #         return True
    #     except Exception as e:
    #         logger.error(f"Failed to upload image: {e}")
    #         return False
    
    def upload_image(self, image_path):
        """Upload an image using JavaScript File API"""
        try:
            # Get absolute path
            absolute_path = os.path.abspath(image_path)
            logger.info(f"Uploading image: {absolute_path}")
            
            # Read file and encode to base64
            with open(absolute_path, 'rb') as file:
                file_content = base64.b64encode(file.read()).decode()
            
            # Get just the filename
            filename = os.path.basename(absolute_path)
            
            # Determine MIME type based on file extension
            file_ext = os.path.splitext(filename)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp'
            }.get(file_ext, 'image/jpeg')
            # print(file_content)
            
            # JavaScript to create file and upload
            script = f"""
            var input = document.querySelector('input[type="file"]');
            if (!input) {{
                throw new Error('File input not found');
            }}
            
            var file = new File([Uint8Array.from(atob('{file_content}'), c => c.charCodeAt(0))], 
                                '{filename}', {{type: '{mime_type}'}});
            var dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            
            // Trigger change event
            input.dispatchEvent(new Event('change', {{bubbles: true}}));
            input.dispatchEvent(new Event('input', {{bubbles: true}}));
            
            return true;
            """
            
            # Execute the script
            result = self.driver.execute_script(script)
            time.sleep(5)
            
            # Wait for the image to be processed
            try:
                # Wait for image to be loaded/processed - look for the crop interface
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//canvas")),  # Image canvas
                    EC.presence_of_element_located((By.XPATH, "//img[contains(@style, 'object-fit')]")),  # Image preview
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")),  # Next button
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'crop')]"))  # Crop interface
                ))
                logger.info("Image uploaded and processed successfully")
                time.sleep(3)  # Give it a moment to fully load
                return True
                
            except Exception as e:
                logger.error(f"Image didn't load properly after upload: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to upload image using JavaScript: {e}")
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
            caption_element = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.xw2csxc.x1odjw0f.x1n2onr6.x1hnll1o.xpqswwc.xl565be.x5dp1im.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1w2wdq1.xen30ot.x1swvt13.x1pi30zi.xh8yej3.x5n08af.notranslate"
            )))
            
            # Click on the element to focus it
            caption_element.click()
            logger.info("Clicked on caption area")
            time.sleep(1)

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
    
    def post_to_instagram(self, image_path: Path, caption: str) -> bool:
        """Post image with caption to Instagram using Selenium"""
        try:
            # Prepare image
            prepared_image = self.prepare_image(image_path)
            
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
            
            # Step 4: Upload image
            if not self.upload_image(str(prepared_image)):
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
            
            # Clean up temporary resized image if created
            if prepared_image != image_path and prepared_image.exists():
                prepared_image.unlink()
            
            logger.info("Successfully posted to Instagram using Selenium")
            return True
            
        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            return False
    
    def get_current_month_content(self) -> Optional[Tuple[Path, List[Path], List[str]]]:
        """Get content for the current month"""
        current_month = datetime.now().month
        monthly_folders = self.get_monthly_folders()
        
        # Find folder for current month
        current_month_folder = None
        for folder in monthly_folders:
            if int(folder.name) == current_month:
                current_month_folder = folder
                break
        
        if not current_month_folder:
            logger.warning(f"No folder found for current month: {current_month}")
            return None
        
        # Get images and text files
        images = self.get_images_from_folder(current_month_folder)
        text_files = self.get_text_files_from_folder(current_month_folder)
        
        if not images:
            logger.warning(f"No images found in month {current_month}")
            return None
        
        if not text_files:
            logger.warning(f"No text files found in month {current_month}")
            return None
        
        # Read all text files
        texts = []
        for text_file in text_files:
            content = self.read_text_file(text_file)
            if content:
                texts.append(content)
        
        if not texts:
            logger.warning(f"No valid text content found in month {current_month}")
            return None
        
        return current_month_folder, images, texts
    
    def create_content_key(self, month: int, image_name: str, text_index: int) -> str:
        """Create a unique key for tracking posted content"""
        return f"{month}_{image_name}_{text_index}"
    
    def post_monthly_content(self):
        """Post content for the current month"""
        logger.info("Starting monthly content posting...")
        
        if not self.setup_chrome_driver():
            logger.error("Failed to setup Chrome driver")
            return
        
        try:
            if not self.navigate_to_instagram():
                logger.error("Failed to navigate to Instagram")
                return
        
            # time.sleep(10000)
            
            content = self.get_current_month_content()
            if not content:
                logger.error("No content available for current month")
                return
            
            folder, images, texts = content
            current_month = int(folder.name)
            
            # Randomly select an image and text combination that hasn't been posted
            available_combinations = []
            
            for i, image in enumerate(images):
                for j, text in enumerate(texts):
                    content_key = self.create_content_key(current_month, image.name, j)
                    if content_key not in self.posted_content:
                        available_combinations.append((image, text, content_key))
            
            if not available_combinations:
                logger.info("All content for this month has already been posted")
                return
            
            # Randomly select a combination
            image, text, content_key = random.choice(available_combinations)
            
            # Enhance text with ChatGPT if enabled
            enhanced_text = self.enhance_text_with_chatgpt(text)
            print(f"Enhanced text: {enhanced_text}")
            
            # Add month info to caption
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            month_name = month_names[current_month - 1]
            
            final_caption = f"{enhanced_text}\n\n❤️ {month_name} Content\n\n#instagram #monthly #content"
            print(f"Final caption: {final_caption}")
            print(f"Image: {image}")
            
            # Post to Instagram
            if self.post_to_instagram(image, final_caption):
                # Mark as posted
                self.posted_content[content_key] = {
                    'posted_at': datetime.now().isoformat(),
                    'image': image.name,
                    'month': current_month,
                    'text_index': texts.index(text)
                }
                self.save_posted_content()
                logger.info(f"Successfully posted content: {content_key}")
            else:
                logger.error(f"Failed to post content: {content_key}")
                
        finally:
            if self.driver:
                self.driver.quit()
    
    def run_scheduler(self):
        """Run the posting scheduler"""
        post_hour = int(os.getenv('POST_HOUR', 12))
        post_minute = int(os.getenv('POST_MINUTE', 0))
        
        # Schedule daily posting
        schedule.every().day.at(f"{post_hour:02d}:{post_minute:02d}").do(self.post_monthly_content)
        
        logger.info(f"Scheduler started. Will post daily at {post_hour:02d}:{post_minute:02d}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def create_sample_structure():
    """Create sample folder structure for testing"""
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    
    # Create folders for months 1-12
    for month in range(1, 13):
        month_dir = content_dir / str(month)
        month_dir.mkdir(exist_ok=True)
        
        # Create sample text files
        (month_dir / 'post1.txt').write_text(f"This is sample content for month {month}! 🌟")
        (month_dir / 'post2.txt').write_text(f"Another great post for month {month}! ✨")
        
        logger.info(f"Created sample structure for month {month}")
    
    logger.info("Sample folder structure created. Add your images to the monthly folders!")

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
    print("Usage:")
    print("  python instagram_poster.py create-sample  # Create sample folder structure")
    print("  python instagram_poster.py post-now       # Post content immediately")
    print("  python instagram_poster.py schedule       # Run scheduler")

if __name__ == "__main__":
    main() 