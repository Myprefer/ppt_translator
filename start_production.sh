#!/bin/bash
# PPT翻译服务器启动脚本 - Linux/Mac版本

echo "正在启动PPT翻译服务器..."

# 检查虚拟环境
if [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 创建必要的目录
mkdir -p logs
mkdir -p pids  
mkdir -p translated_files

# 设置环境变量
export FLASK_ENV=production
export SECRET_KEY=8sadhfalkduaf9duf9hndsclkada5313

echo "使用Gunicorn启动生产服务器..."
echo "服务器地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务器"

# 启动Gunicorn服务器
gunicorn -c gunicorn.conf.py wsgi:application
