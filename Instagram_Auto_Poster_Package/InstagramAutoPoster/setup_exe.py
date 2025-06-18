#!/usr/bin/env python3
"""
Windows executable alternative to setup.bat (interactive version)
"""
import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def log_message(msg, level="INFO"):
    """Log message with level"""
    print(f"[{level}] {msg}")

def wait_for_user():
    """Wait for user input"""
    input("Press any key to continue...")

def find_python():
    """Find suitable Python installation"""
    python_commands = ["python", "python3", "py"]
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"{cmd} found!")
                print(version_str)
                return cmd
        except:
            continue
    
    return None

def main():
    """Main setup function"""
    os.system('cls' if platform.system() == "Windows" else 'clear')
    
    print("\n" + "="*50)
    print("   Instagram Auto Poster - Setup & Launch")
    print("="*50)
    print("\nThis script will:")
    print("1. Check and install Python if needed")
    print("2. Create virtual environment")
    print("3. Install all dependencies")
    print("4. Create necessary folders")
    print("5. Start the web application")
    print("\nPress any key to continue...")
    wait_for_user()
    
    try:
        # Import and run the non-interactive setup
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Use the same logic as setup_noninteractive_exe.py but with user interaction
        from setup_noninteractive_exe import (
            check_and_install_python, setup_virtual_environment, 
            install_dependencies, create_directories, create_env_file, check_chrome
        )
        
        print("\n[1/5] Checking Python installation...")
        python_cmd = check_and_install_python()
        if not python_cmd:
            wait_for_user()
            return 1
        
        print("\n[2/5] Setting up virtual environment...")
        if not setup_virtual_environment(python_cmd):
            wait_for_user()
            return 1
        
        print("\n[3/5] Installing dependencies...")
        print("This may take a few minutes...")
        if not install_dependencies():
            wait_for_user()
            return 1
        
        print("\n[4/5] Creating necessary directories...")
        create_directories()
        create_env_file()
        
        print("\n[5/5] Checking Chrome installation...")
        check_chrome()
        
        print("\n" + "="*50)
        print("   Setup Complete!")
        print("="*50)
        print("\nThe web application will now start...")
        print("\nOnce started, open your browser and go to:")
        print("http://localhost:5003")
        print("\nTo stop the application, press Ctrl+C in this window.")
        print("\nPress any key to start the application...")
        wait_for_user()
        
        # Start the application
        print("\nStarting Instagram Auto Poster...")
        
        # Import and run the start functionality
        from start_noninteractive_exe import get_venv_python, start_server, check_server_ready, open_browser
        
        process = start_server()
        if process and check_server_ready():
            open_browser()
            
            print("\nApplication started successfully!")
            print("The server is running. You can use the web interface now.")
            
            # Keep the process running until user stops it
            try:
                print("\nPress Ctrl+C to stop the server...")
                process.wait()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print("Server stopped.")
        else:
            print("\nApplication failed to start properly.")
            wait_for_user()
            return 1
        
        return 0
        
    except Exception as e:
        log_message(f"Setup failed with error: {str(e)}", "ERROR")
        wait_for_user()
        return 1

if __name__ == "__main__":
    sys.exit(main())
