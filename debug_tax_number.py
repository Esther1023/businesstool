#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试税号识别问题
"""

import re

def debug_tax_number():
    """调试税号识别问题"""
    print("🔍 调试税号识别问题")
    print("=" * 50)
    
    test_text = "915303005798280920D 0874-8969836"
    print(f"测试文本: {test_text}")
    print()
    
    # 测试不同的税号模式
    tax_patterns = [
        (r'(9[0-9A-HJ-NPQRTUWXY]{16}[A-HJ-NPQRTUWXY])', '18位，以9开头，最后一位是字母'),
        (r'(9[0-9A-Z]{17})', '18位统一社会信用代码，以9开头（包含所有字母）'),
        (r'([0-9A-Z]{18})', '18位代码（包含所有字母）'),
        (r'(\d{15})', '15位旧版税号'),
    ]
    
    for pattern, description in tax_patterns:
        print(f"模式: {pattern}")
        print(f"描述: {description}")
        
        matches = re.findall(pattern, test_text.upper())
        print(f"匹配结果: {matches}")
        
        if matches:
            for match in matches:
                print(f"  找到: {match}")
        else:
            print("  未匹配")
        print()

if __name__ == '__main__':
    debug_tax_number()