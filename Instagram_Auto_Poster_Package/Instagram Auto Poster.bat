@echo off
title Instagram Auto Poster
cd /d "%~dp0"

REM Enable delayed expansion for the loop
setlocal EnableDelayedExpansion

REM Try to find Python
set PYTHON_CMD=

echo Checking for Python installation...
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

REM If Python not found, automatically download and install it
echo Python not found. Downloading and installing Python automatically (ensure after successful download to close and start the application...
echo This may take a few minutes...
echo.

REM Create temp directory for download
if not exist "%TEMP%\InstagramAutoPoster" mkdir "%TEMP%\InstagramAutoPoster"
cd /d "%TEMP%\InstagramAutoPoster"

REM Download Python installer
echo Downloading Python installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'}"

if not exist "python_installer.exe" (
    echo Failed to download Python installer.
    echo Please manually install Python from https://python.org/downloads
    echo Press any key to open Python download page...
    pause >nul
    start https://python.org/downloads
    exit /b 1
)

REM Install Python silently with pip and add to PATH
echo Installing Python...
echo This will take a few minutes, please wait...
python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1

REM Wait for installation to complete
timeout /t 10 >nul

REM Clean up installer
del python_installer.exe

REM Return to original directory
cd /d "%~dp0"

REM Refresh PATH by restarting command processor
echo Refreshing system PATH...
call refreshenv.cmd >nul 2>&1 || (
    echo Please restart this script after Python installation completes.
    echo Press any key to restart...
    pause >nul
    "%~f0"
    exit /b
)

REM Try to find Python again after installation
echo Checking for Python after installation...
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

REM If still not found, try refreshing PATH manually
echo Refreshing PATH variables...
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "UserPath=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SystemPath=%%b"
set "PATH=%UserPath%;%SystemPath%"

REM Try Python one more time
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

echo Python installation may have succeeded but is not in PATH.
echo Please restart your computer and try again, or install Python manually.
echo Press any key to open Python download page...
pause >nul
start https://python.org/downloads
exit /b 1

:found_python
echo Found Python: !PYTHON_CMD!
echo Starting Instagram Auto Poster...
"!PYTHON_CMD!" gui_installer.py
if !errorlevel! neq 0 (
    echo.
    echo Failed to start the installer.
    pause
)
