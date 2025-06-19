#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI入口文件 - 用于生产环境部署
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入Flask应用
from src.main import app as application

if __name__ == "__main__":
    # 如果直接运行此文件，仍然使用开发服务器
    application.run(host='0.0.0.0', port=5001, debug=False)
