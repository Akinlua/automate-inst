#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import subprocess
import threading
import platform
import time
import signal
import psutil
from pathlib import Path

class InstagramAutoPoserInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instagram Auto Poster - Setup")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Check for auto-launch mode
        self.auto_launch_mode = "--auto-launch" in sys.argv
        
        # Center the window
        self.center_window()
        
        # Set app icon (if available)
        try:
            self.root.iconbitmap('InstagramAutoPoster/static/favicon.ico')
        except:
            pass
        
        # Variables
        self.is_setup_mode = True
        self.app_dir = Path(__file__).parent / "InstagramAutoPoster"
        self.setup_complete = False
        self.server_process = None
        self.server_running = False
        
        # Create GUI
        self.create_widgets()
        
        # Auto-detect mode
        self.detect_mode()
        
        # Update auto-startup button status
        self.update_startup_button()
        
        # Handle auto-launch mode
        if self.auto_launch_mode:
            self.handle_auto_launch()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"600x550+{x}+{y}")
    
    def create_widgets(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg="#1a237e", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Instagram Auto Poster",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1a237e"
        )
        title_label.pack(pady=20)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)
        
        # Welcome message
        self.welcome_label = tk.Label(
            self.content_frame,
            text="Welcome! Click 'Start Setup' to install all requirements and launch the application.",
            font=("Arial", 11),
            wraplength=550,
            justify="center"
        )
        self.welcome_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(self.content_frame)
        status_frame.pack(fill="x", pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame, 
            mode='indeterminate',
            length=550
        )
        self.progress.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="Ready to start...",
            font=("Arial", 10),
            fg="#666"
        )
        self.status_label.pack()
        
        # Server status frame
        server_status_frame = tk.Frame(self.content_frame)
        server_status_frame.pack(fill="x", pady=5)
        
        self.server_status_label = tk.Label(
            server_status_frame,
            text="Server Status: Stopped",
            font=("Arial", 10, "bold"),
            fg="#d32f2f"
        )
        self.server_status_label.pack()
        
        # Log area
        log_frame = tk.Frame(self.content_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Label(log_frame, text="Installation Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Main action button
        self.action_button = tk.Button(
            button_frame,
            text="Start Setup",
            font=("Arial", 12, "bold"),
            bg="#4caf50",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_setup
        )
        self.action_button.pack(side="left")
        
        # Stop server button
        self.stop_button = tk.Button(
            button_frame,
            text="Stop Server",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=8,
            command=self.stop_server,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Open app folder button
        self.folder_button = tk.Button(
            button_frame,
            text="Open App Folder",
            font=("Arial", 10),
            padx=15,
            pady=8,
            command=self.open_app_folder
        )
        self.folder_button.pack(side="left")
        
        # Auto-startup button
        self.startup_button = tk.Button(
            button_frame,
            text="Enable Auto-Startup",
            font=("Arial", 10),
            bg="#9c27b0",
            fg="white",
            padx=15,
            pady=8,
            command=self.toggle_auto_startup
        )
        self.startup_button.pack(side="left", padx=5)
        
        # Close button
        self.close_button = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 10),
            padx=15,
            pady=8,
            command=self.on_closing
        )
        self.close_button.pack(side="right")
    
    def detect_mode(self):
        """Detect if this is first setup or subsequent launch"""
        venv_path = self.app_dir / "venv"
        
        # Check if server is already running
        server_already_running = False
        try:
            for conn in psutil.net_connections():
                if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == 5003:
                    server_already_running = True
                    break
        except:
            pass
        
        if venv_path.exists():
            self.is_setup_mode = False
            if server_already_running:
                # Server is already running
                self.welcome_label.config(text="Instagram Auto Poster is already running! Server is active on port 5003.")
                self.action_button.config(
                    text="Open in Browser",
                    bg="#ff9800",
                    command=self.open_browser
                )
                self.status_label.config(text="Server is running - ready to use!")
                self.update_server_status(True)
                self.log_message("✅ Detected running server on port 5003")
                self.log_message("🌐 Server is available at: http://localhost:5003")
            else:
                # Setup complete but server not running
                self.welcome_label.config(text="Instagram Auto Poster is ready! Click 'Launch App' to start.")
                self.action_button.config(
                    text="Launch App",
                    bg="#2196f3",
                    command=self.launch_app
                )
                self.status_label.config(text="Application ready to launch...")
    
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
        self.root.update()
    
    def update_server_status(self, running):
        """Update server status indicator"""
        self.server_running = running
        if running:
            self.server_status_label.config(
                text="Server Status: Running ✓",
                fg="#388e3c"
            )
            self.stop_button.config(state="normal")
        else:
            self.server_status_label.config(
                text="Server Status: Stopped",
                fg="#d32f2f"
            )
            self.stop_button.config(state="disabled")
    
    def find_and_kill_processes(self, process_name="python"):
        """Find and kill processes related to the app"""
        try:
            killed_any = False
            # Find processes by name containing app.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'app.py' in cmdline and 'python' in proc.info['name'].lower():
                            self.log_message(f"🛑 Terminating Flask app process (PID: {proc.info['pid']})")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                                killed_any = True
                            except psutil.TimeoutExpired:
                                proc.kill()
                                killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process already gone or no access - this is fine
                    continue
            
            # Also try to find by port
            for conn in psutil.net_connections():
                try:
                    if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == 5003:
                        proc = psutil.Process(conn.pid)
                        self.log_message(f"🛑 Terminating process using port 5003: {proc.name()} (PID: {conn.pid})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                            killed_any = True
                        except psutil.TimeoutExpired:
                            proc.kill()
                            killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                    # Process already gone, no access, or connection info unavailable - this is fine
                    continue
            
            if killed_any:
                self.log_message("✅ Process cleanup completed")
            
        except Exception as e:
            # Only log if it's a significant error, not just cleanup issues
            if "No such process" not in str(e) and "Access denied" not in str(e):
                self.log_message(f"⚠️ Note: Some processes may still be running: {str(e)}")
    
    def start_setup(self):
        """Start the setup process"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run setup in separate thread
        thread = threading.Thread(target=self.run_setup)
        thread.daemon = True
        thread.start()
    
    def run_setup(self):
        """Run the actual setup process"""
        try:
            self.update_status("Starting installation...")
            self.log_message("🚀 Starting Instagram Auto Poster setup...")
            self.log_message(f"📁 App directory: {self.app_dir}")
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # Determine setup script
            if platform.system() == "Windows":
                setup_script = "setup_noninteractive.bat"
            else:
                setup_script = "./setup_noninteractive.sh"
            
            self.log_message(f"🔧 Running setup script: {setup_script}")
            self.update_status("Installing Python and dependencies...")
            
            # Run setup process
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    setup_script,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    shell=True,
                    cwd=self.app_dir
                )
            else:
                process = subprocess.Popen(
                    ["bash", setup_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.app_dir
                )
            
            # Read output line by line
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Filter and format output
                    if "INFO" in line or "SUCCESS" in line:
                        self.log_message(f"✅ {line}")
                    elif "WARNING" in line:
                        self.log_message(f"⚠️ {line}")
                    elif "ERROR" in line:
                        self.log_message(f"❌ {line}")
                    else:
                        self.log_message(line)
                    
                    # Update status based on content
                    if "python" in line.lower():
                        self.update_status("Setting up Python...")
                    elif "pip" in line.lower() or "install" in line.lower():
                        self.update_status("Installing dependencies...")
                    elif "chrome" in line.lower():
                        self.update_status("Checking Chrome installation...")
                    elif "virtual" in line.lower():
                        self.update_status("Creating virtual environment...")
            
            process.wait()
            
            if process.returncode == 0:
                self.setup_complete = True
                self.update_status("✅ Setup completed successfully!")
                self.log_message("🎉 Setup completed successfully!")
                self.log_message("🌐 You can now access the app at: http://localhost:5003")
                
                # Update UI for launch mode
                self.action_button.config(
                    text="Launch App",
                    bg="#2196f3",
                    command=self.launch_app,
                    state="normal"
                )
                
                # Auto-launch the app after setup
                self.log_message("🚀 Auto-launching application...")
                time.sleep(1)
                self.launch_app()
                
            else:
                self.update_status("❌ Setup failed!")
                self.log_message("❌ Setup failed! Please check the errors above.")
                self.action_button.config(state="normal")
                messagebox.showerror(
                    "Setup Failed",
                    "Setup encountered errors. Please check the log for details."
                )
        
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            self.action_button.config(state="normal")
            messagebox.showerror("Error", f"Setup failed with error:\n{str(e)}")
        
        finally:
            self.progress.stop()
    
    def launch_app(self):
        """Launch the application"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run launch in separate thread
        thread = threading.Thread(target=self.run_launch)
        thread.daemon = True
        thread.start()
    
    def run_launch(self):
        """Run the actual launch process"""
        try:
            self.update_status("Launching application...")
            self.log_message("🚀 Launching Instagram Auto Poster...")
            
            # Stop existing server if running
            self.find_and_kill_processes()
            time.sleep(2)
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # Determine start script
            if platform.system() == "Windows":
                start_script = "start_noninteractive.bat"
            else:
                start_script = "./start_noninteractive.sh"
            
            self.log_message(f"▶️ Running: {start_script}")
            self.update_status("Starting web server...")
            
            # Start the application process
            if platform.system() == "Windows":
                # Use creationflags to create new process group
                self.server_process = subprocess.Popen(
                    start_script,
                    shell=True,
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Use new process group for Unix systems
                self.server_process = subprocess.Popen(
                    ["bash", start_script],
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid
                )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running (didn't crash immediately)
            if self.server_process.poll() is None:
                self.update_status("✅ Application launched!")
                self.update_server_status(True)
                self.log_message("✅ Application launched successfully!")
                self.log_message("🌐 Opening browser to: http://localhost:5003")
                
                # Try to open browser
                try:
                    import webbrowser
                    webbrowser.open("http://localhost:5003")
                except:
                    pass
                
                messagebox.showinfo(
                    "App Launched!",
                    "Instagram Auto Poster is now running!\n\n" +
                    "The web interface should open automatically.\n" +
                    "If not, go to: http://localhost:5003\n\n" +
                    "Use 'Stop Server' button to stop the application."
                )
            else:
                self.update_status("❌ Application failed to start!")
                self.log_message("❌ Application failed to start!")
                # Read any error output
                if self.server_process.stdout:
                    output = self.server_process.stdout.read()
                    self.log_message(f"Error output: {output}")
                
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to launch app:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.action_button.config(state="normal")
    
    def stop_server(self):
        """Stop the server process"""
        try:
            self.log_message("🛑 Stopping server...")
            
            # Kill all processes related to our app
            self.find_and_kill_processes()
            
            # Also terminate our tracked process if it exists
            if self.server_process and self.server_process.poll() is None:
                if platform.system() == "Windows":
                    # On Windows, send CTRL_BREAK_EVENT to the process group
                    try:
                        self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
                        self.server_process.wait(timeout=3)
                    except:
                        # Force kill the process tree
                        subprocess.run(["taskkill", "/f", "/t", "/pid", str(self.server_process.pid)], 
                                     capture_output=True)
                else:
                    # On Unix-like systems, kill the process group
                    try:
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                        self.server_process.wait(timeout=3)
                    except:
                        # Force kill if it doesn't respond
                        try:
                            os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                        except:
                            pass
                
                self.server_process = None
            
            self.update_server_status(False)
            self.log_message("✅ Server stopped successfully!")
            self.update_status("Server stopped")
            
        except Exception as e:
            self.log_message(f"⚠️ Error stopping server: {str(e)}")
    
    def open_app_folder(self):
        """Open the application folder"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.app_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.app_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.app_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
    
    def on_closing(self):
        """Handle window close event"""
        should_stop_server = False
        
        if self.server_running:
            result = messagebox.askyesno(
                "Server Running", 
                "The Instagram Auto Poster server is still running.\n\n" +
                "Do you want to stop the server before closing?"
            )
            if result:  # User clicked Yes
                should_stop_server = True
                self.stop_server()
                time.sleep(2)
                # Final cleanup - kill any remaining processes
                self.find_and_kill_processes()
            else:  # User clicked No
                self.log_message("✅ Server will continue running in background")
        else:
            # No server running, safe to do cleanup
            self.find_and_kill_processes()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

    def open_browser(self):
        """Open browser to running app"""
        try:
            import webbrowser
            webbrowser.open("http://localhost:5003")
            self.log_message("🌐 Opened browser to: http://localhost:5003")
        except Exception as e:
            self.log_message(f"❌ Failed to open browser: {str(e)}")
            messagebox.showerror("Error", f"Could not open browser:\n{str(e)}")

    def toggle_auto_startup(self):
        """Toggle auto-startup functionality"""
        if self.is_auto_startup_enabled():
            self.disable_auto_startup()
        else:
            self.enable_auto_startup()
    
    def is_auto_startup_enabled(self):
        """Check if auto-startup is currently enabled"""
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_READ)
                try:
                    winreg.QueryValueEx(key, "InstagramAutoPoster")
                    winreg.CloseKey(key)
                    return True
                except FileNotFoundError:
                    winreg.CloseKey(key)
                    return False
            
            elif platform.system() == "Darwin":  # macOS
                plist_path = Path.home() / "Library/LaunchAgents/com.instagramautoposter.startup.plist"
                return plist_path.exists()
            
            else:  # Linux
                desktop_path = Path.home() / ".config/autostart/InstagramAutoPoster.desktop"
                return desktop_path.exists()
        except:
            return False
    
    def enable_auto_startup(self):
        """Enable auto-startup on system boot"""
        try:
            app_path = str(self.app_dir.parent.absolute())
            
            if platform.system() == "Windows":
                self.enable_windows_startup(app_path)
            elif platform.system() == "Darwin":
                self.enable_macos_startup(app_path)
            else:
                self.enable_linux_startup(app_path)
            
            self.startup_button.config(
                text="Disable Auto-Startup",
                bg="#f44336"
            )
            self.log_message("✅ Auto-startup enabled! App will start on system boot.")
            messagebox.showinfo(
                "Auto-Startup Enabled",
                "Instagram Auto Poster will now start automatically when your computer boots!\n\n" +
                "The app will launch minimized in the background.\n" +
                "Access it at: http://localhost:5003"
            )
            
        except Exception as e:
            self.log_message(f"❌ Failed to enable auto-startup: {str(e)}")
            messagebox.showerror("Error", f"Failed to enable auto-startup:\n{str(e)}")
    
    def disable_auto_startup(self):
        """Disable auto-startup on system boot"""
        try:
            if platform.system() == "Windows":
                self.disable_windows_startup()
            elif platform.system() == "Darwin":
                self.disable_macos_startup()
            else:
                self.disable_linux_startup()
            
            self.startup_button.config(
                text="Enable Auto-Startup",
                bg="#9c27b0"
            )
            self.log_message("✅ Auto-startup disabled.")
            messagebox.showinfo("Auto-Startup Disabled", "Auto-startup has been disabled.")
            
        except Exception as e:
            self.log_message(f"❌ Failed to disable auto-startup: {str(e)}")
            messagebox.showerror("Error", f"Failed to disable auto-startup:\n{str(e)}")
    
    def enable_windows_startup(self, app_path):
        """Enable Windows startup via registry"""
        import winreg
        
        # Create startup script
        startup_script = Path(app_path) / "startup_silent.bat"
        startup_script.write_text(f'''@echo off
cd /d "{app_path}"
start /min python gui_installer.py --auto-launch
''', encoding='utf-8')
        
        # Add to Windows startup registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "InstagramAutoPoster", 0, winreg.REG_SZ, str(startup_script))
        winreg.CloseKey(key)
    
    def disable_windows_startup(self):
        """Disable Windows startup"""
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "InstagramAutoPoster")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    
    def enable_macos_startup(self, app_path):
        """Enable macOS startup via LaunchAgent"""
        plist_dir = Path.home() / "Library/LaunchAgents"
        plist_dir.mkdir(exist_ok=True)
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.instagramautoposter.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{app_path}/gui_installer.py</string>
        <string>--auto-launch</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{app_path}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/instagram_auto_poster.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/instagram_auto_poster_error.log</string>
</dict>
</plist>'''
        
        plist_path = plist_dir / "com.instagramautoposter.startup.plist"
        plist_path.write_text(plist_content, encoding='utf-8')
        
        # Load the launch agent
        subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
    
    def disable_macos_startup(self):
        """Disable macOS startup"""
        plist_path = Path.home() / "Library/LaunchAgents/com.instagramautoposter.startup.plist"
        if plist_path.exists():
            # Unload the launch agent
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink()
    
    def enable_linux_startup(self, app_path):
        """Enable Linux startup via autostart desktop file"""
        autostart_dir = Path.home() / ".config/autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f'''[Desktop Entry]
Name=Instagram Auto Poster
Comment=Auto-start Instagram Auto Poster
Type=Application
Exec=python3 "{app_path}/gui_installer.py" --auto-launch
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
        
        desktop_path = autostart_dir / "InstagramAutoPoster.desktop"
        desktop_path.write_text(desktop_content, encoding='utf-8')
        desktop_path.chmod(0o755)
    
    def disable_linux_startup(self):
        """Disable Linux startup"""
        desktop_path = Path.home() / ".config/autostart/InstagramAutoPoster.desktop"
        if desktop_path.exists():
            desktop_path.unlink()

    def update_startup_button(self):
        """Update auto-startup button status"""
        if self.is_auto_startup_enabled():
            self.startup_button.config(
                text="Disable Auto-Startup",
                bg="#f44336"
            )
        else:
            self.startup_button.config(
                text="Enable Auto-Startup",
                bg="#9c27b0"
            )

    def handle_auto_launch(self):
        """Handle auto-launch mode"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run auto-launch in separate thread
        thread = threading.Thread(target=self.run_auto_launch)
        thread.daemon = True
        thread.start()
    
    def run_auto_launch(self):
        """Run the actual auto-launch process"""
        try:
            self.update_status("Launching application...")
            self.log_message("🚀 Launching Instagram Auto Poster...")
            
            # Stop existing server if running
            self.find_and_kill_processes()
            time.sleep(2)
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # Determine start script
            if platform.system() == "Windows":
                start_script = "start_noninteractive.bat"
            else:
                start_script = "./start_noninteractive.sh"
            
            self.log_message(f"▶️ Running: {start_script}")
            self.update_status("Starting web server...")
            
            # Start the application process
            if platform.system() == "Windows":
                # Use creationflags to create new process group
                self.server_process = subprocess.Popen(
                    start_script,
                    shell=True,
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Use new process group for Unix systems
                self.server_process = subprocess.Popen(
                    ["bash", start_script],
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid
                )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running (didn't crash immediately)
            if self.server_process.poll() is None:
                self.update_status("✅ Application launched!")
                self.update_server_status(True)
                self.log_message("✅ Application launched successfully!")
                self.log_message("🌐 Opening browser to: http://localhost:5003")
                
                # Try to open browser
                try:
                    import webbrowser
                    webbrowser.open("http://localhost:5003")
                except:
                    pass
                
                messagebox.showinfo(
                    "App Launched!",
                    "Instagram Auto Poster is now running!\n\n" +
                    "The web interface should open automatically.\n" +
                    "If not, go to: http://localhost:5003\n\n" +
                    "Use 'Stop Server' button to stop the application."
                )
            else:
                self.update_status("❌ Application failed to start!")
                self.log_message("❌ Application failed to start!")
                # Read any error output
                if self.server_process.stdout:
                    output = self.server_process.stdout.read()
                    self.log_message(f"Error output: {output}")
                
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to launch app:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.action_button.config(state="normal")

if __name__ == "__main__":
    app = InstagramAutoPoserInstaller()
    app.run()
