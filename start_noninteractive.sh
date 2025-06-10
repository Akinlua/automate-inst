#!/bin/bash

# Instagram Auto Poster - Non-Interactive Start Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=============================================="
echo "   Instagram Auto Poster - Starting..."
echo "=============================================="
echo ""

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Please run setup first."
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if app.py exists
if [[ ! -f "app.py" ]]; then
    echo -e "${RED}app.py not found!${NC}"
    echo "Please make sure all application files are in this directory."
    exit 1
fi

# Start the application
echo ""
echo -e "${GREEN}Starting Instagram Auto Poster...${NC}"
echo ""
echo -e "${GREEN}Server will be available at: http://localhost:5003${NC}"
echo ""

# Start the app in the background and capture the PID
python app.py &
APP_PID=$!

# Give it more time to start
echo -e "${BLUE}Waiting for server to initialize...${NC}"
sleep 5

# Check if the process is still running
if kill -0 $APP_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Process started successfully!${NC}"
    echo -e "${GREEN}📍 Server process ID: $APP_PID${NC}"
    
    # Wait for server to be ready by checking if port is listening
    echo -e "${BLUE}Verifying server is ready...${NC}"
    for i in {1..10}; do
        if lsof -i :5003 >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is ready and listening on port 5003!${NC}"
            break
        fi
        echo -e "${BLUE}Waiting for server... ($i/10)${NC}"
        sleep 2
    done
    
    # Final check
    if lsof -i :5003 >/dev/null 2>&1; then
        echo -e "${GREEN}🌐 Server confirmed ready at: http://localhost:5003${NC}"
        
        # Save PID for later reference
        echo $APP_PID > .server_pid
        
        # Try to open browser automatically
        echo -e "${BLUE}Opening browser...${NC}"
        if command -v open >/dev/null 2>&1; then
            # macOS
            open http://localhost:5003 2>/dev/null &
        elif command -v xdg-open >/dev/null 2>&1; then
            # Linux
            xdg-open http://localhost:5003 2>/dev/null &
        fi
        
        echo -e "${GREEN}🚀 Server started successfully in background!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Server failed to start properly!${NC}"
        kill $APP_PID 2>/dev/null
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to start application!${NC}"
    exit 1
fi 