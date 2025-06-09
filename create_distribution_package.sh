#!/bin/bash

# Instagram Auto Poster - Distribution Package Creator
# This script creates complete packages for Windows, macOS, and Linux

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=============================================="
echo "   Instagram Auto Poster - Package Creator"
echo "=============================================="
echo ""

# Get current directory and create package directory
CURRENT_DIR="$(pwd)"
PACKAGE_DIR="Instagram_Auto_Poster_Package"
APP_DIR="$PACKAGE_DIR/InstagramAutoPoster"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

print_status "Creating distribution package with clean structure..."

# Clean and create package directory
if [[ -d "$PACKAGE_DIR" ]]; then
    rm -rf "$PACKAGE_DIR"
fi
mkdir -p "$PACKAGE_DIR"
mkdir -p "$APP_DIR"

# Core application files to include (go in subfolder)
CORE_FILES=(
    "app.py"
    "instagram_poster.py"
    "requirements.txt"
    "setup_integration.py"
    "setup_chrome.py"
    "vnc_setup.py"
    "run_scheduler.py"
    "test_setup.py"
    "troubleshoot_chrome.py"
    ".env.example"
)

# Setup scripts (go in subfolder)
SETUP_SCRIPTS=(
    "setup.sh"
    "setup.bat"
    "start.sh" 
    "start.bat"
    "create_launchers.sh"
    "create_simple_mac_launchers.sh"
)

# Documentation files (go in subfolder)
DOC_FILES=(
    "README.md"
    "SETUP_README.md"
)

# Directories to include (go in subfolder)
DIRECTORIES=(
    "templates"
    "static"
    "content"
)

print_status "Copying core application files to InstagramAutoPoster/..."
for file in "${CORE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$APP_DIR/"
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying setup scripts to InstagramAutoPoster/..."
for file in "${SETUP_SCRIPTS[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$APP_DIR/"
        chmod +x "$APP_DIR/$file" 2>/dev/null || true
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying documentation to InstagramAutoPoster/..."
for file in "${DOC_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$APP_DIR/"
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying directories to InstagramAutoPoster/..."
for dir in "${DIRECTORIES[@]}"; do
    if [[ -d "$dir" ]]; then
        cp -r "$dir" "$APP_DIR/"
        print_status "  ✓ $dir/"
    else
        print_warning "  ⚠ $dir/ not found - creating empty directory"
        mkdir -p "$APP_DIR/$dir"
    fi
done

# Create launchers in main package folder
print_status "Creating platform-specific launchers in main folder..."

cd "$PACKAGE_DIR"

# Create macOS .command files
print_status "Creating macOS .command launchers..."

cat > "Instagram Setup.command" << 'EOF'
#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/InstagramAutoPoster"

# Change to the app directory
cd "$APP_DIR"

# Check if setup.sh exists
if [[ ! -f "setup.sh" ]]; then
    echo "ERROR: setup.sh not found in $APP_DIR"
    echo "Please make sure the InstagramAutoPoster folder is present."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the setup script
echo "Starting Instagram Auto Poster setup..."
echo "App directory: $APP_DIR"
echo ""

./setup.sh

# Keep terminal open
echo ""
echo "Setup script finished."
read -p "Press Enter to close this window..."
EOF

cat > "Instagram Start.command" << 'EOF'
#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/InstagramAutoPoster"

# Change to the app directory
cd "$APP_DIR"

# Check if start.sh exists
if [[ ! -f "start.sh" ]]; then
    echo "ERROR: start.sh not found in $APP_DIR"
    echo "Please make sure the InstagramAutoPoster folder is present."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the start script
echo "Starting Instagram Auto Poster..."
echo "App directory: $APP_DIR"
echo ""

./start.sh

# Keep terminal open if there was an error
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Start script finished with an error."
    read -p "Press Enter to close this window..."
fi
EOF

chmod +x "Instagram Setup.command"
chmod +x "Instagram Start.command"
print_success "  ✓ macOS .command files created"

# Create Windows .bat files
print_status "Creating Windows .bat launchers..."

cat > "Instagram Setup.bat" << 'EOF'
@echo off
title Instagram Auto Poster - Setup
cls

cd /d "%~dp0InstagramAutoPoster"

if not exist "setup.bat" (
    echo ERROR: setup.bat not found in InstagramAutoPoster folder
    echo Please make sure the InstagramAutoPoster folder is present.
    pause
    exit /b 1
)

echo Starting Instagram Auto Poster setup...
echo App directory: %CD%
echo.

call setup.bat

echo.
echo Setup finished.
pause
EOF

cat > "Instagram Start.bat" << 'EOF'
@echo off
title Instagram Auto Poster - Start
cls

cd /d "%~dp0InstagramAutoPoster"

if not exist "start.bat" (
    echo ERROR: start.bat not found in InstagramAutoPoster folder
    echo Please make sure the InstagramAutoPoster folder is present.
    pause
    exit /b 1
)

echo Starting Instagram Auto Poster...
echo App directory: %CD%
echo.

call start.bat

if %errorlevel% neq 0 (
    echo.
    echo Start script finished with an error.
    pause
)
EOF

print_success "  ✓ Windows .bat files created"

# Create Linux .desktop files
print_status "Creating Linux .desktop launchers..."

cat > "Instagram Setup.desktop" << 'EOF'
[Desktop Entry]
Name=Instagram Auto Poster - Setup
Comment=Instagram Auto Poster - One-time Setup
Exec=bash -c "cd '%k/InstagramAutoPoster' && ./setup.sh; read -p 'Press Enter to close...'"
Icon=system-software-install
Type=Application
Terminal=true
Categories=Development;
EOF

cat > "Instagram Start.desktop" << 'EOF'
[Desktop Entry]
Name=Instagram Auto Poster - Start
Comment=Instagram Auto Poster - Quick Start
Exec=bash -c "cd '%k/InstagramAutoPoster' && ./start.sh; read -p 'Press Enter to close...'"
Icon=media-playback-start
Type=Application
Terminal=true
Categories=Development;
EOF

chmod +x *.desktop
print_success "  ✓ Linux .desktop files created"

# Create comprehensive README for main folder
cat > "USER_GUIDE.md" << 'EOF'
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
EOF

cd "$CURRENT_DIR"

# Create archive
print_status "Creating distribution archive..."

if command -v zip >/dev/null 2>&1; then
    ARCHIVE_NAME="Instagram_Auto_Poster_${TIMESTAMP}.zip"
    zip -r "$ARCHIVE_NAME" "$PACKAGE_DIR" > /dev/null
    print_success "Created ZIP archive: $ARCHIVE_NAME"
elif command -v tar >/dev/null 2>&1; then
    ARCHIVE_NAME="Instagram_Auto_Poster_${TIMESTAMP}.tar.gz"
    tar -czf "$ARCHIVE_NAME" "$PACKAGE_DIR"
    print_success "Created TAR.GZ archive: $ARCHIVE_NAME"
else
    print_warning "No archive tool found - distribution folder ready: $PACKAGE_DIR"
    ARCHIVE_NAME="$PACKAGE_DIR"
fi

# Create file list
print_status "Creating file inventory..."
find "$PACKAGE_DIR" -type f | sort > "${PACKAGE_DIR}_file_list.txt"

echo ""
echo "=============================================="
print_success "🎉 Distribution package created successfully!"
echo "=============================================="
echo ""
print_status "Package structure:"
echo "  📁 $PACKAGE_DIR/ (main folder - contains only launchers)"
echo "    📱 Instagram Setup.command (macOS)"
echo "    📱 Instagram Start.command (macOS)"
echo "    🪟 Instagram Setup.bat (Windows)"
echo "    🪟 Instagram Start.bat (Windows)"
echo "    🐧 Instagram Setup.desktop (Linux)"
echo "    🐧 Instagram Start.desktop (Linux)"
echo "    📄 USER_GUIDE.md"
echo "    📁 InstagramAutoPoster/ (all application files)"
if [[ "$ARCHIVE_NAME" != "$PACKAGE_DIR" ]]; then
    echo "  📦 $ARCHIVE_NAME (compressed archive)"
fi
echo "  📄 ${PACKAGE_DIR}_file_list.txt (file inventory)"
echo ""
print_status "What users see:"
echo "  1. Clean main folder with just the launchers they need"
echo "  2. All technical files hidden in InstagramAutoPoster subfolder"
echo "  3. Clear USER_GUIDE.md with simple instructions"
echo ""
print_success "Ready to distribute! 🚀"
echo "==============================================" 