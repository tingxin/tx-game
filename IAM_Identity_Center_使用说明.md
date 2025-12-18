# AWS IAM Identity Center 用户管理示例

这个项目提供了使用 AWS boto3 在 IAM Identity Center 中管理 kiro 用户的完整示例。

## 文件说明

### 1. `iam_identity_center_example.py`
完整的 IAM Identity Center 用户管理类，包含：
- 创建用户
- 删除用户  
- 列出用户
- 查询用户
- 用户组管理

### 2. `kiro_user_management.py`
简化版本，专门用于 kiro 用户的添加和删除操作。

## 前置要求

### 1. AWS 权限
确保你的 AWS 凭证具有以下权限：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sso:ListInstances",
                "identitystore:CreateUser",
                "identitystore:DeleteUser",
                "identitystore:ListUsers",
                "identitystore:ListGroups",
                "identitystore:CreateGroupMembership"
            ],
            "Resource": "*"
        }
    ]
}
```

### 2. IAM Identity Center 设置
- 确保已启用 AWS IAM Identity Center
- 记录你的 Identity Store ID 和 Instance ARN

### 3. Python 依赖
```bash
pip install boto3
```

## 使用方法

### 快速开始 - 使用简化版本
```bash
python kiro_user_management.py
```

### 完整功能 - 使用完整版本
```bash
python iam_identity_center_example.py
```

### 单独使用函数
```python
from kiro_user_management import add_kiro_user, delete_kiro_user, check_kiro_user_exists

# 检查用户是否存在
if not check_kiro_user_exists():
    # 添加用户
    user_id = add_kiro_user()
    print(f"用户创建成功，ID: {user_id}")

# 删除用户
delete_kiro_user()
```

## API 参考

### 主要函数

#### `add_kiro_user()`
添加 kiro 用户到 IAM Identity Center
- **返回**: 用户ID (成功) 或 None (失败)
- **用户信息**:
  - 用户名: kiro
  - 显示名: Kiro Assistant  
  - 邮箱: kiro@company.com

#### `delete_kiro_user()`
删除 kiro 用户
- **返回**: True (成功) 或 False (失败)

#### `check_kiro_user_exists()`
检查 kiro 用户是否存在
- **返回**: True (存在) 或 False (不存在)

#### `get_kiro_user_id()`
获取 kiro 用户的 ID
- **返回**: 用户ID (存在) 或 None (不存在)

## 错误处理

常见错误和解决方案：

### 1. `ConflictException`
用户已存在，代码会自动处理并返回现有用户ID。

### 2. `AccessDeniedException`
权限不足，检查 AWS 凭证和 IAM 权限。

### 3. `ResourceNotFoundException`
IAM Identity Center 未启用或配置错误。

### 4. `ValidationException`
输入参数格式错误，检查邮箱格式等。

## 自定义配置

如需修改用户信息，编辑 `add_kiro_user()` 函数中的参数：

```python
response = identity_store_client.create_user(
    IdentityStoreId=identity_store_id,
    UserName="your_username",           # 修改用户名
    DisplayName="Your Display Name",    # 修改显示名
    Name={
        'GivenName': "First",          # 修改名字
        'FamilyName': "Last"           # 修改姓氏
    },
    Emails=[
        {
            'Value': "your@email.com", # 修改邮箱
            'Type': 'work',
            'Primary': True
        }
    ]
)
```

## 注意事项

1. **生产环境**: 不要在代码中硬编码 AWS 凭证，使用 IAM 角色或环境变量
2. **邮箱唯一性**: 每个用户的邮箱必须唯一
3. **用户名唯一性**: 每个用户名在 Identity Store 中必须唯一
4. **权限最小化**: 只授予必要的 IAM 权限

## 扩展功能

完整版本 (`iam_identity_center_example.py`) 还支持：
- 批量用户管理
- 用户组操作
- 用户属性更新
- 更详细的错误处理和日志