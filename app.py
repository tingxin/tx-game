from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import base64
import json
import os
from werkzeug.utils import secure_filename
import logging
from config import setup_aws_credentials

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置 AWS 凭证
setup_aws_credentials()

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# AWS Bedrock 配置
# 从环境变量获取 AK/SK
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# 初始化 Bedrock 客户端
def get_bedrock_client():
    """获取 Bedrock 客户端"""
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        raise Exception("AWS 凭证未配置，请设置 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY 环境变量")
    
    return boto3.client(
        'bedrock-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image_to_base64(image_path):
    """将图片编码为 base64（用于 Nova 模型）"""
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
        return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image_with_bedrock(image_base64, image_format):
    """使用 AWS Bedrock Nova 模型分析图片"""
    try:
        # Nova 模型请求体格式
        request_body = {
            "inputText": """请详细分析这张图片的内容，包括：
1. 主要物体和场景描述
2. 颜色、构图和视觉元素
3. 可能的情感或氛围
4. 任何文字内容（如果有）
5. 图片的整体质量和特点

请用中文回答，内容要详细且专业。""",
            "textGenerationConfig": {
                "maxTokenCount": 2000,
                "temperature": 0.7,
                "topP": 0.9
            },
            "inferenceConfig": {
                "max_new_tokens": 2000
            },
            "images": [
                {
                    "format": image_format.upper(),
                    "source": {
                        "bytes": image_base64
                    }
                }
            ]
        }

        # 获取 Bedrock 客户端并调用 API
        bedrock_client = get_bedrock_client()
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-pro-v1:0",  # Nova Pro 模型ID
            body=json.dumps(request_body),
            contentType="application/json"
        )

        # 解析响应
        response_body = json.loads(response['body'].read())
        
        # Nova 模型的响应格式
        if 'outputText' in response_body:
            analysis_text = response_body['outputText']
        elif 'results' in response_body and len(response_body['results']) > 0:
            analysis_text = response_body['results'][0]['outputText']
        else:
            # 尝试其他可能的响应格式
            analysis_text = str(response_body)
        
        return analysis_text

    except Exception as e:
        logger.error(f"Bedrock Nova API 调用失败: {str(e)}")
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