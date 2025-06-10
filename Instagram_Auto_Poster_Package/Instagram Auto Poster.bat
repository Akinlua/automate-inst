@echo off
title Instagram Auto Poster
cd /d "%~dp0"

REM Enable delayed expansion for the loop
setlocal EnableDelayedExpansion

REM Try to find Python
set PYTHON_CMD=

for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

REM If Python not found, try to install it
echo Python not found. Please install Python from https://python.org
echo Press any key to open Python download page...
pause >nul
start https://python.org/downloads
exit /b 1

:found_python
echo Starting Instagram Auto Poster...
"!PYTHON_CMD!" gui_installer.py
if !errorlevel! neq 0 (
    echo.
    echo Failed to start the installer.
    pause
)
