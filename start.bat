@echo off
title Instagram Auto Poster
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

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Start the application
echo.
echo Starting Instagram Auto Poster...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application.
echo.

python app.py

pause 