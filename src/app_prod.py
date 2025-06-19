#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境配置文件
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.translation import translation_bp

def create_app():
    """应用工厂函数"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # 从环境变量读取配置，或使用默认值
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'prod-secret-key-change-me-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    # 生产环境配置
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # 数据库配置
    db_path = os.environ.get('DATABASE_URL', 
                           f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # 连接池预检测
        'pool_recycle': 300,    # 连接回收时间
    }
    
    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(translation_bp, url_prefix='/api')
    
    # 初始化数据库
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": True, "message": "服务器内部错误"}, 500
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发环境
    app.run(host='0.0.0.0', port=5001, debug=True)
