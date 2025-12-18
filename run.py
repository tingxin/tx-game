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
    """检查 AWS 配置"""
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    print(f"🌍 AWS 区域: {aws_region}")
    print("🔐 使用 IAM Role 认证")
    print("📋 请确保运行环境具有以下权限:")
    print("   - bedrock:InvokeModel")
    print("   - bedrock:Converse")
    
    # 尝试获取当前身份
    try:
        import boto3
        sts_client = boto3.client('sts', region_name=aws_region)
        identity = sts_client.get_caller_identity()
        print(f"✅ 当前身份: {identity.get('Arn', 'Unknown')}")
        return True
    except Exception as e:
        print(f"⚠️  无法获取 AWS 身份: {str(e)}")
        print("请确保:")
        print("1. 运行环境有正确的 IAM Role")
        print("2. 或者配置了 AWS CLI (aws configure)")
        print("3. 或者设置了环境变量 AWS_PROFILE")
        return False

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