#!/usr/bin/env python3
"""
测试 AWS Bedrock 连接
"""

import os
import boto3
import json
from config import setup_aws_credentials

def test_bedrock_connection():
    """测试 Bedrock 连接"""
    print("🔍 测试 AWS Bedrock 连接...")
    
    # 设置凭证
    setup_aws_credentials()
    
    # 检查凭证
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ AWS 凭证未配置")
        return False
    
    print(f"✅ 凭证已配置 (Region: {aws_region})")
    
    try:
        # 创建 Bedrock 客户端
        bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # 测试 Nova 模型的文本请求
        request_body = {
            "inputText": "Hello, please respond with 'Connection successful!'",
            "textGenerationConfig": {
                "maxTokenCount": 100,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        print("📡 发送测试请求到 Nova 模型...")
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        # 解析 Nova 响应
        response_body = json.loads(response['body'].read())
        if 'outputText' in response_body:
            result = response_body['outputText']
        elif 'results' in response_body and len(response_body['results']) > 0:
            result = response_body['results'][0]['outputText']
        else:
            result = str(response_body)
        
        print(f"✅ 连接成功！响应: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("\n可能的原因:")
        print("1. AWS 凭证错误")
        print("2. 没有 Bedrock 访问权限")
        print("3. 区域不支持 Claude 模型")
        print("4. 网络连接问题")
        return False

if __name__ == '__main__':
    test_bedrock_connection()