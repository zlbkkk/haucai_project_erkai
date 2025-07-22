#!/usr/bin/env python3
import requests
import json

def test_login():
    url = "http://localhost:8000/api/user/login/"
    data = {
        "username": "admin",
        "password": "admin123456"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 登录成功!")
                print(f"Token: {result.get('token', 'N/A')}")
                print(f"User: {result.get('user', 'N/A')}")
                return result.get('token')
            else:
                print("❌ 登录失败:", result.get('msg', 'Unknown error'))
        else:
            print("❌ HTTP错误:", response.status_code)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Django服务器正在运行")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    
    return None

if __name__ == "__main__":
    test_login()
