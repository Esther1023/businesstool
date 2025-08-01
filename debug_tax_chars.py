#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试税号字符问题
"""

import re

def debug_tax_chars():
    """调试税号字符问题"""
    print("🔍 调试税号字符问题")
    print("=" * 50)
    
    test_text = "915303005798280920D 0874-8969836"
    tax_number = "915303005798280920D"
    
    print(f"测试文本: {test_text}")
    print(f"税号: {tax_number}")
    print(f"税号长度: {len(tax_number)}")
    print()
    
    # 检查每个字符
    print("字符分析:")
    for i, char in enumerate(tax_number):
        print(f"  位置{i}: '{char}' (ASCII: {ord(char)})")
    print()
    
    # 测试简单的模式
    simple_patterns = [
        (r'915303005798280920D', '完全匹配'),
        (r'9\d{17}[A-Z]', '9开头+17位数字+1位字母'),
        (r'9\d{17}D', '9开头+17位数字+D'),
        (r'[0-9A-Z]{19}', '19位字母数字'),
        (r'[0-9A-Z]{18}', '18位字母数字'),
    ]
    
    for pattern, description in simple_patterns:
        print(f"模式: {pattern}")
        print(f"描述: {description}")
        
        matches = re.findall(pattern, test_text)
        print(f"匹配结果: {matches}")
        print()

if __name__ == '__main__':
    debug_tax_chars()