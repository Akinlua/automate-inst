@echo off
title Instagram Auto Poster - Setup
cls

cd /d "%~dp0InstagramAutoPoster"

if not exist "setup.bat" (
    echo ERROR: setup.bat not found in InstagramAutoPoster folder
    echo Please make sure the InstagramAutoPoster folder is present.
    pause
    exit /b 1
)

echo Starting Instagram Auto Poster setup...
echo App directory: %CD%
echo.

call setup.bat

echo.
echo Setup finished.
pause
