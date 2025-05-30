#!/usr/bin/env python3
"""
Setup script for Instagram Auto Poster
Helps configure credentials and settings
"""

import os
import sys
from pathlib import Path
import getpass

def create_env_file():
    """Create .env file with user credentials"""
    print("🔧 Instagram Auto Poster Setup")
    print("=" * 40)
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📱 Instagram Credentials")
    username = input("Instagram Username: ").strip()
    password = getpass.getpass("Instagram Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required!")
        return
    
    print("\n🤖 ChatGPT Integration (Optional)")
    use_chatgpt = input("Enable ChatGPT text enhancement? (y/N): ").lower() == 'y'
    
    openai_key = ""
    if use_chatgpt:
        openai_key = getpass.getpass("OpenAI API Key: ").strip()
        if not openai_key:
            print("⚠️  No OpenAI key provided. ChatGPT will be disabled.")
            use_chatgpt = False
    
    print("\n📁 Content Directory")
    content_dir = input("Content directory name (default: content): ").strip()
    if not content_dir:
        content_dir = "content"
    
    print("\n⏰ Posting Schedule")
    try:
        post_hour = int(input("Posting hour (0-23, default: 12): ") or "12")
        post_minute = int(input("Posting minute (0-59, default: 0): ") or "0")
    except ValueError:
        print("⚠️  Invalid time format. Using defaults (12:00)")
        post_hour = 12
        post_minute = 0
    
    # Create .env content
    env_content = f"""# Instagram Credentials
INSTAGRAM_USERNAME={username}
INSTAGRAM_PASSWORD={password}

# OpenAI API Key (optional - for text enhancement)
OPENAI_API_KEY={openai_key}

# Content Directory
CONTENT_DIR={content_dir}

# Posting Schedule (hour in 24h format)
POST_HOUR={post_hour}
POST_MINUTE={post_minute}

# Enable ChatGPT text enhancement (true/false)
USE_CHATGPT={str(use_chatgpt).lower()}
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print(f"\n✅ Configuration saved to .env")
        print(f"📁 Content directory: {content_dir}")
        print(f"⏰ Posting time: {post_hour:02d}:{post_minute:02d}")
        print(f"🤖 ChatGPT: {'Enabled' if use_chatgpt else 'Disabled'}")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return
    
    # Ask if user wants to create sample structure
    create_sample = input(f"\n📂 Create sample folder structure in '{content_dir}'? (Y/n): ").lower()
    if create_sample != 'n':
        create_content_structure(content_dir)

def create_content_structure(content_dir):
    """Create the monthly content folder structure"""
    try:
        content_path = Path(content_dir)
        content_path.mkdir(exist_ok=True)
        
        # Create folders for months 1-12
        for month in range(1, 13):
            month_dir = content_path / str(month)
            month_dir.mkdir(exist_ok=True)
            
            # Create sample text files
            (month_dir / 'post1.txt').write_text(f"Sample post for month {month}! 🌟\n\nAdd your own content here and replace this text.")
            (month_dir / 'post2.txt').write_text(f"Another sample post for month {month}! ✨\n\nYou can have multiple text files per month.")
        
        print(f"✅ Created monthly folders (1-12) in '{content_dir}'")
        print("📝 Sample text files created in each folder")
        print("🖼️  Add your images to the monthly folders!")
        
    except Exception as e:
        print(f"❌ Error creating folder structure: {e}")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        print("💡 Try running: pip install -r requirements.txt")

def main():
    """Main setup function"""
    print("🚀 Instagram Auto Poster Setup")
    print("=" * 40)
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found!")
        print("💡 Make sure you're in the correct directory")
        return
    
    # Install dependencies
    install_deps = input("📦 Install Python dependencies? (Y/n): ").lower()
    if install_deps != 'n':
        install_dependencies()
    
    # Create configuration
    print("\n" + "=" * 40)
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Add your images to the monthly folders")
    print("2. Edit the text files with your content")
    print("3. Test with: python instagram_poster.py post-now")
    print("4. Start scheduler: python instagram_poster.py schedule")
    print("\n⚠️  Important: Keep your .env file secure and don't share it!")

if __name__ == "__main__":
    main() 