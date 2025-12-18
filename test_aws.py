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
        
        # 测试简单的文本请求
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Hello, please respond with 'Connection successful!'"
                        }
                    ]
                }
            ]
        }
        
        print("📡 发送测试请求...")
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        # 解析响应
        response_body = json.loads(response['body'].read())
        result = response_body['content'][0]['text']
        
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