#!/usr/bin/env python3
"""
Windows executable alternative to start.bat (interactive version)
"""
import os
import sys
import platform
import subprocess
import signal
from pathlib import Path

def main():
    """Main start function"""
    os.system('cls' if platform.system() == "Windows" else 'clear')
    
    print("\n" + "="*50)
    print("   Instagram Auto Poster - Quick Start")
    print("="*50)
    print()
    
    try:
        # Import and run the non-interactive start
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from start_noninteractive_exe import (
            check_venv, check_app_file, start_server, check_server_ready, open_browser
        )
        
        # Check prerequisites
        if not check_venv():
            print("\nPlease run setup first.")
            input("Press Enter to exit...")
            return 1
        
        if not check_app_file():
            input("Press Enter to exit...")
            return 1
        
        print("Starting Instagram Auto Poster...")
        print("Server will be available at: http://localhost:5003")
        print()
        
        # Start server
        process = start_server()
        if not process:
            print("Failed to start server!")
            input("Press Enter to exit...")
            return 1
        
        # Check if server is ready
        if check_server_ready():
            print("\nServer started successfully!")
            open_browser()
            
            print("\nApplication is running!")
            print("You can now use the web interface.")
            print("\nPress Ctrl+C to stop the server...")
            
            # Keep running until user stops
            try:
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
            print("Server failed to start properly!")
            input("Press Enter to exit...")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
