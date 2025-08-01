#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段匹配问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_service_optimized import OptimizedOCRService

def debug_field_matching():
    """调试字段匹配问题"""
    print("🔍 调试字段匹配问题")
    print("=" * 70)
    
    # 模拟真实的OCR识别文本（201字符）
    real_ocr_text = """名称：云南三谱信息科技有限公司
税号：915303005798280920D
单位地址：云南省曲靖市麒麟区寥廓南路135号
电话：0874-8969836
开户银行：曲靖市麒麟区农村信用合作联社西北信用社
银行账户：1300013009770012"""
    
    print(f"📄 输入文本 (长度: {len(real_ocr_text)} 字符):")
    print(real_ocr_text)
    print()
    
    # 创建OCR服务实例
    ocr_service = OptimizedOCRService()
    
    # 手动调用parse_text_to_fields方法，逐步调试
    print("🔄 开始逐步调试...")
    
    # 第一步：检查文本分割
    lines = real_ocr_text.split('\n')
    print(f"📋 文本分割结果 ({len(lines)} 行):")
    for i, line in enumerate(lines):
        print(f"  {i+1}: '{line.strip()}'")
    print()
    
    # 第二步：检查每行的字段匹配
    result = {}
    separators = ['：', ':', '=', '：', '＝', '｜', '|', '\t', ' ']
    
    print("🔍 逐行字段匹配:")
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            print(f"  行{line_num}: 空行，跳过")
            continue
        
        print(f"  行{line_num}: '{line}'")
        
        # 尝试不同的分隔符
        matched = False
        for separator in separators:
            if separator in line:
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    if key and value:
                        print(f"    分隔符 '{separator}': key='{key}', value='{value}'")
                        
                        # 查找匹配的字段
                        field_name = ocr_service._find_matching_field(key)
                        if field_name:
                            print(f"    ✅ 字段匹配: '{key}' -> {field_name}")
                            
                            # 清理字段值
                            cleaned_value = ocr_service._clean_field_value(field_name, value)
                            print(f"    清理后值: '{cleaned_value}'")
                            
                            # 验证字段值
                            is_valid = ocr_service._validate_field_value(field_name, cleaned_value)
                            print(f"    验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
                            
                            if cleaned_value and is_valid:
                                # 检查是否已存在更好的值
                                if field_name not in result or len(cleaned_value) > len(result[field_name]):
                                    result[field_name] = cleaned_value
                                    print(f"    ✅ 添加到结果: {field_name} = '{cleaned_value}'")
                                else:
                                    print(f"    ⚠️ 跳过（已有更好值）: {field_name}")
                            else:
                                print(f"    ❌ 跳过（值无效或为空）")
                        else:
                            print(f"    ❌ 无匹配字段: '{key}'")
                        matched = True
                        break
        
        if not matched:
            print(f"    ❌ 未找到有效分隔符")
        print()
    
    print(f"📊 正常字段匹配结果 ({len(result)} 个字段):")
    for field_name, value in result.items():
        print(f"  {field_name}: {value}")
    print()
    
    # 第三步：检查正则匹配补充
    print("🔍 正则匹配补充:")
    supplemented_result = ocr_service._pattern_match_supplement(real_ocr_text, result)
    
    print(f"📊 最终结果 ({len(supplemented_result)} 个字段):")
    for field_name, value in supplemented_result.items():
        print(f"  {field_name}: {value}")
    
    # 分析问题
    print(f"\n🎯 问题分析:")
    if len(result) == 0:
        print("  🚨 严重问题：正常字段匹配完全失效！")
        print("  可能原因：")
        print("    1. 字段映射配置问题")
        print("    2. 分隔符识别问题")
        print("    3. 字段验证过于严格")
        print("    4. 字段清理过程出错")
    elif len(result) < 6:
        print(f"  ⚠️ 部分问题：正常匹配只识别了 {len(result)}/6 个字段")
    else:
        print(f"  ✅ 正常匹配工作正常")
    
    if len(supplemented_result) - len(result) > 0:
        added_by_regex = len(supplemented_result) - len(result)
        print(f"  📈 正则补充添加了 {added_by_regex} 个字段")
    
    return supplemented_result

if __name__ == '__main__':
    debug_field_matching()