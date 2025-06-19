# Gunicorn配置文件
# 生产环境部署配置

import multiprocessing
import os

# 服务器配置
bind = "0.0.0.0:5001"  # 绑定地址和端口
backlog = 2048         # 等待连接的队列大小

# 工作进程配置
workers = multiprocessing.cpu_count() * 2 + 1  # 工作进程数量
worker_class = "sync"   # 工作进程类型
worker_connections = 1000  # 每个工作进程的最大连接数
timeout = 30           # 工作进程超时时间
keepalive = 2          # 保持连接时间

# 安全配置
max_requests = 1000    # 每个工作进程最大请求数
max_requests_jitter = 50  # 随机化重启
preload_app = True     # 预加载应用

# 日志配置
loglevel = 'info'
accesslog = 'logs/access.log'  # 访问日志
errorlog = 'logs/error.log'    # 错误日志
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程管理
pidfile = 'pids/gunicorn.pid'
daemon = False  # 不以守护进程运行（便于管理）

# 性能优化 - 根据操作系统调整
if os.name == 'posix':  # Linux/Mac
    worker_tmp_dir = '/dev/shm'  # 使用内存作为临时目录
else:  # Windows
    worker_tmp_dir = None

# 用户和组（生产环境中建议使用专用用户，仅限Linux）
# user = 'www-data'
# group = 'www-data'

# SSL配置（如果需要HTTPS）
# certfile = '/path/to/cert.pem'
# keyfile = '/path/to/key.pem'

# 其他配置
enable_stdio_inheritance = True
