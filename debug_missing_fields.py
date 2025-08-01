#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试缺失字段问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def debug_missing_fields():
    """调试缺失字段问题"""
    print("🔍 调试缺失字段问题")
    print("=" * 60)
    
    # 基于您截图的真实OCR识别文本（包含字母D）
    real_text = """名称：云南三谱信息科技有限公司
税号：915303005798280920D
单位地址：云南省曲靖市麒麟区寥廓南路135号
电话：0874-8969836
开户银行：曲靖市麒麟区农村信用合作联社西北信用社
银行账户：1300013009770012"""
    
    print(f"📄 输入文本:")
    print(real_text)
    print()
    
    # 创建OCR服务实例
    ocr_service = OptimizedOCRService()
    
    # 解析文本
    print("🔄 开始解析...")
    result = ocr_service.parse_text_to_fields(real_text)
    
    print(f"📊 解析结果:")
    print(f"识别字段数: {len(result)}")
    print()
    
    # 显示所有识别的字段
    print("📋 识别的字段:")
    for field_name, value in result.items():
        print(f"  {field_name}: {value}")
    
    print()
    
    # 检查期望的字段
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920D',  # 注意这里有字母D
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    print("🎯 期望vs实际对比:")
    missing_fields = []
    incorrect_fields = []
    
    for field_name, expected_value in expected_fields.items():
        if field_name in result:
            actual_value = result[field_name]
            if actual_value == expected_value:
                print(f"  ✅ {field_name}: {actual_value}")
            else:
                print(f"  ⚠️  {field_name}: {actual_value}")
                print(f"      期望: {expected_value}")
                incorrect_fields.append((field_name, actual_value, expected_value))
        else:
            print(f"  ❌ {field_name}: 未识别")
            missing_fields.append(field_name)
    
    # 分析问题
    print(f"\n🔍 问题分析:")
    if missing_fields:
        print(f"  缺失字段: {', '.join(missing_fields)}")
    
    if incorrect_fields:
        print(f"  错误字段:")
        for field, actual, expected in incorrect_fields:
            print(f"    - {field}: '{actual}' != '{expected}'")
    
    # 特别检查税号问题
    if 'tax_number' in result:
        tax_value = result['tax_number']
        if tax_value == '915303005798280920':
            print(f"  🚨 税号缺少字母D: '{tax_value}' 应该是 '915303005798280920D'")
        elif tax_value == '915303005798280920D':
            print(f"  ✅ 税号完整: '{tax_value}'")
    
    return result

if __name__ == '__main__':
    debug_missing_fields()