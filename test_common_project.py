#!/usr/bin/env python
"""
测试公共项目功能的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings.dev')
django.setup()

from fastrunner.models import Project, API, Config, Variables
from fastrunner.utils.prepare import get_project_filter_condition, get_common_project_id

def test_common_project_functionality():
    """测试公共项目功能"""
    
    print("=== 测试公共项目功能 ===")
    
    # 1. 检查公共项目是否存在
    common_project_id = get_common_project_id()
    if common_project_id:
        print(f"✓ 公共项目存在，ID: {common_project_id}")
    else:
        print("✗ 公共项目不存在，请先运行 create_common_project.py")
        return
    
    # 2. 创建测试项目
    test_project, created = Project.objects.get_or_create(
        name="测试项目",
        defaults={
            'desc': '用于测试公共项目功能的测试项目',
            'responsible': 'admin',
            'creator': 'admin'
        }
    )
    print(f"{'✓ 创建' if created else '✓ 使用现有'}测试项目: {test_project.name} (ID: {test_project.id})")
    
    # 3. 在公共项目中创建测试数据
    common_api, created = API.objects.get_or_create(
        name="公共登录接口",
        project_id=common_project_id,
        defaults={
            'body': '{"method": "POST", "url": "/api/login"}',
            'url': '/api/login',
            'method': 'POST',
            'relation': 1,
            'creator': 'admin'
        }
    )
    print(f"{'✓ 创建' if created else '✓ 使用现有'}公共API: {common_api.name}")
    
    common_config, created = Config.objects.get_or_create(
        name="公共配置",
        project_id=common_project_id,
        defaults={
            'body': '{"variables": {"base_url": "https://api.example.com"}}',
            'base_url': 'https://api.example.com',
            'creator': 'admin'
        }
    )
    print(f"{'✓ 创建' if created else '✓ 使用现有'}公共配置: {common_config.name}")
    
    common_var, created = Variables.objects.get_or_create(
        key="COMMON_TOKEN",
        project_id=common_project_id,
        defaults={
            'value': 'common_token_value',
            'description': '公共令牌',
            'creator': 'admin'
        }
    )
    print(f"{'✓ 创建' if created else '✓ 使用现有'}公共变量: {common_var.key}")
    
    # 4. 在测试项目中创建测试数据
    test_api, created = API.objects.get_or_create(
        name="测试项目接口",
        project_id=test_project.id,
        defaults={
            'body': '{"method": "GET", "url": "/api/test"}',
            'url': '/api/test',
            'method': 'GET',
            'relation': 1,
            'creator': 'admin'
        }
    )
    print(f"{'✓ 创建' if created else '✓ 使用现有'}测试项目API: {test_api.name}")
    
    # 5. 测试过滤条件
    print("\n=== 测试查询过滤 ===")
    
    # 测试项目应该能看到自己的数据和公共项目的数据
    project_filter = get_project_filter_condition(test_project.id)
    
    # 查询API
    apis = API.objects.filter(project_filter)
    api_names = [api.name for api in apis]
    print(f"测试项目能看到的API: {api_names}")
    
    # 查询配置
    configs = Config.objects.filter(project_filter)
    config_names = [config.name for config in configs]
    print(f"测试项目能看到的配置: {config_names}")
    
    # 查询变量
    variables = Variables.objects.filter(project_filter)
    var_keys = [var.key for var in variables]
    print(f"测试项目能看到的变量: {var_keys}")
    
    # 6. 验证公共项目本身的查询
    print("\n=== 测试公共项目查询 ===")
    common_project_filter = get_project_filter_condition(common_project_id)
    
    common_apis = API.objects.filter(common_project_filter)
    common_api_names = [api.name for api in common_apis]
    print(f"公共项目能看到的API: {common_api_names}")
    
    print("\n=== 测试完成 ===")
    print("如果上述测试都显示 ✓，说明公共项目功能正常工作")

if __name__ == "__main__":
    test_common_project_functionality()
