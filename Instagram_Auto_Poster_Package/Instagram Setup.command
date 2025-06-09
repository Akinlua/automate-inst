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
