#!/usr/bin/env python3
"""
Windows executable alternative to start_noninteractive.bat
"""
import os
import sys
import subprocess
import platform
import time
import socket
import webbrowser
from pathlib import Path

def log_message(msg, level="INFO"):
    """Log message with level"""
    print(f"[{level}] {msg}")

def check_venv():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if not venv_path.exists():
        log_message("Virtual environment not found!", "ERROR")
        log_message("Please run setup first.", "INFO")
        return False
    return True

def check_app_file():
    """Check if app.py exists"""
    app_file = Path("app.py")
    if not app_file.exists():
        log_message("app.py not found!", "ERROR")
        log_message("Please make sure all application files are in this directory.", "INFO")
        return False
    return True

def get_venv_python():
    """Get the virtual environment Python executable"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def start_server():
    """Start the Flask server"""
    log_message("Starting Instagram Auto Poster...")
    
    python_exe = get_venv_python()
    if not python_exe.exists():
        log_message("Virtual environment Python not found!", "ERROR")
        return False
    
    log_message("Starting server process...")
    
    # Start the server process
    if platform.system() == "Windows":
        # Use CREATE_NEW_PROCESS_GROUP for Windows
        process = subprocess.Popen(
            [str(python_exe), "app.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL
        )
    else:
        # Use new session for Unix-like systems
        process = subprocess.Popen(
            [str(python_exe), "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid  # Create new session - completely detached
        )
    
    return process

def check_server_ready(max_attempts=10):
    """Check if server is ready"""
    log_message("Waiting for server to initialize...")
    
    for attempt in range(max_attempts):
        time.sleep(2)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 5003))
            sock.close()
            
            if result == 0:
                log_message("Server is ready and listening on port 5003!", "SUCCESS")
                return True
        except:
            pass
        
        log_message(f"Waiting for server... ({attempt + 1}/{max_attempts})")
    
    return False

def open_browser():
    """Open browser to the application"""
    try:
        log_message("Opening browser...")
        webbrowser.open("http://localhost:5003")
        return True
    except Exception as e:
        log_message(f"Failed to open browser: {str(e)}", "WARNING")
        return False

def main():
    """Main start function"""
    print("\n" + "="*50)
    print("   Instagram Auto Poster - Starting...")
    print("="*50)
    print()
    
    try:
        # Check prerequisites
        if not check_venv():
            input("Press Enter to exit...")
            return 1
        
        if not check_app_file():
            input("Press Enter to exit...")
            return 1
        
        # Start server
        log_message("Server will be available at: http://localhost:5003", "SUCCESS")
        
        process = start_server()
        if not process:
            log_message("Failed to start server process!", "ERROR")
            input("Press Enter to exit...")
            return 1
        
        # Check if server is ready
        if check_server_ready():
            log_message("Server confirmed ready at: http://localhost:5003", "SUCCESS")
            log_message("Server started successfully in background!", "SUCCESS")
            
            # Open browser
            open_browser()
            
            log_message("Application is now running in the background.")
            log_message("You can close this window - the server will continue running.")
            log_message("To stop the server, use the web interface or Task Manager.")
            
            return 0
        else:
            log_message("Server failed to start properly!", "ERROR")
            
            # Try to get error output
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stderr:
                    log_message(f"Server error: {stderr.decode()}", "ERROR")
            except:
                pass
            
            input("Press Enter to exit...")
            return 1
            
    except Exception as e:
        log_message(f"Start failed with error: {str(e)}", "ERROR")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
