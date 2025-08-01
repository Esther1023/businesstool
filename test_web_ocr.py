#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web OCR接口
"""

import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_test_image():
    """创建测试图片"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 使用默认字体
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # 测试文本
    test_text = [
        "公司名称：测试科技有限公司",
        "税号：91330108MA28A1234X", 
        "注册地址：浙江省杭州市西湖区测试路88号",
        "注册电话：0571-88888888",
        "开户行：中国工商银行杭州分行",
        "银行账号：1234567890123456789"
    ]
    
    y_position = 30
    for line in test_text:
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 50
    
    # 转换为base64
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return base64.b64encode(img_byte_arr).decode('utf-8')

def test_ocr_image_endpoint():
    """测试/ocr_image接口"""
    print("🧪 测试 /ocr_image 接口...")
    
    # 创建会话并登录
    session = requests.Session()
    
    # 先登录
    login_data = {
        'username': 'Esther',
        'password': '967420'
    }
    
    login_response = session.post('http://localhost:8080/login', data=login_data)
    if login_response.status_code != 200 or 'login' in login_response.url:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功")
    
    # 创建测试图片
    image_base64 = create_test_image()
    
    # 准备请求数据
    data = {
        'image': f'data:image/png;base64,{image_base64}'
    }
    
    try:
        # 发送请求
        response = session.post(
            'http://localhost:8080/ocr_image',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"识别状态: {'成功' if result.get('success') else '失败'}")
            
            if result.get('success'):
                print(f"识别文本长度: {len(result.get('text', ''))}")
                print(f"识别字段数: {result.get('field_count', 0)}")
                
                if result.get('fields'):
                    print("识别的字段:")
                    for field, value in result.get('fields', {}).items():
                        print(f"  {field}: {value}")
                
                print(f"\n原始文本:")
                print(result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', ''))
            else:
                print(f"❌ 识别失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保应用正在运行在 http://localhost:8080")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_health_endpoint():
    """测试健康检查接口"""
    print("🧪 测试 /health 接口...")
    
    try:
        response = requests.get('http://localhost:8080/health', timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查通过")
            print(f"状态: {result.get('status')}")
            print(f"版本: {result.get('version')}")
            print(f"环境: {result.get('environment')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：应用可能未运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    print("🚀 Web OCR接口测试")
    print("=" * 50)
    
    # 测试健康检查
    test_health_endpoint()
    print()
    
    # 测试OCR接口
    test_ocr_image_endpoint()
    
    print("\n" + "=" * 50)
    print("测试完成")