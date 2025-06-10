@echo off
title Instagram Auto Poster

REM Change to script directory
cd /d "%~dp0"

echo ============================================== 
echo    Instagram Auto Poster - Quick Start
echo ==============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first to complete the initial setup.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if app.py exists
if not exist "app.py" (
    echo app.py not found!
    echo Please make sure all application files are in this directory.
    echo.
    pause
    exit /b 1
)

REM Set environment variables to prevent Python from freezing on Windows
set PYTHONUNBUFFERED=1
set PYTHONDONTWRITEBYTECODE=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1
set FLASK_ENV=production
set PYTHONUTF8=1
set PYTHONFAULTHANDLER=1

REM Start the application with unbuffered output and no input
echo.
echo Starting Instagram Auto Poster...
echo.
echo Open your browser and go to: http://localhost:5003
echo.
echo Press Ctrl+C to stop the application.
echo.

REM Use -u flag to prevent buffering, -X dev for better error handling, and < nul to prevent input hanging
python -u -X dev app.py < nul 