#!/usr/bin/env python3
"""
AWS 认证配置文件
从 .env 文件读取配置，支持 IAM 角色和 Access Key 两种认证方式
"""

import os
import boto3
from botocore.exceptions import ClientError

class AWSConfig:
    def __init__(self):
        """初始化 AWS 配置"""
        self.auth_method = None
        self.region = None
        self.access_key_id = None
        self.secret_access_key = None
        self.session_token = None
        
        # 加载 .env 配置
        self._load_env_config()
    
    def _load_env_config(self):
        """从 .env 文件加载配置"""
        env_file = '.env'
        
        # 如果 .env 文件存在，读取配置
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # 设置到环境变量中
                            if value and value != 'your_access_key_id_here' and value != 'your_secret_access_key_here':
                                os.environ[key] = value
                
                print("✅ 已加载 .env 配置文件")
                
            except Exception as e:
                print(f"⚠️  .env 文件读取失败: {e}")
        else:
            print("⚠️  未找到 .env 文件，使用环境变量或默认配置")
        
        # 从环境变量读取配置
        self.auth_method = os.environ.get('AWS_AUTH_METHOD', 'iam_role').lower()
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.session_token = os.environ.get('AWS_SESSION_TOKEN')
    
    def setup_credentials(self):
        """设置 AWS 凭证"""
        print("🔐 配置 AWS 认证...")
        
        if self.auth_method == 'iam_role':
            return self._setup_iam_role()
        elif self.auth_method == 'access_key':
            return self._setup_access_key()
        else:
            # 自动检测模式
            return self._auto_detect_auth()
    
    def _setup_iam_role(self):
        """使用 IAM 角色认证"""
        print("🎯 使用 IAM 角色认证模式")
        
        try:
            # 测试 IAM 角色认证
            sts = boto3.client('sts', region_name=self.region)
            identity = sts.get_caller_identity()
            
            arn = identity.get('Arn', '')
            if 'role/' in arn or 'assumed-role/' in arn:
                role_name = arn.split('/')[-1] if 'role/' in arn else arn.split('/')[-2]
                print(f"✅ IAM 角色认证成功: {role_name}")
                print(f"   账户ID: {identity.get('Account')}")
                print(f"   区域: {self.region}")
                return True
            else:
                print("❌ 当前环境未使用 IAM 角色")
                return False
                
        except Exception as e:
            print(f"❌ IAM 角色认证失败: {e}")
            return False
    
    def _setup_access_key(self):
        """使用 Access Key 认证"""
        print("🔑 使用 Access Key 认证模式")
        
        if not self.access_key_id or not self.secret_access_key:
            print("❌ 缺少 Access Key 配置")
            print("请在 .env 文件中设置 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY")
            return False
        
        # 检查是否是占位符
        if (self.access_key_id == 'your_access_key_id_here' or 
            self.secret_access_key == 'your_secret_access_key_here'):
            print("❌ 请在 .env 文件中设置真实的 AWS Access Key")
            return False
        
        try:
            # 使用指定的凭证创建客户端
            sts = boto3.client(
                'sts',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                aws_session_token=self.session_token,
                region_name=self.region
            )
            
            # 测试认证
            identity = sts.get_caller_identity()
            
            print(f"✅ Access Key 认证成功")
            print(f"   用户ARN: {identity.get('Arn')}")
            print(f"   账户ID: {identity.get('Account')}")
            print(f"   区域: {self.region}")
            return True
            
        except Exception as e:
            print(f"❌ Access Key 认证失败: {e}")
            print("请检查 .env 文件中的 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY 是否正确")
            return False
    
    def _auto_detect_auth(self):
        """自动检测认证方式"""
        print("🔍 自动检测认证方式...")
        
        # 1. 优先尝试 IAM 角色
        if self._setup_iam_role():
            self.auth_method = 'iam_role'
            return True
        
        # 2. 尝试 Access Key
        if self.access_key_id and self.secret_access_key:
            if self._setup_access_key():
                self.auth_method = 'access_key'
                return True
        
        # 3. 尝试默认凭证链
        try:
            sts = boto3.client('sts', region_name=self.region)
            identity = sts.get_caller_identity()
            
            print(f"✅ 使用默认 AWS 凭证链")
            print(f"   ARN: {identity.get('Arn')}")
            print(f"   账户ID: {identity.get('Account')}")
            self.auth_method = 'default'
            return True
            
        except Exception as e:
            print(f"❌ 所有认证方式都失败了: {e}")
            self._print_help()
            return False
    
    def _print_help(self):
        """打印帮助信息"""
        print("\n📋 AWS 认证配置帮助:")
        print("\n方式1: IAM 角色 (推荐)")
        print("  - 为 EC2 实例分配 IAM 角色")
        print("  - 设置环境变量: export AWS_AUTH_METHOD=iam_role")
        
        print("\n方式2: Access Key")
        print("  - 设置环境变量:")
        print("    export AWS_AUTH_METHOD=access_key")
        print("    export AWS_ACCESS_KEY_ID=your_access_key")
        print("    export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("    export AWS_REGION=us-east-1")
        
        print("\n方式3: 配置文件")
        print("  - 创建 aws_credentials.conf 文件")
        print("  - 运行: python script.py --config aws_credentials.conf")
        
        print("\n方式4: AWS CLI")
        print("  - 运行: aws configure")
    
    def get_boto3_session(self):
        """获取 boto3 会话"""
        if self.auth_method == 'access_key' and self.access_key_id:
            return boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                aws_session_token=self.session_token,
                region_name=self.region
            )
        else:
            return boto3.Session(region_name=self.region)


def create_sample_config():
    """创建示例配置文件"""
    sample_config = """# AWS 认证配置文件
# 认证方式: iam_role, access_key, auto
AUTH_METHOD=iam_role

# AWS 区域
AWS_REGION=us-east-1

# Access Key 配置 (仅当 AUTH_METHOD=access_key 时使用)
# AWS_ACCESS_KEY_ID=your_access_key_id
# AWS_SECRET_ACCESS_KEY=your_secret_access_key
# AWS_SESSION_TOKEN=your_session_token

# 示例配置:
# 1. 使用 IAM 角色 (推荐):
#    AUTH_METHOD=iam_role
#    AWS_REGION=us-east-1

# 2. 使用 Access Key:
#    AUTH_METHOD=access_key
#    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
#    AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
#    AWS_REGION=us-east-1

# 3. 自动检测:
#    AUTH_METHOD=auto
#    AWS_REGION=us-east-1
"""
    
    with open('aws_credentials.conf', 'w', encoding='utf-8') as f:
        f.write(sample_config)
    
    print("✅ 示例配置文件已创建: aws_credentials.conf")
    print("请编辑此文件并设置你的 AWS 认证信息")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-config':
        create_sample_config()
    else:
        # 测试配置
        config = AWSConfig()
        success = config.setup_credentials()
        
        if success:
            print(f"\n🎉 AWS 认证配置成功!")
            print(f"   认证方式: {config.auth_method}")
            print(f"   区域: {config.region}")
        else:
            print(f"\n❌ AWS 认证配置失败!")