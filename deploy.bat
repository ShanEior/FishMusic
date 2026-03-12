@echo off
set "ROOT=%~dp0"
cd /d "%ROOT%"

echo ========================================
echo     Music Station Deploy Script
echo ========================================
echo.

:: 1. Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel%==0 (
    echo   Python OK:
    python --version
) else (
    echo   ERROR: Python not found!
    echo   Install: https://www.python.org/downloads/
    cmd /k
)

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 python -m ensurepip --upgrade

:: 2. Check Node.js
echo.
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if %errorlevel%==0 (
    echo   Node OK:
    node --version
) else (
    echo   ERROR: Node.js not found!
    echo   Install: https://nodejs.org/
    cmd /k
)

:: 3. Backend
echo.
echo [3/6] Backend dependencies...
cd /d "%ROOT%\music-api"
if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo   Done

:: 4. Frontend
echo.
echo [4/6] Frontend dependencies...
cd /d "%ROOT%\music-web"
npm install
echo   Done

:: 5. Database
echo.
echo [5/6] Database...
cd /d "%ROOT%\music-api"
call venv\Scripts\activate.bat >nul
python seed.py

:: 6. Start
echo.
echo [6/6] Starting services...
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo.

start "Music Backend" cmd /k "cd /d "%ROOT%\music-api" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload"
start "Music Frontend" cmd /k "cd /d "%ROOT%\music-web" && npm run dev"

echo   Started! Open http://localhost:5173
echo.
echo   Press any key to exit...
pause >nul
