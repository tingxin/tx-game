#!/usr/bin/env python3
"""
图片分析器启动脚本
"""

import os
import sys
import subprocess

def check_requirements():
    """检查依赖是否安装"""
    try:
        import flask
        import boto3
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_aws_credentials():
    """检查 AWS 凭证配置"""
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION')
    
    if not all([aws_access_key, aws_secret_key]):
        print("⚠️  AWS 凭证未配置")
        print("请设置环境变量:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("export AWS_DEFAULT_REGION=us-east-1")
        return False
    
    print("✅ AWS 凭证配置检查通过")
    return True

def main():
    print("🚀 启动图片分析器...")
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查 AWS 凭证
    if not check_aws_credentials():
        print("⚠️  继续启动，但 AWS 功能可能无法正常工作")
    
    # 启动应用
    print("🌐 启动 Flask 服务器...")
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()