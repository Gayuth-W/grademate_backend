@echo off
echo ========================================
echo    GradeMate Backend Server Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Python found. Starting GradeMate Backend...
echo.

REM Change to the Backend directory
cd /d "%~dp0"

REM Check if required files exist
if not exist "app\main.py" (
    echo ERROR: main.py not found in app directory
    echo Please ensure you're running this from the Backend directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
    if errorlevel 1 (
        echo WARNING: Failed to activate virtual environment
        echo Continuing with system Python...
    ) else (
        echo Virtual environment activated successfully
    )
) else (
    echo WARNING: Virtual environment not found
    echo Using system Python...
)

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Failed to install some dependencies
    echo Continuing anyway...
)

echo.
echo Starting FastAPI server...
echo Server will be available at: http://127.0.0.1:8000
echo API documentation at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

REM If we get here, the server was stopped
echo.
echo ========================================
echo Server stopped
echo ========================================
pause
