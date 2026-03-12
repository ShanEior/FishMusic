@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo     Music Station 一键部署脚本
echo ========================================
echo.

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

:: 查找可用的包管理器
set "PACKAGE_MANAGER="
where winget >nul 2>&1
if %errorlevel% equ 0 set "PACKAGE_MANAGER=winget"
where choco >nul 2>&1
if %errorlevel% equ 0 (
    if "%PACKAGE_MANAGER%"=="" set "PACKAGE_MANAGER=choco"
)

:: ========== 安装函数 ==========
:install_python
echo.
echo     正在尝试安装 Python...
if "%PACKAGE_MANAGER%"=="winget" (
    winget install Python.Python.3.11 -e --silent --accept-source-agreements --accept-package-agreements
    if !errorlevel! equ 0 goto :python_ok
)
if "%PACKAGE_MANAGER%"=="choco" (
    choco install python --version=3.11.0 -y
    if !errorlevel! equ 0 goto :python_ok
)
:: 尝试下载 portable 版本
echo     自动安装失败，尝试下载便携版...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python-installer.exe'" 2>nul
if exist "%TEMP%\python-installer.exe" (
    start /wait "" "%TEMP%\python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1
    del "%TEMP%\python-installer.exe" 2>nul
    goto :python_ok
)
echo.
echo ========================================
echo     [错误] 无法自动安装 Python
echo     请手动下载安装: https://www.python.org/downloads/
echo     安装时勾选 "Add Python to PATH"
echo     安装完成后按任意键继续...
echo ========================================
pause >nul
:python_ok
:: 刷新 PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set "PATH=C:\Python311;C:\Python311\Scripts;%PATH%"
    python --version >nul 2>&1
)
echo     Python 安装完成

:: 刷新环境变量
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%b"
    set "PATH=%SysPath%"
)
exit /b 0

:install_nodejs
echo.
echo     正在尝试安装 Node.js...
if "%PACKAGE_MANAGER%"=="winget" (
    winget install OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements
    if !errorlevel! equ 0 goto :node_ok
)
if "%PACKAGE_MANAGER%"=="choco" (
    choco install nodejs-lts -y
    if !errorlevel! equ 0 goto :node_ok
)
:: 尝试下载 portable 版本
echo     自动安装失败，尝试下载便携版...
powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile '%TEMP%\node-installer.msi'" 2>nul
if exist "%TEMP%\node-installer.msi" (
    msiexec /i "%TEMP%\node-installer.msi" /quiet
    del "%TEMP%\node-installer.msi" 2>nul
    goto :node_ok
)
echo.
echo ========================================
echo     [错误] 无法自动安装 Node.js
echo     请手动下载安装: https://nodejs.org/
echo     推荐安装 LTS 版本
echo     安装完成后按任意键继续...
echo ========================================
pause >nul
:node_ok
node --version >nul 2>&1
if %errorlevel% neq 0 (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%b"
    set "PATH=%SysPath%"
    node --version >nul 2>&1
)
echo     Node.js 安装完成
exit /b 0

:: ========== 主流程 ==========

:: 1. 检查/安装 Python
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :install_python
)

:: 确保 pip 可用
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     正在安装 pip...
    python -m ensurepip --upgrade 2>nul
    python -m pip --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo     [警告] pip 安装失败，尝试其他方法...
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py'" 2>nul
        python "%TEMP%\get-pip.py" 2>nul
        del "%TEMP%\get-pip.py" 2>nul
    )
)

:: 2. 检查/安装 Node.js
echo [2/6] 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    call :install_nodejs
)

:: 3. 安装后端依赖
echo.
echo [3/6] 安装后端依赖...
cd /d "%PROJECT_ROOT%\music-api"
if not exist "venv" (
    echo     创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo     [警告] 依赖安装失败，尝试使用系统 Python...
    cd /d "%PROJECT_ROOT%\music-api"
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo     后端依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo     后端依赖安装完成

:: 4. 安装前端依赖
echo.
echo [4/6] 安装前端依赖...
cd /d "%PROJECT_ROOT%\music-web"

:: 检查 npm 或 pnpm
set "NODE_PACKAGE_MANAGER=npm"
where pnpm >nul 2>&1
if %errorlevel% equ 0 set "NODE_PACKAGE_MANAGER=pnpm"

!NODE_PACKAGE_MANAGER! install --silent
if %errorlevel% neq 0 (
    echo     [警告] !NODE_PACKAGE_MANAGER! 安装失败，尝试 npm...
    npm install --silent
    if %errorlevel% neq 0 (
        echo     前端依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo     前端依赖安装完成

:: 5. 初始化数据库
echo.
echo [5/6] 初始化数据库...
cd /d "%PROJECT_ROOT%\music-api"
call venv\Scripts\activate.bat >nul
python seed.py >nul 2>&1
if %errorlevel% equ 0 (
    echo     数据库初始化完成
) else (
    echo     数据库可能已初始化，跳过
)

:: 6. 启动服务
echo.
echo [6/6] 启动服务...
echo.
echo ========================================
echo     所有组件安装完成！
echo ========================================
echo     后端:   http://localhost:8000
echo     前端:   http://localhost:5173
echo     API文档: http://localhost:8000/docs
echo.
echo     首次启动可能需要等待几秒钟...
echo ========================================
echo.

:: 杀掉可能存在的旧进程
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: 后端
start "Music Station - Backend" cmd /k "cd /d "%PROJECT_ROOT%\music-api" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0"

:: 等待后端启动
timeout /t 4 /nobreak >nul

:: 前端
start "Music Station - Frontend" cmd /k "cd /d "%PROJECT_ROOT%\music-web" && !NODE_PACKAGE_MANAGER! run dev"

echo.
echo     已在新窗口启动后端和前端
echo     请在浏览器中访问 http://localhost:5173
echo.
pause
