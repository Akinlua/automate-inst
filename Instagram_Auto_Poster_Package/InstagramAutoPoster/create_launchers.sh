#!/bin/bash

# Instagram Auto Poster - Launcher Creator
# This script creates clickable app launchers for both macOS and Linux

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

echo ""
echo "=============================================="
echo "   Instagram Auto Poster - Launcher Creator"
echo "=============================================="
echo ""

# Get current directory
DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    print_status "Detected macOS - Creating .app bundles"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_status "Detected Linux - Creating .desktop launchers"
else
    print_warning "Unknown OS type: $OSTYPE"
    print_warning "This script supports macOS and Linux only"
    print_warning "Windows users can use the .bat files directly"
    exit 1
fi

# Function to create macOS .app bundle
create_macos_app() {
    local app_name="$1"
    local script_name="$2"
    local display_name="$3"
    
    print_status "Creating $app_name.app..."
    
    # Create app structure
    mkdir -p "$app_name.app/Contents/MacOS"
    mkdir -p "$app_name.app/Contents/Resources"
    
    # Copy the actual script into the app bundle
    if [[ -f "$script_name" ]]; then
        cp "$script_name" "$app_name.app/Contents/Resources/$script_name"
        chmod +x "$app_name.app/Contents/Resources/$script_name"
    fi
    
    # Create a launcher script that finds the script in the same directory as the .app
    cat <<'EOF' > "$app_name.app/Contents/MacOS/$app_name"
#!/bin/bash

# Find the directory containing this .app bundle
APP_BUNDLE="$0"
while [ -L "$APP_BUNDLE" ]; do
    DIR="$(cd -P "$(dirname "$APP_BUNDLE")" && pwd)"
    APP_BUNDLE="$(readlink "$APP_BUNDLE")"
    [[ $APP_BUNDLE != /* ]] && APP_BUNDLE="$DIR/$APP_BUNDLE"
done
APP_DIR="$(cd -P "$(dirname "$APP_BUNDLE")" && pwd)"
PARENT_DIR="$(dirname "$APP_DIR")"

# Try to find the script in multiple locations
SCRIPT_NAME="setup.sh"
if [[ "$APP_BUNDLE" == *"Start"* ]]; then
    SCRIPT_NAME="start.sh"
fi

SCRIPT_LOCATIONS=(
    "$PARENT_DIR/$SCRIPT_NAME"
    "$APP_DIR/../Resources/$SCRIPT_NAME"
    "$(dirname "$PARENT_DIR")/$SCRIPT_NAME"
)

FOUND_SCRIPT=""
for location in "${SCRIPT_LOCATIONS[@]}"; do
    if [[ -f "$location" ]]; then
        FOUND_SCRIPT="$location"
        break
    fi
done

if [[ -n "$FOUND_SCRIPT" ]]; then
    # Get the directory containing the script
    SCRIPT_DIR="$(dirname "$FOUND_SCRIPT")"
    
    # Run the script in Terminal with proper working directory
    osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && ./$SCRIPT_NAME"
end tell
APPLESCRIPT
else
    osascript -e 'display alert "Error" message "Could not find '$SCRIPT_NAME'. Please make sure all files are in the same folder as this app."'
fi
EOF
    
    chmod +x "$app_name.app/Contents/MacOS/$app_name"
    
    # Create Info.plist
    cat <<EOF > "$app_name.app/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$app_name</string>
    <key>CFBundleIdentifier</key>
    <string>com.instagram-autoposter.$app_name</string>
    <key>CFBundleName</key>
    <string>$display_name</string>
    <key>CFBundleDisplayName</key>
    <string>$display_name</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    print_success "Created $app_name.app"
}

# Function to create Linux .desktop launcher
create_linux_desktop() {
    local desktop_name="$1"
    local script_name="$2"
    local display_name="$3"
    local icon_name="$4"
    
    print_status "Creating $desktop_name.desktop..."
    
    cat <<EOF > "$desktop_name.desktop"
[Desktop Entry]
Name=$display_name
Comment=Instagram Auto Poster - $display_name
Exec=bash -c "cd '$DIR' && ./$script_name; read -p 'Press Enter to close...'"
Icon=$icon_name
Type=Application
Terminal=true
Categories=Development;
Path=$DIR
EOF
    
    chmod +x "$desktop_name.desktop"
    
    print_success "Created $desktop_name.desktop"
}

# Check if required scripts exist
if [[ ! -f "setup.sh" ]]; then
    print_warning "setup.sh not found - skipping setup launcher"
    SETUP_EXISTS=false
else
    SETUP_EXISTS=true
    chmod +x setup.sh
fi

if [[ ! -f "start.sh" ]]; then
    print_warning "start.sh not found - skipping start launcher"
    START_EXISTS=false
else
    START_EXISTS=true
    chmod +x start.sh
fi

# Create launchers based on OS
if [[ "$OS" == "macos" ]]; then
    print_status "Creating macOS app bundles..."
    
    if [[ "$SETUP_EXISTS" == true ]]; then
        create_macos_app "Instagram-Setup" "setup.sh" "Instagram Auto Poster - Setup"
    fi
    
    if [[ "$START_EXISTS" == true ]]; then
        create_macos_app "Instagram-Start" "start.sh" "Instagram Auto Poster - Start"
    fi
    
    echo ""
    print_success "macOS app bundles created successfully!"
    print_status "Users can now double-click the .app files to run the application"
    
elif [[ "$OS" == "linux" ]]; then
    print_status "Creating Linux desktop launchers..."
    
    if [[ "$SETUP_EXISTS" == true ]]; then
        create_linux_desktop "Instagram-Setup" "setup.sh" "Instagram Auto Poster - Setup" "system-software-install"
    fi
    
    if [[ "$START_EXISTS" == true ]]; then
        create_linux_desktop "Instagram-Start" "start.sh" "Instagram Auto Poster - Start" "media-playback-start"
    fi
    
    echo ""
    print_success "Linux desktop launchers created successfully!"
    print_status "Users can now double-click the .desktop files to run the application"
    print_status "To install system-wide, copy .desktop files to ~/.local/share/applications/"
fi

# Create usage instructions
cat <<EOF > "LAUNCHER_USAGE.md"
# App Launchers Usage

## For Users

### Windows
- Double-click \`setup.bat\` to install and run
- Double-click \`start.bat\` to start the app (after setup)

### macOS
- Double-click \`Instagram-Setup.app\` to install and run
- Double-click \`Instagram-Start.app\` to start the app (after setup)

### Linux
- Double-click \`Instagram-Setup.desktop\` to install and run
- Double-click \`Instagram-Start.desktop\` to start the app (after setup)
- Or install to applications menu: 
  \`cp *.desktop ~/.local/share/applications/\`

## What Each Launcher Does

### Setup Launchers
- Installs Python if needed
- Creates virtual environment
- Installs all dependencies
- Creates necessary folders
- Starts the web application
- **One-time setup only**

### Start Launchers
- Quickly starts the app if already set up
- Opens web interface at http://localhost:5003
- **Use after initial setup is complete**

## Troubleshooting

If launchers don't work:
1. Make sure all files are in the same folder
2. On Linux: \`chmod +x *.sh *.desktop\`
3. On macOS: Right-click → Open (first time only)

EOF

print_success "Created LAUNCHER_USAGE.md with user instructions"

echo ""
echo "=============================================="
print_success "🎉 All launchers created successfully!"
echo "=============================================="
echo ""
print_status "Files created for distribution:"
if [[ "$OS" == "macos" ]]; then
    echo "  📱 Instagram-Setup.app (one-time setup)"
    echo "  📱 Instagram-Start.app (quick start)"
elif [[ "$OS" == "linux" ]]; then
    echo "  🖥️  Instagram-Setup.desktop (one-time setup)"
    echo "  🖥️  Instagram-Start.desktop (quick start)"
fi
echo "  📄 LAUNCHER_USAGE.md (user instructions)"
echo ""
print_status "Package these files with your application for easy distribution!"
echo "==============================================" 