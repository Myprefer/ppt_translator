# PPT翻译软件 - 项目文档

## 项目概述

这是一个基于LLM API的PPT文字翻译软件，能够提取PPT中的文字内容并考虑上下文进行高质量翻译。该软件使用Python开发，集成了Qwen API进行翻译，并提供了现代化的Web界面。

## 技术栈

- **后端**: Python 3.11, Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite
- **PPT处理**: python-pptx
- **翻译API**: Qwen API (OpenAI格式)
- **部署**: Flask开发服务器

## 核心功能

### 1. PPT文本提取
- 支持.pptx格式文件
- 提取幻灯片中的所有文本内容
- 保留文本的格式信息（字体、大小、颜色等）
- 支持表格内容提取

### 2. 智能翻译
- 集成Qwen API进行高质量翻译
- 支持上下文感知翻译
- 支持多种语言对（中文、英语、日语、韩语、法语、德语、西班牙语、俄语）
- 自动检测源语言

### 3. PPT重构
- 将翻译后的文本重新插入PPT
- 尽可能保持原有格式
- 支持文本框和表格内容替换

### 4. 用户界面
- 现代化的Web界面设计
- 拖拽上传文件支持
- 实时翻译进度显示
- 响应式设计，支持移动设备

## 项目结构

```
ppt_translator/
├── src/
│   ├── main.py                 # Flask应用主文件
│   ├── static/
│   │   └── index.html         # 前端界面
│   ├── routes/
│   │   ├── user.py           # 用户相关路由
│   │   └── translation.py    # 翻译相关路由
│   ├── models/
│   │   └── user.py           # 数据库模型
│   └── database/
│       └── app.db            # SQLite数据库
├── ppt_text_extractor.py      # PPT文本提取模块
├── llm_translator.py          # LLM翻译模块
├── ppt_reconstructor.py       # PPT重构模块
├── requirements.txt           # 依赖包列表
└── venv/                      # 虚拟环境
```

## 安装和运行

### 1. 环境准备
```bash
cd ppt_translator
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python src/main.py
```

### 3. 访问应用
打开浏览器访问: http://localhost:5001

## 使用说明

1. **上传PPT文件**: 点击上传区域或拖拽.pptx文件
2. **选择语言**: 设置源语言和目标语言
3. **输入API密钥**: 提供有效的Qwen API密钥
4. **开始翻译**: 点击"开始翻译"按钮
5. **下载结果**: 翻译完成后下载翻译后的PPT文件

## API接口

### POST /api/translate
翻译PPT文件

**请求参数**:
- `file`: PPT文件 (.pptx)
- `source_language`: 源语言代码
- `target_language`: 目标语言代码
- `api_key`: Qwen API密钥

**响应**:
```json
{
  "error": false,
  "message": "翻译完成",
  "download_url": "/api/download/filename",
  "original_filename": "original.pptx"
}
```

### GET /api/download/<filename>
下载翻译后的文件

## 测试

项目包含完整的集成测试：

```bash
python main_integration.py
```

测试覆盖：
- PPT文本提取功能
- 翻译功能（模拟测试）
- PPT重构功能
- 完整流程集成测试


