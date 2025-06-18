@echo off
title Instagram Auto Poster - Automated Setup
setlocal EnableDelayedExpansion

echo.
echo ==============================================
echo    Instagram Auto Poster - Automated Setup
echo ==============================================
echo.
echo Setting up Instagram Auto Poster automatically...
echo.

REM Check for Python installation
set PYTHON_CMD=
set PYTHON_FOUND=0

echo [INFO] Checking Python installation...

REM Try different Python commands
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python py) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        REM Get Python version
        for /f "tokens=2" %%v in ('%%i --version 2^>^&1') do (
            set PYTHON_VERSION=%%v
            REM Extract major and minor version
            for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
                set MAJOR=%%a
                set MINOR=%%b
                if !MAJOR! geq 3 (
                    if !MINOR! geq 8 (
                        set PYTHON_CMD=%%i
                        set PYTHON_FOUND=1
                        echo [SUCCESS] Found Python !PYTHON_VERSION! using command: %%i
                        goto :python_found
                    )
                )
            )
        )
    )
)

:python_found
if !PYTHON_FOUND! == 0 (
    echo [ERROR] Python 3.8+ not found!
    echo [INFO] Please install Python from https://python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    start https://python.org/downloads/
    exit /b 1
)

REM Check pip
echo [INFO] Checking pip installation...
"!PYTHON_CMD!" -m pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [INFO] Installing pip...
    "!PYTHON_CMD!" -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install pip
        exit /b 1
    )
)
echo [SUCCESS] pip is available

REM Create virtual environment
echo [INFO] Setting up virtual environment...
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    "!PYTHON_CMD!" -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip in virtual environment
echo [INFO] Upgrading pip in virtual environment...
python -m pip install --upgrade pip -q
if !errorlevel! neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing...
)

REM Install dependencies
echo [INFO] Installing dependencies...
echo [INFO] This may take a few minutes...

if exist "requirements.txt" (
    python -m pip install -r requirements.txt -q
    if !errorlevel! neq 0 (
        echo [WARNING] requirements.txt installation failed, trying alternative...
        python -m pip install -q selenium Pillow python-dotenv schedule requests flask werkzeug pytz psutil undetected-chromedriver setuptools selenium-driverless
    )
) else (
    echo [INFO] Installing dependencies manually...
    python -m pip install -q selenium Pillow python-dotenv schedule requests flask werkzeug pytz psutil undetected-chromedriver setuptools selenium-driverless
)

if !errorlevel! neq 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [SUCCESS] Dependencies installed successfully!

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "content" mkdir content
if not exist "static" mkdir static
if not exist "templates" mkdir templates

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        (
            echo # Instagram Auto Poster Configuration
            echo CONTENT_DIR=content
            echo USE_CHATGPT=false
            echo OPENAI_API_KEY=
            echo CHROME_PROFILE_PATH=
            echo CHROME_USER_DATA_DIR=
            echo CHROME_PROFILE_NAME=InstagramBot
        ) > .env
    )
    echo [SUCCESS] .env file created
)

REM Check Chrome installation
echo [INFO] Checking Google Chrome installation...
set CHROME_FOUND=0

REM Check common Chrome installation paths
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

REM Check if chrome command works
chrome --version >nul 2>&1
if !errorlevel! == 0 set CHROME_FOUND=1

if !CHROME_FOUND! == 1 (
    echo [SUCCESS] Google Chrome found!
) else (
    echo [WARNING] Google Chrome not detected!
    echo [WARNING] Please install Google Chrome from: https://www.google.com/chrome/
    echo [WARNING] The application will work but Chrome setup may fail later.
)

echo.
echo [SUCCESS] ==============================================
echo [SUCCESS]    Setup Complete!
echo [SUCCESS] ==============================================
echo.
echo [SUCCESS] Instagram Auto Poster has been set up successfully!
echo [SUCCESS] The application is ready to launch.
echo.

exit /b 0 