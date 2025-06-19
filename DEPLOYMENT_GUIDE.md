# PPT翻译服务器部署指南

## 开发环境 vs 生产环境

### 开发环境（当前使用）
- 使用Flask内置开发服务器
- 单线程，性能有限
- 适合开发调试
- 会显示警告：`WARNING: This is a development server. Do not use it in a production deployment.`

### 生产环境（推荐）
- 使用Gunicorn WSGI服务器
- 多进程并发处理
- 更好的性能和稳定性
- 适合生产部署

## 启动方式

### 方式1：继续使用开发服务器（简单但不推荐）
```bash
cd src
python main.py
```

### 方式2：使用生产服务器（推荐）

#### Windows系统
```cmd
# 双击运行
start_production.bat

# 或者命令行运行
start_production.bat
```

#### Linux/Mac系统
```bash
# 赋予执行权限
chmod +x start_production.sh

# 运行
./start_production.sh
```

#### 手动启动（任何系统）
```bash
# 安装依赖
pip install -r requirements.txt

# 创建必要目录
mkdir -p logs pids translated_files

# 启动Gunicorn服务器
gunicorn -c gunicorn.conf.py wsgi:application
```

## 配置说明

### Gunicorn配置 (gunicorn.conf.py)
- **工作进程数**: CPU核心数 × 2 + 1
- **绑定地址**: 0.0.0.0:5001
- **超时时间**: 30秒
- **日志**: 保存在 `logs/` 目录
- **PID文件**: 保存在 `pids/` 目录

### 环境变量
可以通过环境变量自定义配置：
- `SECRET_KEY`: Flask密钥（生产环境必须更改）
- `DATABASE_URL`: 数据库连接URL
- `FLASK_ENV`: 设置为 `production`

## 性能优化建议

### 1. 系统资源
- **CPU**: 至少2核心，推荐4核心以上
- **内存**: 至少2GB，推荐4GB以上
- **存储**: SSD硬盘，确保足够空间存储翻译文件

### 2. 网络配置
- 确保稳定的网络连接（调用AI翻译API）
- 考虑使用CDN加速静态文件
- 配置适当的防火墙规则

### 3. 反向代理（可选）
生产环境建议使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 大文件上传支持
        client_max_body_size 50M;
        proxy_request_buffering off;
    }
}
```

## 监控和日志

### 日志文件
- **访问日志**: `logs/access.log`
- **错误日志**: `logs/error.log`

### 监控进程
```bash
# 查看Gunicorn进程
ps aux | grep gunicorn

# 查看PID文件
cat pids/gunicorn.pid

# 重启服务器
kill -HUP $(cat pids/gunicorn.pid)

# 停止服务器
kill $(cat pids/gunicorn.pid)
```

## 安全建议

1. **更改默认密钥**: 修改 `SECRET_KEY` 环境变量
2. **防火墙配置**: 只开放必要端口
3. **定期更新**: 保持依赖包最新版本
4. **备份数据**: 定期备份数据库和翻译文件
5. **监控日志**: 定期检查错误日志

## 故障排除

### 常见问题

1. **端口已被占用**
   ```bash
   # 查找占用端口的进程
   netstat -an | findstr 5001  # Windows
   lsof -i :5001               # Linux/Mac
   ```

2. **权限问题**
   - 确保对 `logs/`, `pids/`, `translated_files/` 目录有写权限
   - Linux/Mac系统可能需要 `chmod 755` 设置权限

3. **依赖问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   ```

4. **内存不足**
   - 减少工作进程数量
   - 增加系统内存

## 容器化部署（Docker）

如果需要使用Docker部署，可以创建以下Dockerfile：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5001

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:application"]
```

这样可以确保环境一致性，便于部署和扩展。
