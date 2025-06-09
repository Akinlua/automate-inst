#!/bin/bash

# Instagram Auto Poster - Package Creation Script
# This script creates a clean distribution package

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

# Check if we're in the right directory
if [[ ! -f "app.py" ]] || [[ ! -f "instagram_poster.py" ]]; then
    print_error "Not in the correct directory. Please run from the project root."
    exit 1
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x setup.sh start.sh

# Create package directory
PACKAGE_DIR="instagram_auto_poster_package"
print_status "Creating package directory: $PACKAGE_DIR"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Files to include
print_status "Copying core files..."

# Core application files
cp app.py "$PACKAGE_DIR/"
cp instagram_poster.py "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp setup_integration.py "$PACKAGE_DIR/"
cp vnc_setup.py "$PACKAGE_DIR/"
cp run_scheduler.py "$PACKAGE_DIR/"

# Setup scripts
cp setup.bat "$PACKAGE_DIR/"
cp setup.sh "$PACKAGE_DIR/"
cp start.bat "$PACKAGE_DIR/"
cp start.sh "$PACKAGE_DIR/"

# Make scripts executable in package
chmod +x "$PACKAGE_DIR/setup.sh"
chmod +x "$PACKAGE_DIR/start.sh"

# Configuration files
if [[ -f ".env.example" ]]; then
    cp .env.example "$PACKAGE_DIR/"
fi

if [[ -f "scheduler_settings.json" ]]; then
    cp scheduler_settings.json "$PACKAGE_DIR/"
fi

# Documentation
cp README.md "$PACKAGE_DIR/"
cp SETUP_README.md "$PACKAGE_DIR/"
cp DISTRIBUTION_FILES.md "$PACKAGE_DIR/"

# Test script
cp test_setup.py "$PACKAGE_DIR/"

# Web interface files
print_status "Copying web interface files..."
if [[ -d "templates" ]]; then
    cp -r templates "$PACKAGE_DIR/"
fi

if [[ -d "static" ]]; then
    cp -r static "$PACKAGE_DIR/"
fi

# Create empty content directory structure
print_status "Creating content directory structure..."
mkdir -p "$PACKAGE_DIR/content"

# Create sample month folders (empty)
for i in {1..12}; do
    mkdir -p "$PACKAGE_DIR/content/$i"
done

# Create a basic .env file if .env.example doesn't exist
if [[ ! -f "$PACKAGE_DIR/.env.example" ]]; then
    print_status "Creating .env.example..."
    cat > "$PACKAGE_DIR/.env.example" << EOF
# Instagram Auto Poster Configuration
CONTENT_DIR=content
USE_CHATGPT=false
OPENAI_API_KEY=
CHROME_PROFILE_PATH=
CHROME_USER_DATA_DIR=
CHROME_PROFILE_NAME=InstagramBot
EOF
fi

# Create ZIP package
PACKAGE_NAME="instagram_auto_poster_v$(date +%Y%m%d_%H%M%S).zip"
print_status "Creating ZIP package: $PACKAGE_NAME"

cd "$PACKAGE_DIR"
zip -r "../$PACKAGE_NAME" .
cd ..

# Verify package
print_status "Verifying package contents..."
unzip -l "$PACKAGE_NAME" | head -20

# Get package size
PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)

print_success ""
print_success "=============================================="
print_success "   Package Created Successfully!"
print_success "=============================================="
print_success ""
print_success "Package: $PACKAGE_NAME"
print_success "Size: $PACKAGE_SIZE"
print_success "Location: $(pwd)/$PACKAGE_NAME"
print_success ""
print_success "The package includes:"
print_success "• Setup scripts for Windows and Linux/macOS"
print_success "• Complete web application"
print_success "• All required Python files"
print_success "• Documentation and examples"
print_success "• Empty content folder structure"
print_success ""
print_success "Users can simply:"
print_success "1. Extract the ZIP file"
print_success "2. Run setup.bat (Windows) or ./setup.sh (Linux/macOS)"
print_success "3. Open http://localhost:5000 in their browser"
print_success ""

# Clean up
print_status "Cleaning up temporary directory..."
rm -rf "$PACKAGE_DIR"

print_success "Package creation complete!"

# Optional: Test the package
read -p "Do you want to test the package in a temporary directory? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    TEST_DIR="test_package_$(date +%s)"
    print_status "Creating test directory: $TEST_DIR"
    mkdir "$TEST_DIR"
    cd "$TEST_DIR"
    
    print_status "Extracting package for testing..."
    unzip "../$PACKAGE_NAME"
    
    print_status "Running test script..."
    if [[ -f "test_setup.py" ]]; then
        python3 test_setup.py || true
    fi
    
    cd ..
    print_status "Cleaning up test directory..."
    rm -rf "$TEST_DIR"
    
    print_success "Test complete!"
fi

print_success ""
print_success "Your distribution package is ready: $PACKAGE_NAME"
print_success "You can now share this ZIP file with users!" 