#!/usr/bin/env python3
"""
AWS IAM Identity Center 用户管理示例
使用 boto3 添加和删除 kiro 用户
"""

import boto3
import json
from botocore.exceptions import ClientError
from config import setup_aws_credentials

class IAMIdentityCenterManager:
    def __init__(self, region='us-east-1'):
        """初始化 IAM Identity Center 管理器"""
        # 设置 AWS 凭证
        setup_aws_credentials()
        
        # 创建 SSO Admin 客户端
        self.sso_admin_client = boto3.client('sso-admin', region_name=region)
        
        # 创建 Identity Store 客户端
        self.identity_store_client = boto3.client('identitystore', region_name=region)
        
        # 获取 Identity Store ID 和 Instance ARN
        self.identity_store_id = None
        self.instance_arn = None
        self._get_sso_instance_info()
    
    def _get_sso_instance_info(self):
        """获取 SSO 实例信息"""
        try:
            response = self.sso_admin_client.list_instances()
            if response['Instances']:
                instance = response['Instances'][0]
                self.instance_arn = instance['InstanceArn']
                self.identity_store_id = instance['IdentityStoreId']
                print(f"✅ 找到 SSO 实例: {self.instance_arn}")
                print(f"✅ Identity Store ID: {self.identity_store_id}")
            else:
                raise Exception("未找到 SSO 实例")
        except ClientError as e:
            print(f"❌ 获取 SSO 实例信息失败: {e}")
            raise
    
    def create_user(self, username="kiro", display_name="Kiro User", 
                   email="kiro@example.com", given_name="Kiro", 
                   family_name="User"):
        """创建用户"""
        try:
            print(f"🔄 正在创建用户: {username}")
            
            # 创建用户
            response = self.identity_store_client.create_user(
                IdentityStoreId=self.identity_store_id,
                UserName=username,
                DisplayName=display_name,
                Name={
                    'GivenName': given_name,
                    'FamilyName': family_name
                },
                Emails=[
                    {
                        'Value': email,
                        'Type': 'work',
                        'Primary': True
                    }
                ]
            )
            
            user_id = response['UserId']
            print(f"✅ 用户创建成功!")
            print(f"   用户名: {username}")
            print(f"   用户ID: {user_id}")
            print(f"   显示名: {display_name}")
            print(f"   邮箱: {email}")
            
            return user_id
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConflictException':
                print(f"⚠️  用户 {username} 已存在")
                # 尝试获取现有用户信息
                return self.get_user_by_username(username)
            else:
                print(f"❌ 创建用户失败: {e}")
                return None
    
    def delete_user(self, username="kiro"):
        """删除用户"""
        try:
            print(f"🔄 正在删除用户: {username}")
            
            # 先获取用户ID
            user_id = self.get_user_by_username(username)
            if not user_id:
                print(f"❌ 未找到用户: {username}")
                return False
            
            # 删除用户
            self.identity_store_client.delete_user(
                IdentityStoreId=self.identity_store_id,
                UserId=user_id
            )
            
            print(f"✅ 用户删除成功: {username} (ID: {user_id})")
            return True
            
        except ClientError as e:
            print(f"❌ 删除用户失败: {e}")
            return False
    
    def get_user_by_username(self, username):
        """根据用户名获取用户ID"""
        try:
            response = self.identity_store_client.list_users(
                IdentityStoreId=self.identity_store_id,
                Filters=[
                    {
                        'AttributePath': 'UserName',
                        'AttributeValue': username
                    }
                ]
            )
            
            if response['Users']:
                user = response['Users'][0]
                print(f"📋 找到用户: {user['UserName']} (ID: {user['UserId']})")
                return user['UserId']
            else:
                print(f"❌ 未找到用户: {username}")
                return None
                
        except ClientError as e:
            print(f"❌ 查询用户失败: {e}")
            return None
    
    def list_users(self):
        """列出所有用户"""
        try:
            print("🔄 正在获取用户列表...")
            
            response = self.identity_store_client.list_users(
                IdentityStoreId=self.identity_store_id
            )
            
            users = response['Users']
            print(f"📋 找到 {len(users)} 个用户:")
            
            for user in users:
                print(f"   - {user['UserName']} ({user.get('DisplayName', 'N/A')}) - ID: {user['UserId']}")
            
            return users
            
        except ClientError as e:
            print(f"❌ 获取用户列表失败: {e}")
            return []
    
    def assign_user_to_group(self, username, group_name):
        """将用户分配到组"""
        try:
            print(f"🔄 正在将用户 {username} 添加到组 {group_name}")
            
            # 获取用户ID
            user_id = self.get_user_by_username(username)
            if not user_id:
                return False
            
            # 获取组ID
            group_id = self.get_group_by_name(group_name)
            if not group_id:
                return False
            
            # 添加用户到组
            self.identity_store_client.create_group_membership(
                IdentityStoreId=self.identity_store_id,
                GroupId=group_id,
                MemberId={
                    'UserId': user_id
                }
            )
            
            print(f"✅ 用户 {username} 已添加到组 {group_name}")
            return True
            
        except ClientError as e:
            print(f"❌ 添加用户到组失败: {e}")
            return False
    
    def get_group_by_name(self, group_name):
        """根据组名获取组ID"""
        try:
            response = self.identity_store_client.list_groups(
                IdentityStoreId=self.identity_store_id,
                Filters=[
                    {
                        'AttributePath': 'DisplayName',
                        'AttributeValue': group_name
                    }
                ]
            )
            
            if response['Groups']:
                group = response['Groups'][0]
                return group['GroupId']
            else:
                print(f"❌ 未找到组: {group_name}")
                return None
                
        except ClientError as e:
            print(f"❌ 查询组失败: {e}")
            return None


def main():
    """主函数 - 演示用户管理操作"""
    print("🚀 AWS IAM Identity Center 用户管理示例")
    print("=" * 50)
    
    try:
        # 初始化管理器
        manager = IAMIdentityCenterManager()
        
        # 1. 列出现有用户
        print("\n1️⃣ 列出现有用户:")
        manager.list_users()
        
        # 2. 创建 kiro 用户
        print("\n2️⃣ 创建 kiro 用户:")
        user_id = manager.create_user(
            username="kiro",
            display_name="Kiro Assistant",
            email="kiro@company.com",
            given_name="Kiro",
            family_name="Assistant"
        )
        
        if user_id:
            # 3. 再次列出用户，确认创建成功
            print("\n3️⃣ 确认用户创建:")
            manager.list_users()
            
            # 4. 可选：将用户添加到组（如果有组的话）
            # manager.assign_user_to_group("kiro", "Developers")
            
            # 5. 删除用户（演示）
            print("\n4️⃣ 删除 kiro 用户:")
            manager.delete_user("kiro")
            
            # 6. 最终确认
            print("\n5️⃣ 最终用户列表:")
            manager.list_users()
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")


if __name__ == '__main__':
    main()