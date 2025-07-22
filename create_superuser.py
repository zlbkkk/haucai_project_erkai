#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings')
django.setup()

from fastuser.models import MyUser, UserInfo

def create_superuser():
    # 检查是否已存在超级用户
    if MyUser.objects.filter(is_superuser=True).exists():
        print("超级用户已存在")
        return

    # 创建超级用户
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123456'
    phone = '13800138000'

    # 创建Django用户
    user = MyUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        phone=phone,
        is_staff=True,
        is_superuser=True
    )

    # 创建对应的UserInfo记录
    try:
        user_info = UserInfo.objects.create(
            username=username,
            password=password,  # 这里可能需要加密，但先试试
            email=email,
            level=1  # 设置为管理员级别
        )
        print(f"超级用户和UserInfo创建成功！")
        print(f"用户名: {username}")
        print(f"密码: {password}")
        print(f"邮箱: {email}")
        print(f"手机: {phone}")
    except Exception as e:
        print(f"创建UserInfo时出错: {e}")
        # 如果UserInfo创建失败，至少Django用户已经创建
        print(f"Django超级用户创建成功！")
        print(f"用户名: {username}")
        print(f"密码: {password}")
        print(f"邮箱: {email}")
        print(f"手机: {phone}")

if __name__ == '__main__':
    create_superuser()
