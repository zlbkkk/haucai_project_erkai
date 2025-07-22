#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def create_admin():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123456'
    
    # 检查用户是否已存在
    if User.objects.filter(username=username).exists():
        print(f"用户 {username} 已存在")
        return
    
    # 创建超级用户
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    
    print(f"超级用户创建成功！")
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"邮箱: {email}")
    print(f"现在可以使用这个账号登录了")

if __name__ == '__main__':
    create_admin()
