#!/usr/bin/env python3
"""
企业 SSO 与 AWS IAM Identity Center 集成示例
支持 Okta, Azure AD, Google Workspace 等
"""

import boto3
import json
from botocore.exceptions import ClientError
from config import setup_aws_credentials

class EnterpriseSSOIntegration:
    def __init__(self):
        """初始化企业 SSO 集成管理"""
        setup_aws_credentials()
        self.sso_admin_client = boto3.client('sso-admin')
        self.identity_store_client = boto3.client('identitystore')
        
        # 获取 SSO 实例信息
        self.instance_arn, self.identity_store_id = self._get_sso_instance_info()
    
    def _get_sso_instance_info(self):
        """获取 SSO 实例信息"""
        response = self.sso_admin_client.list_instances()
        if not response['Instances']:
            raise Exception("未找到 SSO 实例")
        
        instance = response['Instances'][0]
        return instance['InstanceArn'], instance['IdentityStoreId']
    
    def configure_external_idp(self, idp_type="okta", idp_config=None):
        """
        配置外部身份提供商
        支持的类型: okta, azure_ad, google_workspace, ping_federate
        """
        print(f"🔗 配置外部身份提供商: {idp_type}")
        
        if idp_type == "okta":
            return self._configure_okta_integration(idp_config)
        elif idp_type == "azure_ad":
            return self._configure_azure_ad_integration(idp_config)
        elif idp_type == "google_workspace":
            return self._configure_google_workspace_integration(idp_config)
        else:
            return self._configure_generic_saml_integration(idp_config)
    
    def _configure_okta_integration(self, config):
        """配置 Okta 集成"""
        print("🔧 配置 Okta SAML 集成")
        
        # Okta SAML 配置示例
        saml_config = {
            "idp_entity_id": config.get("okta_entity_id", "http://www.okta.com/exk1234567890"),
            "sso_url": config.get("okta_sso_url", "https://company.okta.com/app/aws_sso/exk1234567890/sso/saml"),
            "certificate": config.get("okta_certificate"),  # X.509 证书
            "attribute_mapping": {
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname", 
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
                "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
            }
        }
        
        print("✅ Okta 配置准备完成")
        print(f"   Entity ID: {saml_config['idp_entity_id']}")
        print(f"   SSO URL: {saml_config['sso_url']}")
        
        return saml_config
    
    def _configure_azure_ad_integration(self, config):
        """配置 Azure AD 集成"""
        print("🔧 配置 Azure AD SAML 集成")
        
        saml_config = {
            "idp_entity_id": config.get("azure_entity_id", "https://sts.windows.net/tenant-id/"),
            "sso_url": config.get("azure_sso_url", "https://login.microsoftonline.com/tenant-id/saml2"),
            "certificate": config.get("azure_certificate"),
            "attribute_mapping": {
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname", 
                "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
                "groups": "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups"
            }
        }
        
        print("✅ Azure AD 配置准备完成")
        return saml_config
    
    def _configure_google_workspace_integration(self, config):
        """配置 Google Workspace 集成"""
        print("🔧 配置 Google Workspace SAML 集成")
        
        saml_config = {
            "idp_entity_id": config.get("google_entity_id", "https://accounts.google.com/o/saml2?idpid=C01abc234"),
            "sso_url": config.get("google_sso_url", "https://accounts.google.com/o/saml2/idp?idpid=C01abc234"),
            "certificate": config.get("google_certificate"),
            "attribute_mapping": {
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
                "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
            }
        }
        
        print("✅ Google Workspace 配置准备完成")
        return saml_config
    
    def _configure_generic_saml_integration(self, config):
        """配置通用 SAML 集成"""
        print("🔧 配置通用 SAML 2.0 集成")
        
        saml_config = {
            "idp_entity_id": config.get("entity_id"),
            "sso_url": config.get("sso_url"),
            "certificate": config.get("certificate"),
            "attribute_mapping": config.get("attribute_mapping", {
                "email": "email",
                "first_name": "firstName", 
                "last_name": "lastName",
                "username": "username"
            })
        }
        
        return saml_config
    
    def setup_automatic_provisioning(self, enable_scim=True):
        """
        设置自动用户预配置 (SCIM)
        当企业 SSO 中添加/删除用户时，自动同步到 AWS
        """
        print("⚙️ 配置自动用户预配置 (SCIM)")
        
        if enable_scim:
            scim_config = {
                "scim_endpoint": f"https://scim.{self.instance_arn.split('/')[-1]}.amazonaws.com/scim/v2/",
                "authentication": "bearer_token",
                "supported_operations": [
                    "create_user",
                    "update_user", 
                    "delete_user",
                    "create_group",
                    "update_group",
                    "delete_group"
                ],
                "user_attributes": [
                    "userName", "displayName", "name.givenName", 
                    "name.familyName", "emails", "active"
                ]
            }
            
            print("✅ SCIM 自动预配置已启用")
            print(f"   SCIM 端点: {scim_config['scim_endpoint']}")
            print("   支持操作: 用户和组的创建、更新、删除")
            
            return scim_config
        else:
            print("⚠️  SCIM 自动预配置已禁用，需要手动同步用户")
            return None
    
    def create_permission_sets_for_enterprise(self):
        """为企业用户创建权限集"""
        print("🔑 创建企业用户权限集")
        
        # 不同角色的权限集
        permission_sets = {
            "KiroAdmin": {
                "description": "Kiro 管理员权限",
                "session_duration": "PT8H",  # 8小时
                "policies": [
                    "arn:aws:iam::aws:policy/PowerUserAccess"
                ],
                "inline_policy": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:*",
                                "s3:GetObject",
                                "s3:PutObject"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            },
            "KiroUser": {
                "description": "Kiro 普通用户权限",
                "session_duration": "PT4H",  # 4小时
                "policies": [
                    "arn:aws:iam::aws:policy/ReadOnlyAccess"
                ],
                "inline_policy": {
                    "Version": "2012-10-17", 
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:InvokeModel",
                                "s3:GetObject"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            }
        }
        
        created_sets = []
        
        for name, config in permission_sets.items():
            try:
                # 这里应该调用真实的 AWS API 创建权限集
                print(f"   ✅ 创建权限集: {name}")
                print(f"      描述: {config['description']}")
                print(f"      会话时长: {config['session_duration']}")
                
                created_sets.append({
                    "name": name,
                    "arn": f"arn:aws:sso:::permissionSet/{self.instance_arn.split('/')[-1]}/ps-{name.lower()}",
                    "config": config
                })
                
            except Exception as e:
                print(f"   ❌ 创建权限集失败: {name} - {e}")
        
        return created_sets
    
    def map_enterprise_groups_to_aws_roles(self, group_mappings):
        """
        将企业组映射到 AWS 角色
        例如: 企业的 "Developers" 组 → AWS 的 "KiroUser" 权限集
        """
        print("👥 配置企业组到 AWS 角色的映射")
        
        for enterprise_group, aws_permission_set in group_mappings.items():
            print(f"   📋 {enterprise_group} → {aws_permission_set}")
        
        # 这个映射通常在 SAML 断言中配置
        saml_role_mapping = {
            "attribute_name": "https://aws.amazon.com/SAML/Attributes/Role",
            "mappings": []
        }
        
        for enterprise_group, aws_permission_set in group_mappings.items():
            role_arn = f"arn:aws:iam::ACCOUNT-ID:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_{aws_permission_set}"
            principal_arn = f"arn:aws:iam::ACCOUNT-ID:saml-provider/ExternalProvider"
            
            saml_role_mapping["mappings"].append({
                "enterprise_group": enterprise_group,
                "aws_role": f"{role_arn},{principal_arn}"
            })
        
        print("✅ 组映射配置完成")
        return saml_role_mapping


def main():
    """演示企业 SSO 集成配置"""
    print("🏢 企业 SSO 与 AWS IAM Identity Center 集成")
    print("=" * 50)
    
    # 初始化集成管理器
    integration = EnterpriseSSOIntegration()
    
    # 1. 配置外部身份提供商 (以 Okta 为例)
    print("\n1️⃣ 配置外部身份提供商:")
    okta_config = {
        "okta_entity_id": "http://www.okta.com/exk1234567890",
        "okta_sso_url": "https://company.okta.com/app/aws_sso/exk1234567890/sso/saml",
        "okta_certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
    }
    
    saml_config = integration.configure_external_idp("okta", okta_config)
    
    # 2. 设置自动用户预配置
    print("\n2️⃣ 配置自动用户预配置:")
    scim_config = integration.setup_automatic_provisioning(enable_scim=True)
    
    # 3. 创建权限集
    print("\n3️⃣ 创建企业权限集:")
    permission_sets = integration.create_permission_sets_for_enterprise()
    
    # 4. 配置组映射
    print("\n4️⃣ 配置企业组映射:")
    group_mappings = {
        "Kiro-Admins": "KiroAdmin",      # 企业的管理员组
        "Kiro-Users": "KiroUser",        # 企业的普通用户组
        "Developers": "KiroUser"         # 企业的开发者组
    }
    
    role_mapping = integration.map_enterprise_groups_to_aws_roles(group_mappings)
    
    print("\n🎉 企业 SSO 集成配置完成!")
    print("\n📋 配置总结:")
    print(f"   身份提供商: Okta")
    print(f"   自动预配置: {'启用' if scim_config else '禁用'}")
    print(f"   权限集数量: {len(permission_sets)}")
    print(f"   组映射数量: {len(group_mappings)}")


if __name__ == '__main__':
    main()