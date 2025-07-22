#!/usr/bin/env python
"""
创建公共项目的脚本
用于初始化公共项目，让所有项目都能访问公共项目的数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings.dev')
django.setup()

from fastrunner.models import Project
from django.core.exceptions import ObjectDoesNotExist

def create_common_project():
    """创建公共项目"""
    common_project_name = "公共项目"
    
    try:
        # 检查公共项目是否已存在
        project = Project.objects.get(name=common_project_name)
        print(f"公共项目已存在: {project.name} (ID: {project.id})")
        return project
    except ObjectDoesNotExist:
        # 创建公共项目
        project = Project.objects.create(
            name=common_project_name,
            desc="公共项目，包含所有项目都可以使用的通用配置、接口等数据",
            responsible="admin",
            creator="admin",
            yapi_base_url="",
            yapi_openapi_token="",
            jira_project_key="",
            jira_bearer_token=""
        )
        print(f"公共项目创建成功: {project.name} (ID: {project.id})")
        return project

if __name__ == "__main__":
    create_common_project()
