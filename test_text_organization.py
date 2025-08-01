#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文本整理功能
"""

import requests
import json

def test_text_organization():
    """测试文本整理功能"""
    print("🧪 测试文本整理功能")
    print("=" * 70)
    
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
    
    # 使用真实的混乱OCR文本
    messy_ocr_text = """户银行 云南省曲靖市麒麟区寥廓南路 电话 曲靖市麒麟区农村信用合作联社西北信 云南三谱信息科技有限公司 曲靖市麒麟区农村信用合作联社西北信用 税号 银行账户 单位地址 915303005798280920D 0874-8969836 1300013009770012"""
    
    print(f"📄 混乱的OCR文本:")
    print(messy_ocr_text)
    print()
    
    # 期望的整理结果
    expected_organized = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920D',
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    print("🎯 期望的整理结果:")
    for field, value in expected_organized.items():
        print(f"  {field}: {value}")
    print()
    
    # 准备请求数据
    data = {
        'text': messy_ocr_text
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
                print()
                
                print("📊 文本整理效果对比:")
                correct_count = 0
                
                for field_name, expected_value in expected_organized.items():
                    if field_name in fields:
                        actual_value = fields[field_name]
                        # 宽松匹配：只要包含主要内容就算正确
                        is_correct = _is_field_correct(field_name, actual_value, expected_value)
                        status = "✅" if is_correct else "⚠️"
                        print(f"  {status} {field_name}:")
                        print(f"      实际: {actual_value}")
                        if not is_correct:
                            print(f"      期望: {expected_value}")
                        else:
                            correct_count += 1
                    else:
                        print(f"  ❌ {field_name}: 未识别")
                    print()
                
                # 关键指标检查
                print("🎯 关键指标检查:")
                
                # 1. 银行名称完整性
                bank_name = fields.get('bank_name', '')
                bank_complete = '曲靖市' in bank_name and '信用社' in bank_name
                print(f"  银行名称完整: {'✅' if bank_complete else '❌'}")
                
                # 2. 地址识别
                address = fields.get('reg_address', '')
                address_correct = '云南省' in address and '路' in address
                print(f"  地址识别正确: {'✅' if address_correct else '❌'}")
                
                # 3. 税号完整性
                tax_number = fields.get('tax_number', '')
                tax_complete = len(tax_number) >= 18 and 'D' in tax_number
                print(f"  税号完整: {'✅' if tax_complete else '❌'}")
                
                # 4. 银行账号识别
                bank_account = fields.get('bank_account', '')
                account_correct = bank_account == '1300013009770012'
                print(f"  银行账号正确: {'✅' if account_correct else '❌'}")
                
                # 总体评估
                accuracy = (correct_count / len(expected_organized)) * 100
                print(f"\n📈 整理准确率: {accuracy:.1f}% ({correct_count}/{len(expected_organized)} 字段)")
                
                if accuracy >= 80:
                    print("🎉 文本整理效果优秀！")
                elif accuracy >= 60:
                    print("👍 文本整理效果良好")
                else:
                    print("⚠️ 文本整理需要进一步优化")
                
            else:
                print(f"❌ 解析失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def _is_field_correct(field_name, actual, expected):
    """判断字段是否正确（宽松匹配）"""
    if field_name == 'company_name':
        return '云南三谱信息科技有限公司' in actual
    elif field_name == 'tax_number':
        return '915303005798280920' in actual
    elif field_name == 'reg_address':
        return '云南省' in actual and '曲靖市' in actual and '路' in actual
    elif field_name == 'reg_phone':
        return '0874-8969836' in actual
    elif field_name == 'bank_name':
        return '曲靖市' in actual and '信用社' in actual
    elif field_name == 'bank_account':
        return actual == expected
    return False

if __name__ == '__main__':
    test_text_organization()