@echo off
title Instagram Auto Poster - Quick Start
cls

echo.
echo ===============================================
echo   Instagram Auto Poster - Quick Start
echo ===============================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first to complete the initial setup.
    echo.
    pause
    exit /b 1
)

:: Check if app.py exists
if not exist "app.py" (
    echo app.py not found!
    echo Please make sure all application files are in this directory.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment!
    echo Please run setup.bat to fix the installation.
    pause
    exit /b 1
)

:: Start the application
echo.
echo Starting Instagram Auto Poster...
echo.
echo Open your browser and go to: http://localhost:5003
echo.
echo Press Ctrl+C to stop the application.
echo.

python app.py

:: Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    echo Check the error messages above.
    pause
) 