#!/bin/bash

# 多模态学术推荐系统启动脚本

echo "========================================="
echo "  多模态学术推荐系统"
echo "========================================="
echo ""

# 检查后端是否就绪
echo "[1/3] 检查后端依赖..."
cd backend
if [ ! -d ".venv" ]; then
    echo "初始化 uv 环境..."
    uv sync
fi
cd ..

echo ""
echo "[2/3] 检查前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装 npm 依赖..."
    npm install
fi
cd ..

echo ""
echo "[3/3] 启动服务..."
echo ""
echo "请在两个不同的终端中运行以下命令："
echo ""
echo "  终端 1 (后端):"
echo "    cd backend && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  终端 2 (前端):"
echo "    cd frontend && npm run dev"
echo ""
echo "或者使用 tmux/screen 在后台运行"
echo ""
echo "========================================="
