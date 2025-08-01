#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web接口实际接收的文本内容
"""

import requests
import json

def test_web_text_content():
    """测试Web接口实际接收的文本内容"""
    print("🧪 测试Web接口实际接收的文本内容")
    print("=" * 60)
    
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
    
    # 测试不同的文本内容
    test_cases = [
        {
            'name': '标准格式文本',
            'text': """名称：云南三谱信息科技有限公司
税号：915303005798280920D
单位地址：云南省曲靖市麒麟区寥廓南路135号
电话：0874-8969836
开户银行：曲靖市麒麟区农村信用合作联社西北信用社
银行账户：1300013009770012"""
        },
        {
            'name': '可能的OCR识别文本（带噪音）',
            'text': """名称 云南三谱信息科技有限公司 税号 915303005798280920D 单位地址 云南省曲靖市麒麟区寥廓南路135号 电话 0874-8969836 开户银行 曲靖市麒麟区农村信用合作联社西北信用社 银行账户 1300013009770012"""
        },
        {
            'name': '简化文本（只有关键信息）',
            'text': """915303005798280920D 0874-8969836"""
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 测试案例 {i}: {test_case['name']}")
        print(f"文本长度: {len(test_case['text'])} 字符")
        print(f"文本内容: {repr(test_case['text'])}")
        
        # 准备请求数据
        data = {
            'text': test_case['text']
        }
        
        try:
            # 发送请求
            response = session.post(
                'http://localhost:8080/parse_text',
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"解析状态: {'成功' if result.get('success') else '失败'}")
                
                if result.get('success'):
                    fields = result.get('fields', {})
                    field_count = result.get('field_count', 0)
                    
                    print(f"识别字段数: {field_count}")
                    
                    if field_count > 0:
                        print("识别的字段:")
                        for field_name, value in fields.items():
                            print(f"  {field_name}: {value}")
                    else:
                        print("❌ 未识别到任何字段")
                else:
                    print(f"❌ 解析失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print("-" * 50)

if __name__ == '__main__':
    test_web_text_content()