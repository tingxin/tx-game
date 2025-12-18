from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import base64
import json
import os
from werkzeug.utils import secure_filename
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# AWS Bedrock 配置
# 注意：确保你的 AWS 凭证已正确配置
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1'  # 根据你的区域调整
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image_to_base64(image_path):
    """将图片编码为 base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_bedrock(image_base64, image_format):
    """使用 AWS Bedrock Sonnet 4 分析图片"""
    try:
        # 构建请求体
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{image_format}",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": """请详细分析这张图片的内容，包括：
1. 主要物体和场景描述
2. 颜色、构图和视觉元素
3. 可能的情感或氛围
4. 任何文字内容（如果有）
5. 图片的整体质量和特点

请用中文回答，内容要详细且专业。"""
                        }
                    ]
                }
            ]
        }

        # 调用 Bedrock API
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",  # Sonnet 4 模型ID
            body=json.dumps(request_body),
            contentType="application/json"
        )

        # 解析响应
        response_body = json.loads(response['body'].read())
        analysis_text = response_body['content'][0]['text']
        
        return analysis_text

    except Exception as e:
        logger.error(f"Bedrock API 调用失败: {str(e)}")
        raise Exception(f"AI 分析失败: {str(e)}")

@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('.', filename)

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """分析上传的图片"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400
        
        file = request.files['image']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件大小超过限制'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # 获取图片格式
            image_format = filename.rsplit('.', 1)[1].lower()
            if image_format == 'jpg':
                image_format = 'jpeg'
            
            # 编码图片
            image_base64 = encode_image_to_base64(file_path)
            
            # 调用 Bedrock 分析
            analysis = analyze_image_with_bedrock(image_base64, image_format)
            
            # 清理临时文件
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        logger.error(f"图片分析错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'service': 'Image Analyzer API'})

if __name__ == '__main__':
    print("🚀 图片分析服务启动中...")
    print("📝 请确保已配置 AWS 凭证")
    print("🌐 访问 http://localhost:5000 使用应用")
    
    app.run(debug=True, host='0.0.0.0', port=5000)