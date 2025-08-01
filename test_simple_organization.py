#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试文本整理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def test_simple_organization():
    """简单测试文本整理功能"""
    print("🧪 简单测试文本整理功能")
    print("=" * 60)
    
    # 混乱的OCR文本
    messy_text = """户银行 云南省曲靖市麒麟区寥廓南路 电话 曲靖市麒麟区农村信用合作联社西北信 云南三谱信息科技有限公司 曲靖市麒麟区农村信用合作联社西北信用 税号 银行账户 单位地址 915303005798280920D 0874-8969836 1300013009770012"""
    
    print(f"📄 混乱文本:")
    print(messy_text)
    print()
    
    # 创建OCR服务
    ocr_service = OptimizedOCRService()
    
    # 测试文本整理
    print("🔄 开始文本整理...")
    try:
        organized_text = ocr_service._organize_and_reconstruct_text(messy_text)
        print(f"📋 整理后文本:")
        print(organized_text)
        print()
        
        # 测试字段解析
        print("🔄 开始字段解析...")
        result = ocr_service.parse_text_to_fields(messy_text)
        
        print(f"📊 解析结果 ({len(result)} 个字段):")
        for field_name, value in result.items():
            print(f"  {field_name}: {value}")
        
        # 检查关键字段
        print(f"\n🎯 关键字段检查:")
        expected_fields = ['company_name', 'tax_number', 'reg_address', 'reg_phone', 'bank_name', 'bank_account']
        
        for field in expected_fields:
            status = "✅" if field in result else "❌"
            print(f"  {status} {field}")
        
        accuracy = (len(result) / len(expected_fields)) * 100
        print(f"\n📈 识别率: {accuracy:.1f}% ({len(result)}/{len(expected_fields)} 字段)")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_organization()