#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面的OCR诊断工具
"""

import sys
import os
import requests
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def create_test_image_with_real_data():
    """创建包含真实数据的测试图片"""
    img = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    # 使用默认字体
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # 真实的测试文本（基于您的截图）
    test_text = [
        "名称：云南三谱信息科技有限公司",
        "税号：915303005798280920D", 
        "单位地址：云南省曲靖市麒麟区寥廓南路135号",
        "电话：0874-8969836",
        "开户银行：曲靖市麒麟区农村信用合作联社西北信用社",
        "银行账户：1300013009770012"
    ]
    
    y_position = 40
    for line in test_text:
        draw.text((40, y_position), line, fill='black', font=font)
        y_position += 60
    
    # 转换为字节数据
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def test_1_backend_text_parsing():
    """测试1：后端文本解析"""
    print("🔍 测试1：后端文本解析")
    print("-" * 50)
    
    test_text = """名称：云南三谱信息科技有限公司
税号：915303005798280920D
单位地址：云南省曲靖市麒麟区寥廓南路135号
电话：0874-8969836
开户银行：曲靖市麒麟区农村信用合作联社西北信用社
银行账户：1300013009770012"""
    
    ocr_service = OptimizedOCRService()
    result = ocr_service.parse_text_to_fields(test_text)
    
    print(f"输入文本长度: {len(test_text)} 字符")
    print(f"识别字段数: {len(result)}")
    
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920D',
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    all_correct = True
    for field, expected in expected_fields.items():
        if field in result:
            actual = result[field]
            correct = actual == expected
            status = "✅" if correct else "❌"
            print(f"  {status} {field}: {actual}")
            if not correct:
                print(f"      期望: {expected}")
                all_correct = False
        else:
            print(f"  ❌ {field}: 未识别")
            all_correct = False
    
    print(f"后端文本解析: {'✅ 通过' if all_correct else '❌ 失败'}")
    return all_correct

def test_2_backend_image_processing():
    """测试2：后端图片处理"""
    print("\n🔍 测试2：后端图片处理")
    print("-" * 50)
    
    # 创建测试图片
    image_data = create_test_image_with_real_data()
    print(f"测试图片大小: {len(image_data)} bytes")
    
    ocr_service = OptimizedOCRService()
    result = ocr_service.process_image(image_data)
    
    print(f"处理状态: {'成功' if result['success'] else '失败'}")
    
    if result['success']:
        print(f"提取文本长度: {len(result['extracted_text'])}")
        print(f"识别字段数: {result['field_count']}")
        
        print(f"\n提取的文本:")
        print(result['extracted_text'][:200] + "..." if len(result['extracted_text']) > 200 else result['extracted_text'])
        
        print(f"\n识别的字段:")
        for field, value in result['parsed_fields'].items():
            print(f"  {field}: {value}")
        
        return result['field_count'] >= 4  # 至少识别4个字段
    else:
        print(f"处理失败: {result['error']}")
        return False

def test_3_web_api_parse_text():
    """测试3：Web API文本解析接口"""
    print("\n🔍 测试3：Web API文本解析接口")
    print("-" * 50)
    
    # 创建会话并登录
    session = requests.Session()
    
    login_data = {
        'username': 'Esther',
        'password': '967420'
    }
    
    try:
        login_response = session.post('http://localhost:8080/login', data=login_data, timeout=10)
        if login_response.st