@echo off
echo Stopping GradeMate Backend Server...
echo.

REM Kill any Python processes running uvicorn
taskkill /f /im python.exe /fi "WINDOWTITLE eq *uvicorn*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *uvicorn*" >nul 2>&1

REM Alternative method - kill processes using port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo Backend server stopped (if it was running)
echo.
pause
