@echo off
REM PPT翻译服务器启动脚本 - Windows版本

echo 正在启动PPT翻译服务器...

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "pids" mkdir pids
if not exist "translated_files" mkdir translated_files

REM 设置环境变量
set FLASK_ENV=production
set SECRET_KEY=your-secret-key-here-change-in-production

echo 使用Gunicorn启动生产服务器...
echo 服务器地址: http://localhost:5001
echo 按 Ctrl+C 停止服务器

REM 启动Gunicorn服务器
gunicorn -c gunicorn.conf.py wsgi:application

pause
