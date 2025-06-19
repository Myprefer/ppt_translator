# translation_routes.py

from flask import Blueprint, request, jsonify, send_file, Response
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
import sys
import json
import time
import threading

# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Import our custom modules from the project root
try:
    from ppt_text_extractor import extract_text_from_ppt
    from llm_translator import LLMTranslator
    from ppt_reconstructor import reconstruct_ppt
except ImportError:
    # Fallback: try importing from the same directory
    import importlib.util
    
    def load_module_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load modules from project root
    ppt_extractor = load_module_from_path("ppt_text_extractor", os.path.join(project_root, "ppt_text_extractor.py"))
    llm_translator = load_module_from_path("llm_translator", os.path.join(project_root, "llm_translator.py"))
    ppt_reconstructor = load_module_from_path("ppt_reconstructor", os.path.join(project_root, "ppt_reconstructor.py"))
    
    extract_text_from_ppt = ppt_extractor.extract_text_from_ppt
    LLMTranslator = llm_translator.LLMTranslator
    reconstruct_ppt = ppt_reconstructor.reconstruct_ppt

translation_bp = Blueprint('translation', __name__)

UPLOAD_FOLDER = tempfile.gettempdir()
# 本地存储目录
LOCAL_STORAGE_FOLDER = os.path.join(project_root, 'translated_files')
ALLOWED_EXTENSIONS = {'pptx'}

# 确保本地存储目录存在
if not os.path.exists(LOCAL_STORAGE_FOLDER):
    os.makedirs(LOCAL_STORAGE_FOLDER)

# 全局变量存储翻译进度
translation_progress = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_progress(task_id, current_slide, total_slides, status_text):
    """更新翻译进度"""
    progress = (current_slide / total_slides) * 100 if total_slides > 0 else 0
    translation_progress[task_id] = {
        'current_slide': current_slide,
        'total_slides': total_slides,
        'progress': progress,
        'status': status_text,
        'completed': current_slide >= total_slides
    }

@translation_bp.route('/translate', methods=['POST'])
def translate_ppt():
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({'error': True, 'message': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': True, 'message': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': True, 'message': '不支持的文件格式，请上传.pptx文件'}), 400
        
        # 获取其他参数
        source_language = request.form.get('source_language', 'auto')
        target_language = request.form.get('target_language', 'zh')
        api_key = request.form.get('api_key')
        model = request.form.get('model', 'qwen-turbo')  # 默认使用qwen-turbo
        
        if not api_key:
            return jsonify({'error': True, 'message': '请提供Qwen API密钥'}), 400
        
        # 验证模型
        if not LLMTranslator.is_valid_model(model):
            return jsonify({
                'error': True, 
                'message': f'不支持的模型: {model}. 支持的模型: {list(LLMTranslator.get_available_models().keys())}'
            }), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(input_path)
        
        # 在后台线程中执行翻译
        def translate_task():
            try:
                # 1. 提取PPT文本
                update_progress(task_id, 0, 1, '正在提取PPT文本...')
                extracted_data = extract_text_from_ppt(input_path)
                
                if not extracted_data:
                    translation_progress[task_id] = {
                        'error': True,
                        'message': 'PPT文件中没有找到可翻译的文本'
                    }
                    return
                
                total_slides = len(extracted_data)
                update_progress(task_id, 0, total_slides, f'发现 {total_slides} 页幻灯片，开始翻译...')
                
                # 2. 初始化翻译器（使用指定的模型）
                translator = LLMTranslator(api_key=api_key, model=model)
                
                # 3. 翻译文本
                translated_data = []
                for i, slide_data in enumerate(extracted_data):
                    current_slide = i + 1
                    update_progress(task_id, current_slide, total_slides, f'正在翻译第 {current_slide}/{total_slides} 页...')
                    
                    slide_translated = {
                        "slide_index": slide_data["slide_index"],
                        "texts": []
                    }
                    
                    # 收集当前幻灯片的所有文本作为上下文
                    slide_texts = [text_info["original_text"] for text_info in slide_data["texts"]]
                    
                    for text_info in slide_data["texts"]:
                        original_text = text_info["original_text"]
                        
                        # 使用其他文本作为上下文
                        context_texts = [t for t in slide_texts if t != original_text][:3]  # 限制上下文数量
                        
                        # 翻译文本
                        translated_text = translator.translate_text(
                            original_text,
                            target_language=get_language_name(target_language),
                            context_texts=context_texts if context_texts else None
                        )
                        
                        if translated_text:
                            text_info_copy = text_info.copy()
                            text_info_copy["translated_text"] = translated_text
                            slide_translated["texts"].append(text_info_copy)
                    
                    if slide_translated["texts"]:
                        translated_data.append(slide_translated)
                
                # 4. 重构PPT
                update_progress(task_id, total_slides, total_slides, '正在重构PPT文件...')
                output_filename = f"translated_{unique_filename}"
                # 临时文件路径（用于下载）
                temp_output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                # 本地存储路径
                local_filename = f"translated_{time.strftime('%Y%m%d_%H%M%S')}_{filename}"
                local_output_path = os.path.join(LOCAL_STORAGE_FOLDER, local_filename)
                
                # 先重构到临时目录
                reconstruct_ppt(input_path, translated_data, temp_output_path)
                
                # 保存到本地存储目录
                update_progress(task_id, total_slides, total_slides, '正在保存到本地...')
                import shutil
                shutil.copy2(temp_output_path, local_output_path)
                
                # 5. 标记完成
                translation_progress[task_id] = {
                    'current_slide': total_slides,
                    'total_slides': total_slides,
                    'progress': 100,
                    'status': '翻译完成！文件已保存到本地',
                    'completed': True,
                    'download_url': f"/api/download/{output_filename}",
                    'original_filename': filename,
                    'local_filename': local_filename,
                    'local_path': local_output_path
                }
                
            except Exception as e:
                translation_progress[task_id] = {
                    'error': True,
                    'message': f'翻译过程中出现错误: {str(e)}'
                }
            
            finally:
                # 清理上传的文件
                if os.path.exists(input_path):
                    os.remove(input_path)
        
        # 启动后台翻译任务
        thread = threading.Thread(target=translate_task)
        thread.daemon = True
        thread.start()
        
        # 立即返回任务ID
        return jsonify({
            'error': False,
            'task_id': task_id,
            'message': '翻译任务已开始，请查看进度'
        })
    
    except Exception as e:
        return jsonify({'error': True, 'message': f'服务器错误: {str(e)}'}), 500

@translation_bp.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': True, 'message': '文件不存在'}), 404
        
        # 获取原始文件名（去掉UUID前缀）
        original_filename = filename.split('_', 1)[1] if '_' in filename else filename
        download_name = f"translated_{original_filename}"
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    
    except Exception as e:
        return jsonify({'error': True, 'message': f'下载失败: {str(e)}'}), 500

def get_language_name(language_code):
    """将语言代码转换为语言名称"""
    language_map = {
        'zh': '中文',
        'en': 'English',
        'ja': '日语',
        'ko': '韩语',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'ru': 'Russian',
        'auto': 'auto'
    }
    return language_map.get(language_code, 'English')

@translation_bp.route('/progress/<task_id>')
def get_progress(task_id):
    """获取翻译进度"""
    def generate():
        while task_id in translation_progress:
            data = translation_progress[task_id]
            yield f"data: {json.dumps(data)}\n\n"
            
            if data.get('completed', False) or data.get('error', False):
                # 翻译完成或出错后稍等一下再清理进度数据
                time.sleep(2)
                if task_id in translation_progress:
                    del translation_progress[task_id]
                break
                
            time.sleep(1)  # 每秒更新一次
    
    return Response(generate(), content_type='text/event-stream')

@translation_bp.route('/local-files')
def list_local_files():
    """获取本地保存的翻译文件列表"""
    try:
        if not os.path.exists(LOCAL_STORAGE_FOLDER):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(LOCAL_STORAGE_FOLDER):
            if filename.endswith('.pptx'):
                file_path = os.path.join(LOCAL_STORAGE_FOLDER, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_ctime)),
                    'download_url': f"/api/download-local/{filename}"
                })
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['created_time'], reverse=True)
        
        return jsonify({
            'error': False,
            'files': files,
            'total_count': len(files)
        })
    
    except Exception as e:
        return jsonify({'error': True, 'message': f'获取文件列表失败: {str(e)}'}), 500

@translation_bp.route('/download-local/<filename>')
def download_local_file(filename):
    """下载本地保存的翻译文件"""
    try:
        # 安全检查，防止路径遍历攻击
        filename = secure_filename(filename)
        file_path = os.path.join(LOCAL_STORAGE_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': True, 'message': '文件不存在'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    
    except Exception as e:
        return jsonify({'error': True, 'message': f'下载失败: {str(e)}'}), 500

@translation_bp.route('/delete-local/<filename>', methods=['DELETE'])
def delete_local_file(filename):
    """删除本地保存的翻译文件"""
    try:
        # 安全检查，防止路径遍历攻击
        filename = secure_filename(filename)
        file_path = os.path.join(LOCAL_STORAGE_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': True, 'message': '文件不存在'}), 404
        
        os.remove(file_path)
        
        return jsonify({
            'error': False,
            'message': '文件删除成功'
        })
    
    except Exception as e:
        return jsonify({'error': True, 'message': f'删除失败: {str(e)}'}), 500

@translation_bp.route('/models')
def get_available_models():
    """获取可用的翻译模型列表"""
    try:
        models = LLMTranslator.get_available_models()
        return jsonify({
            'error': False,
            'models': models
        })
    except Exception as e:
        return jsonify({'error': True, 'message': f'获取模型列表失败: {str(e)}'}), 500

