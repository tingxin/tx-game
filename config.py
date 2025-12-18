"""
AWS 配置文件
可以在这里直接设置 AK/SK，或者使用环境变量
"""

import os

# 方式1: 直接在代码中设置（不推荐用于生产环境）
# 取消注释并填入你的凭证
# AWS_ACCESS_KEY_ID = "your_access_key_id_here"
# AWS_SECRET_ACCESS_KEY = "your_secret_access_key_here"
# AWS_REGION = "us-east-1"

# 方式2: 从环境变量读取（推荐）
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def setup_aws_credentials():
    """设置 AWS 凭证到环境变量"""
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
        os.environ['AWS_REGION'] = AWS_REGION
        return True
    return False