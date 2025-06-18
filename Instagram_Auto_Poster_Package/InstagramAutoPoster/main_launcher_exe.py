#!/usr/bin/env python3
"""
Windows executable alternative to "Instagram Auto Poster.bat"
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

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
                return cmd
        except:
            continue
    
    return None

def download_and_install_python():
    """Download and install Python automatically"""
    print("Python not found. Downloading and installing Python automatically...")
    print("This may take a few minutes...")
    print()
    
    try:
        import urllib.request
        import tempfile
        
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "InstagramAutoPoster"
        temp_dir.mkdir(exist_ok=True)
        
        installer_path = temp_dir / "python_installer.exe"
        
        print("Downloading Python installer...")
        urllib.request.urlretrieve(
            "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",
            installer_path
        )
        
        if not installer_path.exists():
            print("Failed to download Python installer.")
            print("Please manually install Python from https://python.org/downloads")
            input("Press any key to open Python download page...")
            import webbrowser
            webbrowser.open("https://python.org/downloads")
            return False
        
        print("Installing Python...")
        print("This will take a few minutes, please wait...")
        
        # Install Python silently
        result = subprocess.run([
            str(installer_path), "/quiet", "InstallAllUsers=0", 
            "PrependPath=1", "Include_pip=1", "Include_tcltk=1"
        ], capture_output=True, text=True)
        
        # Clean up installer
        try:
            installer_path.unlink()
        except:
            pass
        
        # Wait a bit for installation to complete
        import time
        time.sleep(10)
        
        print("Refreshing system PATH...")
        
        # Try to find Python again
        return find_python()
        
    except Exception as e:
        print(f"Failed to auto-install Python: {str(e)}")
        print("Please manually install Python from https://python.org/downloads")
        try:
            import webbrowser
            webbrowser.open("https://python.org/downloads")
        except:
            pass
        return None

def main():
    """Main launcher function"""
    print("Checking for Python installation...")
    
    python_cmd = find_python()
    
    if not python_cmd:
        if platform.system() == "Windows":
            python_cmd = download_and_install_python()
            if not python_cmd:
                input("Press Enter to exit...")
                return 1
        else:
            print("Python not found. Please install Python from https://python.org")
            input("Press Enter to exit...")
            return 1
    
    print(f"Found Python: {python_cmd}")
    print("Starting Instagram Auto Poster...")
    
    # Get the directory where this executable is located
    if getattr(sys, 'frozen', False):
        # Running as exe
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent
    
    gui_installer = app_dir / "gui_installer.py"
    
    if gui_installer.exists():
        # Launch the GUI installer
        try:
            result = subprocess.run([python_cmd, str(gui_installer)], cwd=app_dir)
            return result.returncode
        except Exception as e:
            print(f"Failed to start the installer: {str(e)}")
            input("Press Enter to exit...")
            return 1
    else:
        print("GUI installer not found!")
        print("Please ensure gui_installer.py is in the same directory.")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
