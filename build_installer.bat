@echo off
title Building Instagram Auto Poster Installer
echo ================================================
echo   Building Professional Windows Installer
echo ================================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo NSIS not found! 
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo.
    echo After installation, add NSIS to your PATH or run this from the NSIS directory.
    echo.
    pause
    exit /b 1
)

echo NSIS found! Building installer...
echo.

REM Build the installer
makensis installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   ✅ Installer built successfully!
    echo ================================================
    echo.
    echo The installer has been created and is ready for distribution.
    echo.
    echo To digitally sign the installer:
    echo 1. Get a code signing certificate from a trusted CA
    echo 2. Use signtool.exe to sign the .exe file
    echo.
    echo Example signing command:
    echo signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "Instagram_Auto_Poster_Installer.exe"
    echo.
) else (
    echo.
    echo ❌ Installer build failed!
    echo Please check the errors above.
    echo.
)

pause
