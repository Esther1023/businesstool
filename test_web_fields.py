#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web接口字段返回
"""

import requests
import json

def test_parse_text_endpoint():
    """测试/parse_text接口"""
    print("🧪 测试 /parse_text 接口")
    print("=" * 50)
    
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
    
    # 测试文本
    test_text = """名称：云南三谱信息科技有限公司
税号：915303005798280920D
单位地址：云南省曲靖市麒麟区寥廓南路135号
电话：0874-8969836
开户银行：曲靖市麒麟区农村信用合作联社西北信用社
银行账户：1300013009770012"""
    
    # 准备请求数据
    data = {
        'text': test_text
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
            print(f"✅ 请求成功")
            print(f"解析状态: {'成功' if result.get('success') else '失败'}")
            
            if result.get('success'):
                fields = result.get('fields', {})
                field_count = result.get('field_count', 0)
                
                print(f"识别字段数: {field_count}")
                print()
                
                # 显示所有字段
                print("📋 返回的字段:")
                expected_fields = [
                    'company_name', 'tax_number', 'reg_address', 
                    'reg_phone', 'bank_name', 'bank_account'
                ]
                
                for field_name in expected_fields:
                    if field_name in fields:
                        print(f"  ✅ {field_name}: {fields[field_name]}")
                    else:
                        print(f"  ❌ {field_name}: 未返回")
                
                # 检查额外字段
                extra_fields = set(fields.keys()) - set(expected_fields)
                if extra_fields:
                    print(f"\n🔍 额外字段:")
                    for field in extra_fields:
                        print(f"  + {field}: {fields[field]}")
                
                # 检查关键问题
                print(f"\n🎯 关键检查:")
                tax_correct = fields.get('tax_number') == '915303005798280920D'
                print(f"  税号完整性: {'✅' if tax_correct else '❌'} {fields.get('tax_number', '未找到')}")
                
                company_exists = 'company_name' in fields
                print(f"  公司名称存在: {'✅' if company_exists else '❌'}")
                
                address_exists = 'reg_address' in fields
                print(f"  注册地址存在: {'✅' if address_exists else '❌'}")
                
                bank_exists = 'bank_name' in fields
                print(f"  开户银行存在: {'✅' if bank_exists else '❌'}")
                
                account_exists = 'bank_account' in fields
                print(f"  银行账号存在: {'✅' if account_exists else '❌'}")
                
                if field_count == 6 and tax_correct and company_exists and address_exists and bank_exists and account_exists:
                    print(f"\n🎉 所有字段都正确返回！")
                else:
                    print(f"\n⚠️ 仍有字段缺失或错误")
                
            else:
                print(f"❌ 解析失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保应用正在运行在 http://localhost:8080")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_parse_text_endpoint()