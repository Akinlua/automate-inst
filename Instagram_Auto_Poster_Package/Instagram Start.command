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
