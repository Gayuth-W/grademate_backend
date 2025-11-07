@echo off
REM GradeMate Backend Railway Deployment Script for Windows
REM This script helps deploy your FastAPI backend to Railway

echo 🎓 GradeMate Backend - Railway Deployment
echo =========================================

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Check if user is logged in to Railway
railway whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 🔐 Please login to Railway:
    railway login
)

echo 🔍 Checking Railway project status...
railway status

echo.
echo 📋 Railway Deployment Options:
echo    1. Deploy from current directory
echo    2. Link to existing Railway project
echo    3. Create new Railway project
echo.

set /p choice="Choose an option (1-3): "

if "%choice%"=="1" (
    echo 🚀 Deploying from current directory...
    railway up
) else if "%choice%"=="2" (
    echo 🔗 Linking to existing Railway project...
    railway link
    echo 🚀 Deploying to linked project...
    railway up
) else if "%choice%"=="3" (
    echo 🆕 Creating new Railway project...
    railway init
    echo 🚀 Deploying to new project...
    railway up
) else (
    echo ❌ Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo ✅ Deployment completed!
echo.
echo 📋 Next steps:
echo    1. Add MySQL database service in Railway dashboard
echo    2. Set environment variables:
echo       - DATABASE_URL (use Railway's automatic MySQL variables)
echo       - CORS_ORIGINS
echo       - GOOGLE_API_KEY (if using AI features)
echo.
echo    3. Update your frontend API URL to point to Railway
echo.
echo    4. Test your API endpoints
echo.
echo 🔗 Railway Dashboard: https://railway.app/dashboard

pause
