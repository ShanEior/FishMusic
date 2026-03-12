#!/bin/bash

# Music Station 一键部署脚本 (Linux/Mac)

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "    Music Station 一键部署脚本"
echo "========================================"
echo ""

# 检查并安装 Python
check_python() {
    if command -v python3 &> /dev/null; then
        echo "[1/6] Python 已安装: $(python3 --version)"
        return 0
    fi

    echo "[1/6] 正在安装 Python..."

    if command -v brew &> /dev/null; then
        brew install python3
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    else
        echo "无法自动安装 Python，请手动安装: https://www.python.org/downloads/"
        exit 1
    fi
}

# 检查并安装 Node.js
check_node() {
    if command -v node &> /dev/null; then
        echo "[2/6] Node.js 已安装: $(node --version)"
        return 0
    fi

    echo "[2/6] 正在安装 Node.js..."

    if command -v brew &> /dev/null; then
        brew install node
    elif command -v apt-get &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
    elif command -v dnf &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo dnf install -y nodejs
    else
        echo "无法自动安装 Node.js，请手动安装: https://nodejs.org/"
        exit 1
    fi
}

# 检查并安装 pnpm
check_pnpm() {
    if command -v pnpm &> /dev/null; then
        echo "    pnpm 已安装: $(pnpm --version)"
        return 0
    fi

    echo "    正在安装 pnpm..."
    npm install -g pnpm
}

# 主流程
check_python
check_node

# 检查 pnpm 或使用 npm
if command -v pnpm &> /dev/null; then
    NODE_PM="pnpm"
else
    NODE_PM="npm"
fi
echo "[2/6] 使用: $NODE_PM"

# 安装后端依赖
echo ""
echo "[3/6] 安装后端依赖..."
cd "$PROJECT_ROOT/music-api"

if [ ! -d "venv" ]; then
    echo "    创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

# 安装前端依赖
echo ""
echo "[4/6] 安装前端依赖..."
cd "$PROJECT_ROOT/music-web"
$NODE_PM install -q

# 初始化数据库
echo ""
echo "[5/6] 初始化数据库..."
cd "$PROJECT_ROOT/music-api"
source venv/bin/activate
python3 seed.py 2>/dev/null || true

# 启动服务
echo ""
echo "[6/6] 启动服务..."
echo ""
echo "========================================"
echo "    所有组件安装完成！"
echo "========================================"
echo "    后端:   http://localhost:8000"
echo "    前端:   http://localhost:5173"
echo "    API文档: http://localhost:8000/docs"
echo ""
echo "    首次启动可能需要等待几秒钟..."
echo "========================================"
echo ""

# 杀掉可能存在的旧进程
pkill -f uvicorn 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# 后端
cd "$PROJECT_ROOT/music-api"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 &
BACKEND_PID=$!

# 等待后端启动
sleep 4

# 前端
cd "$PROJECT_ROOT/music-web"
$NODE_PM run dev &

echo ""
echo "服务已启动！"
echo "请在浏览器中访问 http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待
wait
