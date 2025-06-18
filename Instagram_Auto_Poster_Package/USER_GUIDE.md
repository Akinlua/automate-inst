# Instagram Auto Poster - User Guide

Welcome! This package provides a modern, user-friendly way to install and run the Instagram Auto Poster.

## 🚀 Quick Start - One Click Setup!

### 🪟 Windows Users
**Double-click:** `Instagram Auto Poster.bat`

### 🍎 macOS Users  
**Double-click:** `Instagram Auto Poster.command`
- *Note: Right-click → Open on first use for security*

### 🐧 Linux Users
**Double-click:** `Instagram Auto Poster.desktop`

## ⚡ Auto-Startup Feature (NEW!)

Want the Instagram Auto Poster to start automatically when your computer boots? 

1. **Launch the installer** (double-click the launcher for your OS)
2. **Click "Enable Auto-Startup"** button in the installer window
3. **Done!** The app will now start automatically every time you boot your computer

### How Auto-Startup Works
- 🔄 **Windows**: Adds entry to Windows startup registry
- 🍎 **macOS**: Creates a LaunchAgent that starts with your user session
- 🐧 **Linux**: Adds desktop file to autostart directory

### Managing Auto-Startup
- **Enable**: Click "Enable Auto-Startup" (purple button)
- **Disable**: Click "Disable Auto-Startup" (red button)
- **Status**: Button color shows current state

## ✨ What You'll See

When you double-click the launcher, you'll see a beautiful, modern installer window that:

- 🎯 **No Scary Terminal**: Clean, graphical interface
- 📊 **Progress Tracking**: Real-time installation progress
- 🔄 **Auto-Detection**: Knows if it's first-time setup or app launch
- ⚡ **One-Click Setup**: Installs everything automatically
- 🌐 **Auto-Launch**: Opens your browser to the app when ready
- 🚀 **Auto-Startup**: Can start with your computer (optional)

## 📁 Folder Structure

```
Instagram_Auto_Poster_Package/
├── Instagram Auto Poster.bat      (Windows GUI launcher)
├── Instagram Auto Poster.command  (macOS GUI launcher)  
├── Instagram Auto Poster.desktop  (Linux launcher)
├── gui_installer.py               (Modern GUI installer)
├── USER_GUIDE.md                  (this file)
└── InstagramAutoPoster/           (application files)
    ├── app.py                     (main application)
    ├── setup.sh                   (setup script)
    ├── start.sh                   (start script)
    └── [all other files...]
```

## 🎯 Installation Process

The modern installer automatically:

1. **🔍 Detects Your System**: Windows, macOS, or Linux
2. **🐍 Installs Python**: If not already installed (3.8+)
3. **📦 Creates Environment**: Isolated virtual environment
4. **⬇️ Downloads Dependencies**: All required packages
5. **🏗️ Sets Up Folders**: Creates necessary directories
6. **🌐 Checks Chrome**: Verifies browser installation
7. **🚀 Launches App**: Opens web interface automatically

## 📱 After Installation

1. **Web Interface**: Automatically opens at `http://localhost:5003`
2. **Setup Chrome**: Click the setup button in the web interface
3. **Upload Content**: Add your images and captions to the `content` folder
4. **Configure Schedule**: Set your posting preferences
5. **Start Posting**: Enable scheduler or post manually
6. **Auto-Startup** (Optional): Click "Enable Auto-Startup" for boot-time launching

## 🔧 Requirements

- **Google Chrome** (install from https://google.com/chrome)
- **Internet Connection** (for downloading dependencies)
- **Python 3.8+** (installed automatically if missing)

## 🆘 Troubleshooting

### Common Solutions
- **Permission Issues**: Right-click → "Open" or "Run as Administrator"
- **Chrome Not Found**: Install from https://google.com/chrome
- **Port 5003 Busy**: The installer will show instructions to change the port
- **Auto-Startup Not Working**: Make sure you have user permissions for startup entries

### First-Time Setup
1. The installer window will show "Start Setup" - click it
2. Wait for the automated installation (3-5 minutes)
3. Click "Launch App" when setup completes
4. Your browser opens to the app automatically
5. Optionally click "Enable Auto-Startup" for automatic boot-time launching

### Subsequent Uses
1. The installer window will show "Launch App" directly
2. Click it to start the application
3. Your browser opens to the app automatically

### Auto-Startup Management
- **Enable**: Purple "Enable Auto-Startup" button
- **Disable**: Red "Disable Auto-Startup" button
- **Check Status**: Button color indicates current state
- **Troubleshoot**: Auto-startup runs silently in background

## ⚠️ Important Notes

- **Educational Use Only**: Follow Instagram's Terms of Service
- **Responsible Usage**: Don't spam or violate platform rules
- **Chrome Required**: Must be installed separately
- **Internet Required**: For initial dependency downloads
- **Auto-Startup**: Runs in background - access via http://localhost:5003

## 🎉 Modern Features

- **🖥️ Native Look**: Matches your operating system's style
- **📈 Progress Bars**: See installation progress in real-time
- **💬 Clear Messages**: No confusing technical jargon
- **🎯 Smart Detection**: Knows what to do automatically
- **🌐 Auto-Browser**: Opens the app in your browser automatically
- **🚀 Auto-Startup**: Start with computer boot (optional)
- **⚡ Background Mode**: Runs silently when auto-started

## 🔄 Auto-Startup Behavior

When auto-startup is enabled:
- **Silent Launch**: Starts automatically without showing installer window
- **Background Running**: Runs in system background
- **Immediate Access**: Available at http://localhost:5003 right after boot
- **No Interruption**: Doesn't interfere with your normal startup routine
- **Easy Disable**: Use the installer to disable anytime

---

**Ready to start? Just double-click the launcher for your operating system! 🚀**

*No terminals, no command lines, no confusion - just click and go!* ✨

**Want auto-startup? Click "Enable Auto-Startup" in the installer!** 🔄
