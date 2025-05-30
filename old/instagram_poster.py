#!/usr/bin/env python3
"""
Instagram Auto Poster
Automatically posts content from monthly folders to Instagram
"""

import os
import sys
import time
import random
import logging
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

# Third-party imports
from dotenv import load_dotenv
from instagrapi import Client
from PIL import Image
import openai

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

class InstagramPoster:
    def __init__(self):
        """Initialize the Instagram poster with credentials and settings"""
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.content_dir = Path(os.getenv('CONTENT_DIR', 'content'))
        self.use_chatgpt = os.getenv('USE_CHATGPT', 'false').lower() == 'true'
        
        if not self.username or not self.password:
            raise ValueError("Instagram credentials not found in environment variables")
        
        # Initialize Instagram client
        self.client = Client()
        self.client.delay_range = [1, 3]  # Random delay between requests
        
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
    
    def login(self) -> bool:
        """Login to Instagram"""
        try:
            logger.info("Logging into Instagram...")
            self.client.login(self.username, self.password)
            logger.info("Successfully logged into Instagram")
            return True
        except Exception as e:
            logger.error(f"Failed to login to Instagram: {e}")
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
        """Post image with caption to Instagram"""
        try:
            # Prepare image
            prepared_image = self.prepare_image(image_path)
            
            # Upload photo
            media = self.client.photo_upload(
                path=str(prepared_image),
                caption=caption
            )
            
            # Clean up temporary resized image if created
            if prepared_image != image_path and prepared_image.exists():
                prepared_image.unlink()
            
            logger.info(f"Successfully posted to Instagram: {media.pk}")
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
        
        if not self.login():
            return
        
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
        
        # Add month info to caption
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = month_names[current_month - 1]
        
        final_caption = f"{enhanced_text}\n\n📅 {month_name} Content\n\n#instagram #monthly #content"
        
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
    
    print("Instagram Auto Poster")
    print("Usage:")
    print("  python instagram_poster.py create-sample  # Create sample folder structure")
    print("  python instagram_poster.py post-now       # Post content immediately")
    print("  python instagram_poster.py schedule       # Run scheduler")

if __name__ == "__main__":
    main() 