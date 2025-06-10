@echo off
title Instagram Auto Poster - Starting...
setlocal EnableDelayedExpansion

echo.
echo ==============================================
echo    Instagram Auto Poster - Starting...
echo ==============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Please run setup first.
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo [ERROR] app.py not found!
    echo [INFO] Please make sure all application files are in this directory.
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)

echo.
echo [SUCCESS] Starting Instagram Auto Poster...
echo.
echo [SUCCESS] Server will be available at: http://localhost:5003
echo.

REM Start the application in background
echo [INFO] Starting server process...
start /B python app.py

REM Give it more time to start
echo [INFO] Waiting for server to initialize...
timeout /t 5 /nobreak >nul

REM Check if server is responding (multiple attempts)
echo [INFO] Verifying server startup...
set SERVER_READY=0
for /L %%i in (1,1,10) do (
    timeout /t 2 /nobreak >nul
    netstat -an | find "5003" | find "LISTENING" >nul 2>&1
    if !errorlevel! == 0 (
        set SERVER_READY=1
        echo [SUCCESS] ✅ Server is ready and listening on port 5003!
        goto :server_ready
    )
    echo [INFO] Waiting for server... (%%i/10)
)

:server_ready
if !SERVER_READY! == 1 (
    echo [SUCCESS] 🌐 Server confirmed ready at: http://localhost:5003
    echo [SUCCESS] 🚀 Server started successfully in background!
    
    REM Open browser
    echo [INFO] Opening browser...
    start http://localhost:5003
    
    exit /b 0
) else (
    echo [ERROR] ❌ Server failed to start properly!
    exit /b 1
) 