#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的识别效果
"""

import requests
import json

def test_fixed_recognition():
    """测试修复后的识别效果"""
    print("🧪 测试修复后的识别效果")
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
    
    # 模拟真实的OCR识别文本（基于日志）
    real_ocr_text = """74-8969836 FPiR47T:HvSTRRRKAASRRREILiaS + ERTIKF:1300013009770012 915303005798280920 135 银行账户 税号 社 电话 曲靖市麒麟区农村信用合作联社西北信用 单位地址 次 开户银行 云南省曲靖市麒麟区寥廓南路 曲靖市麒麟区农村信用合作联社西北信 云南三谱信息科技有限公司 户银行 作 号"""
    
    print(f"📄 测试文本 (长度: {len(real_ocr_text)} 字符):")
    print(real_ocr_text[:100] + "..." if len(real_ocr_text) > 100 else real_ocr_text)
    print()
    
    # 期望的正确结果
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920D',  # 注意这里应该有D
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    # 准备请求数据
    data = {
        'text': real_ocr_text
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
                
                print("📊 识别结果对比:")
                correct_count = 0
                
                for field_name, expected_value in expected_fields.items():
                    if field_name in fields:
                        actual_value = fields[field_name]
                        is_correct = actual_value == expected_value
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
                
                # 检查关键问题
                print("🎯 关键问题检查:")
                
                # 1. 银行账号是否正确识别
                bank_account_correct = fields.get('bank_account') == '1300013009770012'
                print(f"  银行账号识别: {'✅ 正确' if bank_account_correct else '❌ 错误'}")
                
                # 2. 地址是否正确（不应该是银行名称）
                address = fields.get('reg_address', '')
                address_correct = '银行' not in address and '信用社' not in address
                print(f"  地址识别正确: {'✅ 是' if address_correct else '❌ 否'}")
                
                # 3. 银行名称是否正确
                bank_name = fields.get('bank_name', '')
                bank_name_correct = '信用社' in bank_name or '银行' in bank_name
                print(f"  银行名称识别: {'✅ 正确' if bank_name_correct else '❌ 错误'}")
                
                # 4. 公司名称是否正确
                company_correct = fields.get('company_name') == '云南三谱信息科技有限公司'
                print(f"  公司名称识别: {'✅ 正确' if company_correct else '❌ 错误'}")
                
                # 计算总体准确率
                accuracy = (correct_count / len(expected_fields)) * 100
                print(f"\n📈 总体准确率: {accuracy:.1f}% ({correct_count}/{len(expected_fields)} 字段)")
                
                if bank_account_correct and address_correct and bank_name_correct:
                    print("\n🎉 关键问题已修复！")
                else:
                    print("\n⚠️ 仍有问题需要进一步修复")
                
            else:
                print(f"❌ 解析失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_fixed_recognition()