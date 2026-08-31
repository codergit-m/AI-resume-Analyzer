@echo off
echo ================================================================
echo  ResumAI — Local Development Startup (Single Frame)
echo ================================================================
echo.

:: Check if .env exists
if not exist backend\.env (
    echo [!] backend\.env not found. Copying from .env.example...
    copy backend\.env.example backend\.env
    echo [!] Please fill in your API keys in backend\.env before continuing.
    pause
    exit /b 1
)

echo Starting frontend and backend concurrently in this window...
npm start

