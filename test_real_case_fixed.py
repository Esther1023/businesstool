#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的真实案例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def test_fixed_case():
    """测试修复后的案例"""
    print("🧪 测试修复后的真实案例：云南三谱信息科技有限公司")
    print("=" * 70)
    
    # 基于您截图的真实OCR识别文本
    real_text = """名称：云南三谱信息科技有限公司
税号：915303005798280920
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
    result = ocr_service.parse_text_to_fields(real_text)
    
    print(f"📊 解析结果:")
    print(f"识别字段数: {len(result)}")
    print()
    
    # 期望的正确结果
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920', 
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',  # 固定电话
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    print("📋 字段匹配结果:")
    correct_count = 0
    for field_name, expected_value in expected_fields.items():
        if field_name in result:
            actual_value = result[field_name]
            is_correct = actual_value == expected_value
            status = "✅" if is_correct else "⚠️"
            print(f"  {status} {field_name}: {actual_value}")
            if not is_correct:
                print(f"      期望值: {expected_value}")
            else:
                correct_count += 1
        else:
            print(f"  ❌ {field_name}: 未识别")
    
    # 检查错误的字段映射
    wrong_mappings = []
    for field_name, actual_value in result.items():
        if field_name not in expected_fields:
            wrong_mappings.append((field_name, actual_value))
        elif result[field_name] != expected_fields[field_name]:
            # 检查是否是税号被错误分配
            if actual_value == '915303005798280920' and field_name != 'tax_number':
                wrong_mappings.append((field_name, actual_value))
    
    if wrong_mappings:
        print(f"\n❌ 错误的字段映射:")
        for field, value in wrong_mappings:
            print(f"  - {field}: {value} (应该是其他字段)")
    
    # 计算准确率
    accuracy = (correct_count / len(expected_fields)) * 100
    
    print(f"\n📈 准确率: {accuracy:.1f}% ({correct_count}/{len(expected_fields)} 字段)")
    
    # 特别检查关键问题
    print(f"\n🔍 关键问题检查:")
    
    # 1. 税号是否被错误识别为电话
    tax_as_phone = any(v == '915303005798280920' for k, v in result.items() if 'phone' in k)
    print(f"  税号被识别为电话: {'❌ 是' if tax_as_phone else '✅ 否'}")
    
    # 2. 税号是否被错误识别为银行账号
    tax_as_account = result.get('bank_account') == '915303005798280920'
    print(f"  税号被识别为银行账号: {'❌ 是' if tax_as_account else '✅ 否'}")
    
    # 3. 固定电话是否正确识别
    landline_correct = result.get('reg_phone') == '0874-8969836'
    print(f"  固定电话正确识别: {'✅ 是' if landline_correct else '❌ 否'}")
    
    # 4. 银行账号是否正确
    account_correct = result.get('bank_account') == '1300013009770012'
    print(f"  银行账号正确识别: {'✅ 是' if account_correct else '❌ 否'}")
    
    if accuracy >= 90 and not tax_as_phone and not tax_as_account and landline_correct:
        print("\n🎉 修复成功！所有问题都已解决")
    elif accuracy >= 80:
        print("\n👍 大部分问题已修复，效果良好")
    else:
        print("\n⚠️ 仍需进一步优化")
    
    return result

if __name__ == '__main__':
    test_fixed_case()