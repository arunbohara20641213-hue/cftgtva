@echo off
REM Quick start script for RAG System (Windows)
REM This script sets up and runs both backend and frontend

echo.
echo ========================================
echo  RAG System - Quick Start (Windows)
echo ========================================
echo.

REM Colors and messages
echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)

REM Check Ollama
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not running. Start it with: ollama serve
    echo Then run this script again.
    pause
    exit /b 1
)

echo OK - All prerequisites found!
echo.

REM Backend setup
echo ========================================
echo Setting up Backend...
echo ========================================
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\Activate.bat
echo Installing/updating dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo Starting Backend (Port 8000)...
echo ========================================
echo Backend will start at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.

REM Start backend in new window
start cmd /k "cd /d %CD% && venv\Scripts\python.exe app.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Frontend setup
echo.
echo ========================================
echo Setting up Frontend...
echo ========================================
cd ..\frontend

echo Installing dependencies...
call npm install --legacy-peer-deps >nul 2>&1

echo.
echo ========================================
echo Starting Frontend (Port 3000)...
echo ========================================
echo Frontend will open at http://localhost:3000
echo.

call npm start

pause
