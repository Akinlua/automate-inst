#!/usr/bin/env python3
import os
import sys
import glob
import random
import logging
import time
import json
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import openai

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("instagram_automation")

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_DIR = os.getenv("BASE_DIR", "content")
CHROME_USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
CHROME_PROFILE_NAME = os.getenv("CHROME_PROFILE_NAME", "InstagramBot")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver")

# Set up OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def get_chrome_user_data_dir():
    """Get the default Chrome user data directory for the current OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    elif system == "Windows":
        return os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    else:  # Linux
        return os.path.expanduser("~/.config/google-chrome")

class InstagramSeleniumAutomationV2:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.chrome_user_data_dir = CHROME_USER_DATA_DIR or get_chrome_user_data_dir()
        self.profile_name = CHROME_PROFILE_NAME
        
    def setup_chrome_driver(self):
        """Setup Chrome driver with Chrome's built-in profile system"""
        chrome_options = Options()
        
        # Use Chrome's built-in profile system
        chrome_options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={self.profile_name}")
        logger.info(f"Using Chrome profile: {self.profile_name}")
        
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
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            # self.wait = WebDriverWait(self.driver, 20)
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
                logger.error("Please run setup_chrome_v2.py first to set up the profile!")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False
    
    def click_new_post_icon(self):
        """Click on the + icon for new post"""
        try:
            # Use the specific XPath provided for the + icon
            new_post_icon = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//*[@id='mount_0_0_5V']/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div[7]/div/span/div/a/div"
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
                By.XPATH, "//*[@id='mount_0_0_5V']/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div[7]/div/span/div/div/div/div[1]/a[1]/div[2]"
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
                By.XPATH, "/html/body/div[11]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button"
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
    
    def upload_image(self, image_path):
        """Upload an image file"""
        try:
            # Look for file input
            file_input = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='file']"
            )))
            
            # Upload the file
            absolute_path = os.path.abspath(image_path)
            file_input.send_keys(absolute_path)
            logger.info(f"Uploaded image: {image_path}")
            time.sleep(5)  # Wait for image to process
            return True
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return False
    
    def click_next_button(self, step_name=""):
        """Click the Next button"""
        try:
            # Use the specific XPath provided for Next button
            next_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[11]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div"
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
                    By.XPATH, "//button[contains(text(), 'Next')]"
                )))
                fallback_next.click()
                logger.info(f"Clicked Next button {step_name} (fallback selector)")
                time.sleep(3)
                return True
            except Exception as e2:
                logger.error(f"Fallback Next button selector also failed: {e2}")
                return False
    
    def add_caption(self, caption):
        """Add caption to the P tag"""
        try:
            # Use the specific XPath provided for the caption P tag
            caption_element = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[11]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div[1]/p"
            )))
            
            # Click on the element and add caption
            caption_element.click()
            time.sleep(1)
            caption_element.clear()
            caption_element.send_keys(caption)
            logger.info("Added caption to post")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Failed to add caption using specific XPath: {e}")
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
            except Exception as e2:
                logger.error(f"Fallback caption selector also failed: {e2}")
                return False
    
    def click_share_button(self):
        """Click the Share button"""
        try:
            # Use the specific XPath provided for Share button
            share_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[11]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div"
            )))
            share_button.click()
            logger.info("Clicked Share button - Post published!")
            time.sleep(5)  # Wait for post to process
            return True
        except Exception as e:
            logger.error(f"Could not find or click Share button: {e}")
            # Fallback to text-based selector
            try:
                fallback_share = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(text(), 'Share')]"
                )))
                fallback_share.click()
                logger.info("Clicked Share button - Post published! (fallback selector)")
                time.sleep(5)
                return True
            except Exception as e2:
                logger.error(f"Fallback Share button selector also failed: {e2}")
                return False
    
    def create_and_upload_post(self, image_path, caption):
        """Complete workflow to create and upload a post"""
        try:
            # Step 1: Click the + icon for new post
            if not self.click_new_post_icon():
                return False
            
            # Step 2: Click the Post button
            if not self.click_post_button():
                return False
            
            # Step 3: Click Select from computer
            if not self.click_select_from_computer():
                return False
            
            # Step 4: Upload image
            if not self.upload_image(image_path):
                return False
            
            # Step 5: Click Next button (first time)
            if not self.click_next_button("(crop/filter step)"):
                return False
            
            # Step 6: Click Next button (second time)
            if not self.click_next_button("(final step)"):
                return False
            
            # Step 7: Add caption
            if not self.add_caption(caption):
                return False
            
            # Step 8: Click Share button
            if not self.click_share_button():
                return False
            
            logger.info("Successfully completed post upload workflow!")
            return True
            
        except Exception as e:
            logger.error(f"Error in create_and_upload_post workflow: {e}")
            return False

    def get_month_folders(self):
        """Get all month folders in the base directory"""
        folders = glob.glob(os.path.join(BASE_DIR, "*"))
        month_folders = []
        
        for folder in folders:
            if os.path.isdir(folder) and os.path.basename(folder).isdigit():
                month_folders.append(folder)
                
        logger.info(f"Found {len(month_folders)} month folders")
        return sorted(month_folders)
    
    def get_content_for_month(self, month_folder):
        """Get all text files and images for a specific month"""
        txt_files = glob.glob(os.path.join(month_folder, "*.txt"))
        image_files = []
        
        # Get all image files (jpg, jpeg, png)
        for ext in ["jpg", "jpeg", "png"]:
            image_files.extend(glob.glob(os.path.join(month_folder, f"*.{ext}")))
            image_files.extend(glob.glob(os.path.join(month_folder, f"*.{ext.upper()}")))
        
        logger.info(f"Month {os.path.basename(month_folder)}: Found {len(txt_files)} text files and {len(image_files)} images")
        return txt_files, image_files
    
    def read_text_file(self, text_file):
        """Read content from a text file"""
        try:
            with open(text_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            return content
        except Exception as e:
            logger.error(f"Error reading text file {text_file}: {e}")
            return ""
    
    def enhance_text_with_gpt(self, text, month_folder):
        """Use OpenAI's GPT to enhance or generate Instagram caption"""
        if not OPENAI_API_KEY:
            logger.warning("No OpenAI API key provided, using original text")
            return text or "Monthly post"
            
        month_number = int(os.path.basename(month_folder))
        month_name = datetime(2023, month_number, 1).strftime("%B") if 1 <= month_number <= 12 else "Unknown"
        
        if not text:
            prompt = f"Generate an engaging Instagram caption about the month of {month_name}."
        else:
            prompt = f"Make this text more engaging as an Instagram caption, keeping the original meaning: {text}"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media expert who creates engaging Instagram captions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            enhanced_text = response.choices[0].message.content.strip()
            logger.info("Successfully enhanced text with GPT")
            return enhanced_text
        except Exception as e:
            logger.error(f"Error enhancing text with GPT: {e}")
            return text or f"Caption for {month_name}"
    
    def process_month(self, month_folder, force=False):
        """Process content for a specific month and post to Instagram"""
        month_number = os.path.basename(month_folder)
        
        # Check if we've already processed this month
        status_file = os.path.join(month_folder, ".posted")
        if os.path.exists(status_file) and not force:
            logger.info(f"Month {month_number} already processed. Skipping...")
            return False
            
        # Get content for this month
        txt_files, image_files = self.get_content_for_month(month_folder)
        
        if not image_files:
            logger.warning(f"Month {month_number} has no images. Skipping...")
            return False
            
        # Choose a random image
        image_path = random.choice(image_files)
        
        # Get text content (combine all text files if multiple exist)
        full_text = ""
        for txt_file in txt_files:
            content = self.read_text_file(txt_file)
            full_text += content + "\n\n"
        
        # Enhance text with GPT
        caption = self.enhance_text_with_gpt(full_text.strip(), month_folder)
        
        # Add hashtags
        caption += "\n\n#monthlypost #automation"
        
        # Create and post to Instagram using the new workflow
        if self.create_and_upload_post(image_path, caption):
            # Mark as posted
            with open(status_file, 'w') as f:
                f.write(str(datetime.now()))
            logger.info(f"Month {month_number} successfully processed and posted")
            return True
        
        logger.error(f"Failed to process month {month_number}")
        return False
    
    def run(self, specific_month=None, force=False):
        """Run the automation for all months or a specific month"""
        if not self.setup_chrome_driver():
            logger.error("Failed to setup Chrome driver. Exiting...")
            return
            
        try:
            if not self.navigate_to_instagram():
                logger.error("Failed to navigate to Instagram. Make sure you ran setup_chrome_v2.py first!")
                return
                
            month_folders = self.get_month_folders()
            
            if specific_month:
                # Process only the specified month
                target_folder = os.path.join(BASE_DIR, specific_month)
                if os.path.exists(target_folder) and os.path.isdir(target_folder):
                    logger.info(f"Processing specific month: {specific_month}")
                    self.process_month(target_folder, force=force)
                else:
                    logger.error(f"Month folder '{specific_month}' not found")
            else:
                # Process all months
                for month_folder in month_folders:
                    success = self.process_month(month_folder, force=force)
                    if success:
                        # Wait between posts to avoid rate limiting
                        logger.info("Waiting 5 minutes before next post...")
                        time.sleep(300)  # 5-minute delay between posts
                        
        finally:
            if self.driver:
                input("Press Enter to close browser...")  # Keep browser open for inspection
                self.driver.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Instagram Automation Tool with Chrome Built-in Profiles (V2)")
    parser.add_argument("--month", help="Process specific month (folder name)")
    parser.add_argument("--force", action="store_true", help="Force processing even if already posted")
    args = parser.parse_args()
    
    automation = InstagramSeleniumAutomationV2()
    automation.run(specific_month=args.month, force=args.force) 