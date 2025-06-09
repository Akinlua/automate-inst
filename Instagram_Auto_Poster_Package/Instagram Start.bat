@echo off
title Instagram Auto Poster - Start
cls

cd /d "%~dp0InstagramAutoPoster"

if not exist "start.bat" (
    echo ERROR: start.bat not found in InstagramAutoPoster folder
    echo Please make sure the InstagramAutoPoster folder is present.
    pause
    exit /b 1
)

echo Starting Instagram Auto Poster...
echo App directory: %CD%
echo.

call start.bat

if %errorlevel% neq 0 (
    echo.
    echo Start script finished with an error.
    pause
)
