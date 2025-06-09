@echo off
title Instagram Auto Poster - Setup and Launch
cls

echo.
echo ===============================================
echo   Instagram Auto Poster - Setup ^& Launch
echo ===============================================
echo.
echo This script will:
echo 1. Check and install Python if needed
echo 2. Create virtual environment
echo 3. Install all dependencies
echo 4. Create necessary folders
echo 5. Start the web application
echo.
echo Press any key to continue...
pause >nul

:: Check if Python is installed
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Installing Python...
    echo.
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to:
    echo - Check "Add Python to PATH"
    echo - Install pip
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
) else (
    echo Python found!
    python --version
)

:: Check if pip is available
echo.
echo [2/5] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found! Installing pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip. Please install pip manually.
        pause
        exit /b 1
    )
) else (
    echo pip found!
    python -m pip --version
)

:: Create virtual environment if it doesn't exist
echo.
echo [3/5] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

:: Upgrade pip in virtual environment
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo.
echo [4/5] Installing dependencies...
echo This may take a few minutes...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies!
    echo Trying alternative installation...
    python -m pip install selenium Pillow python-dotenv schedule openai requests flask werkzeug pytz psutil undetected-chromedriver setuptools selenium-driverless
    if %errorlevel% neq 0 (
        echo Failed to install dependencies!
        pause
        exit /b 1
    )
)

:: Create necessary directories
echo.
echo [5/5] Creating necessary directories...
if not exist "content" mkdir content
if not exist "static" mkdir static
if not exist "templates" mkdir templates

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul 2>&1
    if not exist ".env" (
        echo # Instagram Auto Poster Configuration > .env
        echo CONTENT_DIR=content >> .env
        echo USE_CHATGPT=false >> .env
        echo OPENAI_API_KEY= >> .env
        echo CHROME_PROFILE_PATH= >> .env
        echo CHROME_USER_DATA_DIR= >> .env
        echo CHROME_PROFILE_NAME=InstagramBot >> .env
    )
)

:: Check if Chrome is installed
echo.
echo Checking Google Chrome installation...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorlevel% neq 0 (
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon" /v version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: Google Chrome not detected!
        echo Please install Google Chrome from: https://www.google.com/chrome/
        echo.
        echo You can continue, but Chrome setup may fail later.
        echo Press any key to continue anyway...
        pause >nul
    ) else (
        echo Google Chrome found!
    )
) else (
    echo Google Chrome found!
)

:: Success message
echo.
echo ===============================================
echo   Setup Complete!
echo ===============================================
echo.
echo The web application will now start...
echo.
echo Once started, open your browser and go to:
echo http://localhost:5003
echo.
echo To stop the application, press Ctrl+C in this window.
echo.
echo Press any key to start the application...
pause >nul

:: Start the application
echo.
echo Starting Instagram Auto Poster...
echo.
python app.py

:: Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    echo Check the error messages above.
    pause
) 