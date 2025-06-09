#!/bin/bash

# Instagram Auto Poster - Quick Start Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=============================================="
echo "   Instagram Auto Poster - Quick Start"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Please run ./setup.sh first to complete the initial setup."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Start the application
echo ""
echo -e "${GREEN}Starting Instagram Auto Poster...${NC}"
echo ""
echo -e "${GREEN}Open your browser and go to: http://localhost:5000${NC}"
echo ""
echo "Press Ctrl+C to stop the application."
echo ""

python app.py 