# Instagram Auto Poster - User Guide

Welcome! This package contains everything needed to run the Instagram Auto Poster.

## Quick Start by Operating System

### 🪟 Windows Users
1. **First Time**: Double-click `Instagram Setup.bat`
2. **Subsequent Uses**: Double-click `Instagram Start.bat`

### 🍎 macOS Users  
1. **First Time**: Double-click `Instagram Setup.command`
2. **Subsequent Uses**: Double-click `Instagram Start.command`
   - *Note: Right-click → Open on first use for security*

### 🐧 Linux Users
1. **First Time**: Double-click `Instagram Setup.desktop`
2. **Subsequent Uses**: Double-click `Instagram Start.desktop`
   - *Alternative: Open terminal in InstagramAutoPoster folder and run `./setup.sh` then `./start.sh`*

## Folder Structure

```
Instagram_Auto_Poster_Package/
├── Instagram Setup.command     (macOS setup launcher)
├── Instagram Start.command     (macOS start launcher)
├── Instagram Setup.bat         (Windows setup launcher)
├── Instagram Start.bat         (Windows start launcher)
├── Instagram Setup.desktop     (Linux setup launcher)
├── Instagram Start.desktop     (Linux start launcher)
├── USER_GUIDE.md              (this file)
└── InstagramAutoPoster/       (application files)
    ├── app.py                 (main application)
    ├── setup.sh               (setup script)
    ├── start.sh               (start script)
    ├── setup.bat              (Windows setup)
    ├── start.bat              (Windows start)
    └── [all other files...]
```

## What Happens During Setup

The setup process automatically:
- ✅ Installs Python 3.8+ (including Python 3.13)
- ✅ Creates isolated virtual environment
- ✅ Installs all required dependencies
- ✅ Creates necessary folders
- ✅ Checks for Google Chrome
- ✅ Starts the web application

## After Setup

1. **Web Interface**: Opens at `http://localhost:5003`
2. **Setup Chrome Profile**: Click the setup button in the web interface
3. **Upload Content**: Add your images and captions
4. **Configure Schedule**: Set your posting preferences
5. **Start Posting**: Enable scheduler or post manually

## Requirements

- **Google Chrome** (must be installed manually)
- **Internet connection** (for dependencies)
- **Python 3.8+** (installed automatically)

## Troubleshooting

### Common Issues
- **Permission Denied (Linux/macOS)**: Right-click → Open on first use
- **Chrome Not Found**: Install from https://google.com/chrome
- **Port 5003 Busy**: Edit `InstagramAutoPoster/app.py` and change port number

### Getting Help
1. Check `InstagramAutoPoster/README.md` for detailed instructions
2. Run `python InstagramAutoPoster/test_setup.py` to verify installation
3. Check console output for error messages

## Important Notes

- ⚠️ For educational purposes only
- ⚠️ Comply with Instagram's Terms of Service
- ⚠️ Use responsibly and ethically

---
**Ready to start? Just double-click the appropriate setup file for your operating system! 🚀**
