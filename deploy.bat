@echo off
chcp 65001 2>nul
setlocal

echo ========================================
echo     Music Station Deploy Script
echo ========================================
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%" 2>nul
set "ROOT=%CD%"

echo Project directory: %ROOT%
echo.

:: 1. Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel%==0 (
    echo   Python installed:
    python --version
) else (
    echo   ERROR: Python not found!
    echo   Please install Python first: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   Installing pip...
    python -m ensurepip --upgrade >nul 2>&1
)

:: 2. Check Node.js
echo.
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if %errorlevel%==0 (
    echo   Node.js installed:
    node --version
) else (
    echo   ERROR: Node.js not found!
    echo   Please install Node.js first: https://nodejs.org/
    echo   Recommended: LTS version
    echo.
    pause
    exit /b 1
)

:: 3. Install backend dependencies
echo.
echo [3/6] Installing backend dependencies...
cd /d "%ROOT%\music-api"
if %errorlevel% neq 0 (
    echo   ERROR: Cannot find music-api directory
    pause
    exit /b 1
)
echo   Current directory: %CD%

if not exist "venv" (
    echo   Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo   Virtual environment activated

echo   Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo   ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo   Backend dependencies installed

:: 4. Install frontend dependencies
echo.
echo [4/6] Installing frontend dependencies...
cd /d "%ROOT%\music-web"
echo   Current directory: %CD%

echo   Installing npm packages...
npm install
if %errorlevel% neq 0 (
    echo   ERROR: npm install failed
    pause
    exit /b 1
)
echo   Frontend dependencies installed

:: 5. Initialize database
echo.
echo [5/6] Initializing database...
cd /d "%ROOT%\music-api"
call venv\Scripts\activate.bat >nul 2>&1
python seed.py
echo   Database initialized

:: 6. Start services
echo.
echo [6/6] Starting services...
echo.
echo ========================================
echo   Services starting...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo   Starting backend...
start "Music Backend" cmd /k "cd /d "%ROOT%\music-api" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0"

timeout /t 3 /nobreak >nul

echo   Starting frontend...
cd /d "%ROOT%\music-web"
start "Music Frontend" cmd /k "cd /d "%ROOT%\music-web" && npm run dev"

echo.
echo   Done! Please open http://localhost:5173 in your browser
echo.
echo   Press any key to exit...
pause >nul
