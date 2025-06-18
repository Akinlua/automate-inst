; Instagram Auto Poster - Professional Windows Installer
; Created with NSIS (Nullsoft Scriptable Install System)

!define APP_NAME "Instagram Auto Poster"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Instagram Auto Poster Team"
!define APP_URL "https://github.com/your-repo/instagram-auto-poster"
!define APP_DESCRIPTION "Professional Instagram automation tool with modern GUI"

; Installer name and output file
Name "${APP_NAME}"
OutFile "Instagram_Auto_Poster_Installer_${TIMESTAMP}.exe"
InstallDir "$PROGRAMFILES\InstagramAutoPoster"
RequestExecutionLevel admin

; Modern UI includes
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; MUI Settings
!define MUI_ABORTWARNING
; !define MUI_ICON "installer_icon.ico"
; !define MUI_UNICON "installer_icon.ico"
; !define MUI_HEADERIMAGE
; !define MUI_HEADERIMAGE_BITMAP "installer_header.bmp"
; !define MUI_WELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"
; !define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page (optional)
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Instagram Auto Poster.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Instagram Auto Poster"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\USER_GUIDE.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show User Guide"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "Comments" "${APP_DESCRIPTION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2024 ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "InternalName" "${APP_NAME}"
VIAddVersionKey "OriginalFilename" "Instagram_Auto_Poster_Installer.exe"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO  ; Read-only section (always installed)
    
    SetOutPath "$INSTDIR"
    
    ; Copy all application files
    File /r "Instagram_Auto_Poster_Package\InstagramAutoPoster\*.*"
    File "Instagram_Auto_Poster_Package\Instagram Auto Poster.bat"
    File "Instagram_Auto_Poster_Package\USER_GUIDE.md"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\Instagram Auto Poster.bat"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\Instagram Auto Poster.bat"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.md"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    ; WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; Calculate and write installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
SectionEnd

Section "Python Runtime" SecPython
    DetailPrint "Checking Python installation..."
    
    ; Check if Python is already installed
    nsExec::ExecToStack 'python --version'
    Pop $0
    ${If} $0 != 0
        ; Python not found, show message to user
        MessageBox MB_OK "Python 3.11+ is required but not found.$\n$\nPlease install Python from https://python.org and run this installer again.$\n$\nMake sure to check 'Add Python to PATH' during installation."
    ${Else}
        DetailPrint "Python is already installed."
    ${EndIf}
SectionEnd

Section "Auto-Startup" SecAutoStart
    DetailPrint "Setting up auto-startup..."
    
    ; Add to Windows startup registry
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "InstagramAutoPoster" "$INSTDIR\Instagram Auto Poster.bat"
    
SectionEnd

Section "Desktop Integration" SecDesktop
    ; Create additional desktop shortcuts
    CreateShortCut "$DESKTOP\Instagram Auto Poster - Setup.lnk" "$INSTDIR\Instagram Auto Poster.bat"
    
    ; Register file associations (optional)
    WriteRegStr HKCR ".iap" "" "InstagramAutoPoster.Project"
    WriteRegStr HKCR "InstagramAutoPoster.Project" "" "Instagram Auto Poster Project"
    ; WriteRegStr HKCR "InstagramAutoPoster.Project\DefaultIcon" "" "$INSTDIR\icon.ico"
    WriteRegStr HKCR "InstagramAutoPoster.Project\shell\open\command" "" '"$INSTDIR\Instagram Auto Poster.bat" "%1"'
    
SectionEnd

; Component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} "Download and install Python runtime if not present"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} "Start Instagram Auto Poster automatically with Windows"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcuts and file associations"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "InstagramAutoPoster"
    DeleteRegKey HKCR ".iap"
    DeleteRegKey HKCR "InstagramAutoPoster.Project"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$DESKTOP\Instagram Auto Poster - Setup.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove application files
    RMDir /r "$INSTDIR"
    
SectionEnd

; Functions
Function .onInit
    ; Check Windows version
    ${IfNot} ${AtLeastWin7}
        MessageBox MB_OK "This application requires Windows 7 or later."
        Abort
    ${EndIf}
    
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APP_NAME} is already installed. $\n$\nClick OK to remove the previous version or Cancel to cancel this upgrade." \
    IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
        
        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:
    
    done:
FunctionEnd

Function .onInstSuccess
    ; Show completion message
    MessageBox MB_OK "${APP_NAME} has been installed successfully!$\n$\nClick OK to continue."
FunctionEnd
