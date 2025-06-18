#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Function to find Python
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            echo "$cmd"
            return 0
        fi
    done
    return 1
}

# Try to find Python
PYTHON_CMD=$(find_python)

if [[ -z "$PYTHON_CMD" ]]; then
    echo "Python not found. Please install Python from https://python.org"
    echo "Press Enter to open Python download page..."
    read
    open "https://python.org/downloads"
    exit 1
fi

echo "Starting Instagram Auto Poster..."
"$PYTHON_CMD" gui_installer.py

# Keep terminal open if there was an error
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Failed to start the installer."
    read -p "Press Enter to close..."
fi
