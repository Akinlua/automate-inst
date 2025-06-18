#!/bin/bash

# Simple macOS Launcher Creator - Creates .command files instead of .app bundles
# .command files are more reliable and don't have app translocation issues

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
echo "   Simple macOS Launcher Creator"
echo "=============================================="
echo ""

# Get current directory
DIR="$(cd "$(dirname "$0")" && pwd)"

# Create Instagram Setup Launcher
if [[ -f "setup.sh" ]]; then
    print_status "Creating Instagram Setup.command..."
    
    cat <<'EOF' > "Instagram Setup.command"
#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if setup.sh exists
if [[ ! -f "setup.sh" ]]; then
    echo "ERROR: setup.sh not found in $SCRIPT_DIR"
    echo "Please make sure all files are in the same folder."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the setup script
echo "Starting Instagram Auto Poster setup..."
echo "Current directory: $SCRIPT_DIR"
echo ""

./setup.sh

# Keep terminal open
echo ""
echo "Setup script finished."
read -p "Press Enter to close this window..."
EOF
    
    chmod +x "Instagram Setup.command"
    print_success "Created Instagram Setup.command"
fi

# Create Instagram Start Launcher
if [[ -f "start.sh" ]]; then
    print_status "Creating Instagram Start.command..."
    
    cat <<'EOF' > "Instagram Start.command"
#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if start.sh exists
if [[ ! -f "start.sh" ]]; then
    echo "ERROR: start.sh not found in $SCRIPT_DIR"
    echo "Please make sure all files are in the same folder."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the start script
echo "Starting Instagram Auto Poster..."
echo "Current directory: $SCRIPT_DIR"
echo ""

./start.sh

# Keep terminal open if there was an error
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Start script finished with an error."
    read -p "Press Enter to close this window..."
fi
EOF
    
    chmod +x "Instagram Start.command"
    print_success "Created Instagram Start.command"
fi

echo ""
print_success "Simple macOS launchers created successfully!"
print_status "Users can double-click the .command files to run the application"
print_warning "Note: Users may need to right-click → Open on first use for security"
echo "" 