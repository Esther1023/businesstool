#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终验证脚本 - 验证OCR识别问题的修复效果
"""

import logging
from ocr_service_optimized import OptimizedOCRService

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_final_fixes():
    """测试最终修复效果"""
    
    # 用户实际的OCR文本（问题案例）
    ocr_text = """
    公司名称：武汉华中智谷科技有限公司
    税号：914201009MA4K2QOL8
    账号 中国建设银行股份有限公司武汉马场角支行
    42050164250000000123
    """
    
    print("=" * 60)
    print("最终验证测试")
    print("=" * 60)
    print(f"原始OCR文本:\n{ocr_text}")
    print("-" * 60)
    
    # 初始化OCR服务
    ocr_service = OptimizedOCRService()
    
    # 测试完整的文本解析
    print("测试完整文本解析:")
    result = ocr_service.parse_text_to_fields(ocr_text)
    
    print("\n解析结果:")
    for field, value in result.items():
        if value:
            print(f"  {field}: {value}")
    
    print("\n" + "=" * 60)
    print("修复验证结果:")
    print("=" * 60)
    
    # 验证修复效果
    issues = []
    
    # 1. 检查银行名称是否正确（不包含"账号"前缀和地址信息）
    bank_name = result.get('bank_name', '')
    if bank_name:
        if '账号' in bank_name:
            issues.append(f"❌ 银行名称仍包含'账号'前缀: '{bank_name}'")
        elif '武汉马场角' in bank_name:
            issues.append(f"❌ 银行名称仍包含地址信息: '{bank_name}'")
        elif bank_name == '中国建设银行股份有限公司':
            print(f"✅ 银行名称已正确识别: '{bank_name}'")
        else:
            print(f"✅ 银行名称修复成功: '{bank_name}'")
    else:
        issues.append("❌ 银行名称未识别")
    
    # 2. 检查是否还有虚假电话号码
    phone_fields = ['reg_phone', 'contact_phone', 'phone']
    found_fake_phone = False
    for field in phone_fields:
        phone = result.get(field, '')
        if phone and '16425000000' in phone:
            issues.append(f"❌ 仍存在虚假电话号码: '{phone}' (字段: {field})")
            found_fake_phone = True
    
    if not found_fake_phone:
        print("✅ 虚假电话号码问题已修复")
    
    # 3. 检查注册地址
    address = result.get('reg_address', '')
    if not address:
        issues.append("⚠️  注册地址未识别（原始文本中确实缺失地址信息）")
    else:
        print(f"✅ 注册地址识别成功: '{address}'")
    
    # 4. 检查其他字段
    company_name = result.get('company_name', '')
    if company_name:
        print(f"✅ 公司名称识别正常: '{company_name}'")
    
    tax_number = result.get('tax_number', '')
    if tax_number:
        print(f"✅ 税号识别正常: '{tax_number}'")
    
    bank_account = result.get('bank_account', '')
    if bank_account:
        print(f"✅ 银行账号识别正常: '{bank_account}'")
    
    print("\n" + "=" * 60)
    if issues:
        print("仍存在的问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("🎉 所有问题都已修复！")
    
    print("=" * 60)

if __name__ == "__main__":
    test_final_fixes()