@echo off
REM ====================================================
REM LAN Collaboration App - Server Launcher
REM ====================================================

echo.
echo ========================================
echo   LAN Collaboration Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] numpy not installed
    echo [INFO] Installing dependencies...
    pip install numpy
)

echo [OK] Dependencies ready
echo.

REM Get local IP address
echo [INFO] Detecting local IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :ip_found
)
:ip_found
echo [INFO] Server IP: %IP%
echo.

REM Check if server directory exists
if not exist "server\server_main.py" (
    echo [ERROR] server\server_main.py not found!
    echo.
    echo Please make sure you are running this script from the
    echo LAN_Collaboration_App directory.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   Starting All Services...
echo ========================================
echo.
echo Clients should connect to: %IP%
echo.

REM Start the unified server
python server/server_main.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Server exited with error
    echo ========================================
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo   Server stopped successfully
echo ========================================
echo.
pause