# Music Station Deploy Script (PowerShell)
$ErrorActionPreference = "Continue"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Music Station Deploy Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    python --version
} else {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Install: https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/6] Checking Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    node --version
} else {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "Install: https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[3/6] Backend dependencies..." -ForegroundColor Yellow
Set-Location "$ROOT\music-api"
Write-Host "  Current: $(Get-Location)"

if (-not (Test-Path "venv")) {
    Write-Host "  Creating venv..."
    python -m venv venv
}

Write-Host "  Activating venv..."
& ".\venv\Scripts\Activate.ps1"

Write-Host "  Installing packages..."
pip install -r requirements.txt
Write-Host "  Done"

Write-Host ""
Write-Host "[4/6] Frontend dependencies..." -ForegroundColor Yellow
Set-Location "$ROOT\music-web"
Write-Host "  Current: $(Get-Location)"

Write-Host "  Installing npm packages..."
npm install 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "  Done"

Write-Host ""
Write-Host "[5/6] Database..." -ForegroundColor Yellow
Set-Location "$ROOT\music-api"
& ".\venv\Scripts\Activate.ps1" -ErrorAction SilentlyContinue
python seed.py

Write-Host ""
Write-Host "[6/6] Starting services..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""

# Start backend
Start-Process -FilePath "cmd" -ArgumentList "/k cd /d `"$ROOT\music-api`" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start frontend
Start-Process -FilePath "cmd" -ArgumentList "/k cd /d `"$ROOT\music-web`" && npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Done! Open http://localhost:5173 in your browser" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
