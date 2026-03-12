@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo     Music Station 一键部署脚本
echo ========================================
echo.

:: 检查并安装 Python
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     Python 未安装，正在安装...
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        winget install Python.Python.3.11 -e --silent
    ) else (
        echo     winget 未找到，请手动安装 Python: https://www.python.org/downloads/
        echo     安装完成后按任意键继续...
        pause >nul
    )
    :: 等待安装完成
    echo     等待 Python 安装完成...
    timeout /t 15 /nobreak >nul
    set "PATH=C:\Python311;C:\Python311\Scripts;%PATH%"
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo     Python 安装失败，请手动安装后重试
        pause
        exit /b 1
    )
)
echo     Python 已安装

:: 检查并安装 Node.js
echo.
echo [2/5] 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     Node.js 未安装，正在安装...
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        winget install OpenJS.NodeJS.LTS -e --silent
    ) else (
        echo     winget 未找到，请手动安装 Node.js: https://nodejs.org/
        echo     安装完成后按任意键继续...
        pause >nul
    )
    :: 等待安装完成
    echo     等待 Node.js 安装完成...
    timeout /t 30 /nobreak >nul
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo     Node.js 安装失败，请手动安装后重试
        pause
        exit /b 1
    )
)
echo     Node.js 已安装

:: 安装后端依赖
echo.
echo [3/5] 安装后端依赖...
cd /d "%~dp0music-api"
if not exist "venv" (
    echo     创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo     后端依赖安装失败
    pause
    exit /b 1
)
echo     后端依赖安装完成

:: 安装前端依赖
echo.
echo [4/5] 安装前端依赖...
cd /d "%~dp0music-web"
npm install --silent
if %errorlevel% neq 0 (
    echo     前端依赖安装失败
    pause
    exit /b 1
)
echo     前端依赖安装完成

:: 启动服务
echo.
echo [5/5] 启动服务...
echo.
echo ========================================
echo     服务启动完成！
echo ========================================
echo     后端: http://localhost:8000
echo     前端: http://localhost:5173
echo     API文档: http://localhost:8000/docs
echo.
echo     按 Ctrl+C 停止服务
echo ========================================
echo.

:: 后端
start "Music Station - Backend" cmd /k "cd /d "%~dp0music-api" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 前端
start "Music Station - Frontend" cmd /k "cd /d "%~dp0music-web" && npm run dev"

echo.
echo     已打开两个命令行窗口分别运行后端和前端
echo     请在浏览器中访问 http://localhost:5173
echo.
pause
