#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实案例 - 云南三谱信息科技有限公司
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def test_real_case():
    """测试真实案例"""
    print("🧪 测试真实案例：云南三谱信息科技有限公司")
    print("=" * 60)
    
    # 模拟真实的OCR识别文本（基于您的日志）
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
    
    # 显示每个字段的结果
    expected_fields = {
        'company_name': '云南三谱信息科技有限公司',
        'tax_number': '915303005798280920', 
        'reg_address': '云南省曲靖市麒麟区寥廓南路135号',
        'reg_phone': '0874-8969836',
        'bank_name': '曲靖市麒麟区农村信用合作联社西北信用社',
        'bank_account': '1300013009770012'
    }
    
    print("📋 字段匹配结果:")
    for field_name, expected_value in expected_fields.items():
        if field_name in result:
            actual_value = result[field_name]
            status = "✅" if actual_value == expected_value else "⚠️"
            print(f"  {status} {field_name}: {actual_value}")
            if actual_value != expected_value:
                print(f"      期望值: {expected_value}")
        else:
            print(f"  ❌ {field_name}: 未识别")
    
    # 检查是否有额外的字段
    extra_fields = set(result.keys()) - set(expected_fields.keys())
    if extra_fields:
        print(f"\n🔍 额外识别的字段:")
        for field in extra_fields:
            print(f"  + {field}: {result[field]}")
    
    # 计算准确率
    correct_count = sum(1 for field, expected in expected_fields.items() 
                       if field in result and result[field] == expected)
    accuracy = (correct_count / len(expected_fields)) * 100
    
    print(f"\n📈 准确率: {accuracy:.1f}% ({correct_count}/{len(expected_fields)} 字段)")
    
    if accuracy >= 80:
        print("🎉 识别效果优秀！")
    elif accuracy >= 60:
        print("👍 识别效果良好")
    else:
        print("⚠️ 需要进一步优化")
    
    return result

if __name__ == '__main__':
    test_real_case()