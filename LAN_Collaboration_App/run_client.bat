@echo off
REM ====================================================
REM LAN Collaboration App - Client Launcher
REM ====================================================

echo.
echo ========================================
echo   LAN Collaboration App - Client
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
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Found virtual environment, activating...
    call venv\Scripts\activate.bat
)

REM Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import cv2, pyaudio, PyQt5, numpy, mss, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some dependencies are missing!
    echo [INFO] Installing dependencies from requirements.txt...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to install dependencies
        echo.
        echo Please manually run:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo [OK] All dependencies installed
echo.

REM Check if client_gui.py exists
if not exist "client\client_gui.py" (
    echo [ERROR] client\client_gui.py not found!
    echo.
    echo Please make sure you are running this script from the
    echo LAN_Collaboration_App directory.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   Starting Client Application...
echo ========================================
echo.

REM Launch the client GUI
python client\client_gui.py

REM Check if the client exited with an error
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Client exited with error code: %errorlevel%
    echo ========================================
    echo.
    echo Possible issues:
    echo   1. Server is not running
    echo   2. Network connection problem
    echo   3. Firewall blocking connection
    echo   4. Missing dependencies
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo   Client closed successfully
echo ========================================
echo.
pause
