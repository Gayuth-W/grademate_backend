@echo off
echo Starting GradeMate Backend Server for Student View...
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start the server
echo Starting server on port 8001...
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

pause
