#!/usr/bin/env python3
"""
简化版 IAM Identity Center kiro 用户管理
专门用于添加和删除 kiro 用户
"""

import boto3
import os
from botocore.exceptions import ClientError

def setup_aws_credentials():
    """设置 AWS 凭证"""
    # 方式1: 从环境变量读取（推荐）
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    if aws_access_key and aws_secret_key:
        print(f"✅ 使用环境变量中的 AWS 凭证，区域: {aws_region}")
        return True
    
    # 方式2: 使用 AWS CLI 配置或 IAM 角色
    try:
        # 测试是否有有效的凭证
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ 使用默认 AWS 凭证，账户: {identity.get('Account')}")
        return True
    except Exception as e:
        print(f"❌ AWS 凭证配置错误: {e}")
        print("\n请配置 AWS 凭证:")
        print("1. 设置环境变量:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_REGION=us-east-1")
        print("2. 或运行: aws configure")
        return False

def get_sso_instance_info():
    """获取 SSO 实例信息"""
    sso_admin_client = boto3.client('sso-admin')
    
    response = sso_admin_client.list_instances()
    if not response['Instances']:
        raise Exception("未找到 SSO 实例")
    
    instance = response['Instances'][0]
    return instance['InstanceArn'], instance['IdentityStoreId']

def add_kiro_user():
    """添加 kiro 用户到 IAM Identity Center"""
    print("🔄 正在添加 kiro 用户...")
    
    # 设置凭证
    setup_aws_credentials()
    
    try:
        # 获取 SSO 实例信息
        instance_arn, identity_store_id = get_sso_instance_info()
        
        # 创建 Identity Store 客户端
        identity_store_client = boto3.client('identitystore')
        
        # 创建 kiro 用户
        response = identity_store_client.create_user(
            IdentityStoreId=identity_store_id,
            UserName="kiro",
            DisplayName="Kiro Assistant",
            Name={
                'GivenName': "Kiro",
                'FamilyName': "Assistant"
            },
            Emails=[
                {
                    'Value': "kiro@company.com",
                    'Type': 'work',
                    'Primary': True
                }
            ]
        )
        
        user_id = response['UserId']
        print(f"✅ kiro 用户创建成功!")
        print(f"   用户ID: {user_id}")
        print(f"   用户名: kiro")
        print(f"   邮箱: kiro@company.com")
        
        return user_id
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print("⚠️  kiro 用户已存在")
            return get_kiro_user_id()
        else:
            print(f"❌ 创建 kiro 用户失败: {e}")
            return None

def delete_kiro_user():
    """删除 kiro 用户"""
    print("🔄 正在删除 kiro 用户...")
    
    # 设置凭证
    setup_aws_credentials()
    
    try:
        # 获取 SSO 实例信息
        instance_arn, identity_store_id = get_sso_instance_info()
        
        # 创建 Identity Store 客户端
        identity_store_client = boto3.client('identitystore')
        
        # 获取 kiro 用户ID
        user_id = get_kiro_user_id()
        if not user_id:
            print("❌ 未找到 kiro 用户")
            return False
        
        # 删除用户
        identity_store_client.delete_user(
            IdentityStoreId=identity_store_id,
            UserId=user_id
        )
        
        print(f"✅ kiro 用户删除成功! (ID: {user_id})")
        return True
        
    except ClientError as e:
        print(f"❌ 删除 kiro 用户失败: {e}")
        return False

def get_kiro_user_id():
    """获取 kiro 用户ID"""
    try:
        # 获取 SSO 实例信息
        instance_arn, identity_store_id = get_sso_instance_info()
        
        # 创建 Identity Store 客户端
        identity_store_client = boto3.client('identitystore')
        
        # 查找 kiro 用户
        response = identity_store_client.list_users(
            IdentityStoreId=identity_store_id,
            Filters=[
                {
                    'AttributePath': 'UserName',
                    'AttributeValue': 'kiro'
                }
            ]
        )
        
        if response['Users']:
            user = response['Users'][0]
            return user['UserId']
        else:
            return None
            
    except ClientError as e:
        print(f"❌ 查询 kiro 用户失败: {e}")
        return None

def check_kiro_user_exists():
    """检查 kiro 用户是否存在"""
    user_id = get_kiro_user_id()
    if user_id:
        print(f"✅ kiro 用户存在 (ID: {user_id})")
        return True
    else:
        print("❌ kiro 用户不存在")
        return False

if __name__ == '__main__':
    print("🚀 Kiro 用户管理工具")
    print("=" * 30)
    
    # 检查用户是否存在
    print("\n1️⃣ 检查 kiro 用户状态:")
    exists = check_kiro_user_exists()
    
    if not exists:
        # 添加用户
        print("\n2️⃣ 添加 kiro 用户:")
        add_kiro_user()
    else:
        # 用户已存在，询问是否删除
        print("\n2️⃣ kiro 用户已存在，演示删除操作:")
        delete_kiro_user()
        
        # 重新添加
        print("\n3️⃣ 重新添加 kiro 用户:")
        add_kiro_user()