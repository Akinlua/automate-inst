@echo off
title Instagram Auto Poster - Quick Installer Fix
echo ================================================
echo   Quick Installer Fix for Instagram Auto Poster
echo ================================================
echo.

echo 🔧 Fixing installer issues...
echo.

REM Create LICENSE.txt if missing
if not exist "LICENSE.txt" (
    echo ℹ️ Creating LICENSE.txt...
    echo Instagram Auto Poster - End User License Agreement > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2024 Instagram Auto Poster Team >> LICENSE.txt
    echo. >> LICENSE.txt
    echo This software is provided "as is" for educational purposes. >> LICENSE.txt
    echo Users are responsible for complying with Instagram's Terms of Service. >> LICENSE.txt
    echo and applicable laws. Use at your own risk. >> LICENSE.txt
    echo ✅ LICENSE.txt created!
)

REM Create minimal installer without icons
echo ℹ️ Creating minimal installer script...
echo ; Instagram Auto Poster - Minimal Professional Installer > installer_minimal.nsi
echo !define APP_NAME "Instagram Auto Poster" >> installer_minimal.nsi
echo !define APP_VERSION "1.0.0" >> installer_minimal.nsi
echo Name "${APP_NAME}" >> installer_minimal.nsi
echo OutFile "Instagram_Auto_Poster_Installer.exe" >> installer_minimal.nsi
echo InstallDir "$PROGRAMFILES\InstagramAutoPoster" >> installer_minimal.nsi
echo RequestExecutionLevel admin >> installer_minimal.nsi
echo. >> installer_minimal.nsi
echo !include "MUI2.nsh" >> installer_minimal.nsi
echo !include "FileFunc.nsh" >> installer_minimal.nsi
echo. >> installer_minimal.nsi
echo !define MUI_ABORTWARNING >> installer_minimal.nsi
echo !insertmacro MUI_PAGE_WELCOME >> installer_minimal.nsi
echo !insertmacro MUI_PAGE_DIRECTORY >> installer_minimal.nsi
echo !insertmacro MUI_PAGE_INSTFILES >> installer_minimal.nsi
echo !define MUI_FINISHPAGE_RUN "$INSTDIR\gui_installer.py" >> installer_minimal.nsi
echo !insertmacro MUI_PAGE_FINISH >> installer_minimal.nsi
echo !insertmacro MUI_UNPAGE_CONFIRM >> installer_minimal.nsi
echo !insertmacro MUI_UNPAGE_INSTFILES >> installer_minimal.nsi
echo !insertmacro MUI_LANGUAGE "English" >> installer_minimal.nsi
echo. >> installer_minimal.nsi
echo Section "Install" >> installer_minimal.nsi
echo   SetOutPath "$INSTDIR" >> installer_minimal.nsi
echo   File /r "Instagram_Auto_Poster_Package\*.*" >> installer_minimal.nsi
echo   CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\gui_installer.py" >> installer_minimal.nsi
echo   CreateDirectory "$SMPROGRAMS\${APP_NAME}" >> installer_minimal.nsi
echo   CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\gui_installer.py" >> installer_minimal.nsi
echo   CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" >> installer_minimal.nsi
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}" >> installer_minimal.nsi
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe" >> installer_minimal.nsi
echo   WriteUninstaller "$INSTDIR\Uninstall.exe" >> installer_minimal.nsi
echo SectionEnd >> installer_minimal.nsi
echo. >> installer_minimal.nsi
echo Section "Uninstall" >> installer_minimal.nsi
echo   DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" >> installer_minimal.nsi
echo   Delete "$DESKTOP\${APP_NAME}.lnk" >> installer_minimal.nsi
echo   RMDir /r "$SMPROGRAMS\${APP_NAME}" >> installer_minimal.nsi
echo   RMDir /r "$INSTDIR" >> installer_minimal.nsi
echo SectionEnd >> installer_minimal.nsi

echo ✅ Minimal installer script created!
echo.

REM Check if NSIS is available
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ NSIS not found!
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo Then run: build_installer.bat
    echo.
    echo The minimal installer script (installer_minimal.nsi) is ready to use.
    echo.
    pause
    exit /b 1
)

REM Check for package directory
if not exist "Instagram_Auto_Poster_Package" (
    echo ❌ Package directory not found!
    echo Make sure Instagram_Auto_Poster_Package folder exists in this directory.
    echo.
    pause
    exit /b 1
)

echo 🔨 Building minimal installer...
makensis installer_minimal.nsi

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   ✅ SUCCESS! Installer created!
    echo ================================================
    echo.
    echo 📦 File: Instagram_Auto_Poster_Installer.exe
    echo.
    echo This installer provides:
    echo ✅ Professional installation experience
    echo ✅ Desktop shortcut
    echo ✅ Start Menu entry  
    echo ✅ Add/Remove Programs entry
    echo ✅ Clean uninstaller
    echo.
    echo 🚀 Ready for distribution!
    echo.
    echo 💡 To eliminate security warnings completely:
    echo    Sign the installer with a code signing certificate
    echo    See SIGNING_GUIDE.md for instructions
    echo.
) else (
    echo ❌ Build failed! Check errors above.
)

pause 