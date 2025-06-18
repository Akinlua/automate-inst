#!/usr/bin/env python3
"""
Windows executable alternative to setup_noninteractive.bat
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def log_message(msg, level="INFO"):
    """Log message with level"""
    print(f"[{level}] {msg}")

def find_python():
    """Find suitable Python installation"""
    python_commands = [
        "python3.13", "python3.12", "python3.11", "python3.10", 
        "python3.9", "python3.8", "python3", "python", "py"
    ]
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Extract version number
                if "Python" in version_str:
                    version_part = version_str.split()[1]
                    major, minor = map(int, version_part.split('.')[:2])
                    if major >= 3 and minor >= 8:
                        log_message(f"Found Python {version_part} using command: {cmd}", "SUCCESS")
                        return cmd
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, FileNotFoundError):
            continue
    
    return None

def check_and_install_python():
    """Check for Python and install if needed"""
    log_message("Checking Python installation...")
    
    python_cmd = find_python()
    if python_cmd:
        return python_cmd
    
    log_message("Python 3.8+ not found!", "ERROR")
    log_message("Please install Python from https://python.org/downloads/", "INFO")
    log_message("Make sure to check 'Add Python to PATH' during installation", "INFO")
    
    # Try to open Python download page
    try:
        import webbrowser
        webbrowser.open("https://python.org/downloads/")
    except:
        pass
    
    return None

def setup_virtual_environment(python_cmd):
    """Create and setup virtual environment"""
    log_message("Setting up virtual environment...")
    
    venv_path = Path("venv")
    if not venv_path.exists():
        log_message("Creating virtual environment...")
        result = subprocess.run([python_cmd, "-m", "venv", "venv"], capture_output=True, text=True)
        if result.returncode != 0:
            log_message(f"Failed to create virtual environment: {result.stderr}", "ERROR")
            return False
        log_message("Virtual environment created", "SUCCESS")
    else:
        log_message("Virtual environment already exists", "INFO")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    log_message("Installing dependencies...")
    log_message("This may take a few minutes...", "INFO")
    
    # Use the venv Python
    if platform.system() == "Windows":
        python_venv = Path("venv/Scripts/python.exe")
        pip_venv = Path("venv/Scripts/pip.exe")
    else:
        python_venv = Path("venv/bin/python")
        pip_venv = Path("venv/bin/pip")
    
    if not python_venv.exists():
        log_message("Virtual environment Python not found!", "ERROR")
        return False
    
    # Upgrade pip first
    log_message("Upgrading pip in virtual environment...")
    subprocess.run([str(python_venv), "-m", "pip", "install", "--upgrade", "pip"], 
                  capture_output=True, text=True)
    
    # Try requirements.txt first
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        log_message("Installing from requirements.txt...")
        result = subprocess.run([str(python_venv), "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log_message("Dependencies installed successfully!", "SUCCESS")
            return True
        else:
            log_message("requirements.txt installation failed, trying alternative...", "WARNING")
    
    # Fallback to manual installation
    log_message("Installing dependencies manually...")
    packages = [
        "selenium", "Pillow", "python-dotenv", "schedule", "jiter", "distro", 
        "requests", "flask", "werkzeug", "pytz", "psutil", "undetected-chromedriver", 
        "setuptools", "selenium-driverless"
    ]
    
    for package in packages:
        log_message(f"Installing {package}...")
        result = subprocess.run([str(python_venv), "-m", "pip", "install", package], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log_message(f"Failed to install {package}: {result.stderr}", "WARNING")
    
    log_message("Dependencies installed successfully!", "SUCCESS")
    return True

def create_directories():
    """Create necessary directories"""
    log_message("Creating necessary directories...")
    
    dirs = ["content", "static", "templates"]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            log_message(f"Created directory: {dir_name}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        log_message("Creating .env file...")
        
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
        else:
            with open(env_file, 'w') as f:
                f.write("# Instagram Auto Poster Configuration\n")
                f.write("CONTENT_DIR=content\n")
                f.write("USE_CHATGPT=false\n")
                f.write("OPENAI_API_KEY=\n")
                f.write("CHROME_PROFILE_PATH=\n")
                f.write("CHROME_USER_DATA_DIR=\n")
                f.write("CHROME_PROFILE_NAME=InstagramBot\n")
        
        log_message(".env file created", "SUCCESS")

def check_chrome():
    """Check Chrome installation"""
    log_message("Checking Google Chrome installation...")
    
    chrome_found = False
    
    # Check common Chrome paths on Windows
    if platform.system() == "Windows":
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        ]
        
        for path in chrome_paths:
            if Path(path).exists():
                chrome_found = True
                break
    
    # Try running chrome command
    try:
        result = subprocess.run(["chrome", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            chrome_found = True
    except:
        pass
    
    if chrome_found:
        log_message("Google Chrome found!", "SUCCESS")
    else:
        log_message("Google Chrome not detected!", "WARNING")
        log_message("Please install Google Chrome from: https://www.google.com/chrome/", "WARNING")
        log_message("The application will work but Chrome setup may fail later.", "WARNING")

def main():
    """Main setup function"""
    print("\n" + "="*50)
    print("   Instagram Auto Poster - Automated Setup")
    print("="*50)
    print("\nSetting up Instagram Auto Poster automatically...\n")
    
    try:
        # Check Python
        python_cmd = check_and_install_python()
        if not python_cmd:
            input("Press Enter to exit...")
            return 1
        
        # Setup virtual environment
        if not setup_virtual_environment(python_cmd):
            input("Press Enter to exit...")
            return 1
        
        # Install dependencies
        if not install_dependencies():
            input("Press Enter to exit...")
            return 1
        
        # Create directories
        create_directories()
        
        # Create env file
        create_env_file()
        
        # Check Chrome
        check_chrome()
        
        print("\n" + "="*50)
        print("[SUCCESS] Setup Complete!")
        print("="*50)
        print("\n[SUCCESS] Instagram Auto Poster has been set up successfully!")
        print("[SUCCESS] The application is ready to launch.\n")
        
        return 0
        
    except Exception as e:
        log_message(f"Setup failed with error: {str(e)}", "ERROR")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
