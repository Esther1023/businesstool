#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段混乱问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def debug_field_confusion():
    """调试字段混乱问题"""
    print("🔍 调试字段混乱问题")
    print("=" * 80)
    
    # 基于日志的真实OCR识别文本（包含噪音）
    real_ocr_text = """74-8969836 FPiR47T:HvSTRRRKAASRRREILiaS + ERTIKF:1300013009770012 915303005798280920 135 银行账户 税号 社 电话 曲靖市麒麟区农村信用合作联社西北信用 单位地址 次 开户银行 云南省曲靖市麒麟区寥廓南路 曲靖市麒麟区农村信用合作联社西北信 云南三谱信息科技有限公司 户银行 作 号"""
    
    print(f"📄 真实OCR文本 (长度: {len(real_ocr_text)} 字符):")
    print(real_ocr_text)
    print()
    
    # 期望的正确结果
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920D',
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    print("🎯 期望的正确结果:")
    for field, value in expected_fields.items():
        print(f"  {field}: {value}")
    print()
    
    # 创建OCR服务实例
    ocr_service = OptimizedOCRService()
    
    # 解析文本
    print("🔄 开始解析...")
    result = ocr_service.parse_text_to_fields(real_ocr_text)
    
    print(f"📊 实际解析结果 ({len(result)} 个字段):")
    for field_name, value in result.items():
        print(f"  {field_name}: {value}")
    print()
    
    # 分析问题
    print("🔍 问题分析:")
    
    # 检查每个期望字段
    for field_name, expected_value in expected_fields.items():
        if field_name in result:
            actual_value = result[field_name]
            if actual_value == expected_value:
                print(f"  ✅ {field_name}: 正确")
            else:
                print(f"  ❌ {field_name}: 错误")
                print(f"      期望: {expected_value}")
                print(f"      实际: {actual_value}")
        else:
            print(f"  ❌ {field_name}: 未识别")
    
    # 检查关键数字是否存在于文本中
    print(f"\n🔍 关键信息检查:")
    key_info = {
        '银行账号': '1300013009770012',
        '税号': '915303005798280920',
        '电话': '0874-8969836',
        '公司名称': '云南三谱信息科技有限公司'
    }
    
    for name, value in key_info.items():
        if value in real_ocr_text:
            print(f"  ✅ {name} '{value}' 存在于文本中")
        else:
            print(f"  ❌ {name} '{value}' 不存在于文本中")
    
    # 分析为什么银行账号没有被识别
    print(f"\n🔍 银行账号识别分析:")
    bank_account = '1300013009770012'
    if bank_account in real_ocr_text:
        print(f"  银行账号 '{bank_account}' 存在于文本中")
        
        # 检查是否被其他字段使用
        used_in_other_fields = False
        for field_name, field_value in result.items():
            if bank_account in str(field_value):
                print(f"  ⚠️ 银行账号被包含在字段 '{field_name}' 中: {field_value}")
                used_in_other_fields = True
        
        if not used_in_other_fields:
            print(f"  🤔 银行账号未被任何字段使用，可能是验证失败")
    
    return result

if __name__ == '__main__':
    debug_field_confusion()