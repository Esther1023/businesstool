#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化OCR服务测试脚本
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ocr_service_optimized import OptimizedOCRService
    print("✓ 优化OCR服务模块导入成功")
except ImportError as e:
    print(f"✗ 优化OCR服务模块导入失败: {e}")
    sys.exit(1)

def create_comprehensive_test_image():
    """创建一个包含更多字段的测试图片"""
    # 创建更大的白色背景图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf'
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 18)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            
    except:
        font = ImageFont.load_default()
    
    # 添加更全面的测试文本
    test_text = [
        "公司名称：杭州测试科技有限公司",
        "税号：91330108MA28A1234X", 
        "注册地址：浙江省杭州市西湖区文三路138号东方通信大厦8楼",
        "注册电话：0571-88776655",
        "开户行：中国工商银行杭州文三支行",
        "银行账号：1202021209900123456",
        "联系人：张经理",
        "联系电话：13805718888",
        "邮寄地址：浙江省杭州市西湖区文三路138号东方通信大厦8楼",
        "简道云账号：jdy20240801abcdef123456"
    ]
    
    y_position = 40
    for line in test_text:
        draw.text((40, y_position), line, fill='black', font=font)
        y_position += 40
    
    # 添加一些干扰文本来测试识别准确性
    draw.text((40, y_position + 20), "备注：以上信息仅供测试使用", fill='gray', font=font)
    
    # 保存为字节数据
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def test_optimized_ocr_service():
    """测试优化的OCR服务"""
    print("\n开始测试优化OCR服务...")
    
    # 创建优化OCR服务实例
    ocr_service = OptimizedOCRService()
    print("✓ 优化OCR服务实例创建成功")
    
    # 创建测试图片
    print("创建综合测试图片...")
    test_image_data = create_comprehensive_test_image()
    print(f"✓ 测试图片创建成功，大小: {len(test_image_data)} bytes")
    
    # 处理图片
    print("开始优化OCR识别...")
    result = ocr_service.process_image(test_image_data)
    
    # 显示结果
    print("\n" + "="*60)
    print("优化OCR识别结果")
    print("="*60)
    print(f"识别状态: {'成功' if result['success'] else '失败'}")
    print(f"OCR可用性: {'是' if result['ocr_available'] else '否'}")
    
    if result['success']:
        print(f"识别字段数量: {result['field_count']}")
        print(f"原始文本长度: {len(result['extracted_text'])}")
        
        print(f"\n📋 识别的字段 ({result['field_count']}/10):")
        expected_fields = [
            'company_name', 'tax_number', 'reg_address', 'reg_phone', 
            'bank_name', 'bank_account', 'contact_name', 'contact_phone',
            'mail_address', 'jdy_account'
        ]
        
        for field_name in expected_fields:
            if field_name in result['parsed_fields']:
                print(f"  ✅ {field_name}: {result['parsed_fields'][field_name]}")
            else:
                print(f"  ❌ {field_name}: 未识别")
        
        print(f"\n📄 原始识别文本:")
        print("-" * 40)
        print(result['extracted_text'])
        print("-" * 40)
        
        # 计算识别准确率
        accuracy = (result['field_count'] / 10) * 100
        print(f"\n📊 识别准确率: {accuracy:.1f}% ({result['field_count']}/10 字段)")
        
        if accuracy >= 80:
            print("🎉 识别效果优秀！")
        elif accuracy >= 60:
            print("👍 识别效果良好")
        elif accuracy >= 40:
            print("⚠️  识别效果一般，需要优化")
        else:
            print("❌ 识别效果较差，需要重点优化")
        
    else:
        print(f"❌ 识别失败: {result.get('error', '未知错误')}")
    
    return result['success']

def compare_with_original():
    """与原始OCR服务对比"""
    print("\n" + "="*60)
    print("OCR服务对比测试")
    print("="*60)
    
    # 测试原始服务
    try:
        from ocr_service import OCRService
        original_service = OCRService()
        test_image_data = create_comprehensive_test_image()
        
        print("🔄 测试原始OCR服务...")
        original_result = original_service.process_image(test_image_data)
        original_count = original_result.get('field_count', 0)
        print(f"原始服务识别字段数: {original_count}")
        
        # 测试优化服务
        print("🔄 测试优化OCR服务...")
        optimized_service = OptimizedOCRService()
        optimized_result = optimized_service.process_image(test_image_data)
        optimized_count = optimized_result.get('field_count', 0)
        print(f"优化服务识别字段数: {optimized_count}")
        
        # 对比结果
        improvement = optimized_count - original_count
        if improvement > 0:
            print(f"🎉 优化效果: +{improvement} 个字段 (提升 {(improvement/10)*100:.1f}%)")
        elif improvement == 0:
            print("📊 优化效果: 识别字段数相同")
        else:
            print(f"⚠️  优化效果: {improvement} 个字段 (需要进一步调整)")
            
    except Exception as e:
        print(f"⚠️  对比测试失败: {str(e)}")

if __name__ == '__main__':
    print("优化OCR服务测试程序")
    print("=" * 60)
    
    try:
        success = test_optimized_ocr_service()
        
        if success:
            print("\n✅ 优化OCR服务测试通过")
            compare_with_original()
        else:
            print("\n❌ 优化OCR服务测试失败")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()