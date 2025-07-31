#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的OCR实现
当Tesseract不可用时的备用方案
"""

import base64
import io
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SimpleOCR:
    """简化的OCR服务类"""
    
    def __init__(self):
        """初始化简化OCR服务"""
        # 字段映射配置
        self.field_mapping = {
            'company_name': [
                '公司名称', '甲方', '甲方名称', '企业名称', '单位名称', 
                '公司', '企业', '单位', '名称', '机构名称'
            ],
            'tax_number': [
                '税号', '纳税人识别号', '统一社会信用代码', '税务登记号',
                '纳税识别号', '信用代码', '社会信用代码'
            ],
            'reg_address': [
                '注册地址', '地址', '注册地', '企业地址', '公司地址',
                '营业地址', '办公地址', '联系地址'
            ],
            'reg_phone': [
                '注册电话', '电话', '联系电话', '固定电话', '办公电话',
                '公司电话', '座机', '固话'
            ],
            'bank_name': [
                '开户行', '开户银行', '银行', '开户行名称', '银行名称',
                '基本户开户行', '基本账户开户行'
            ],
            'bank_account': [
                '账号', '银行账号', '账户', '银行账户', '基本户账号',
                '对公账号', '基本账户', '开户账号'
            ],
            'contact_name': [
                '联系人', '联系人姓名', '负责人', '经办人', '联系人名称',
                '法人', '法定代表人', '代表人'
            ],
            'contact_phone': [
                '联系人电话', '手机', '手机号', '移动电话', '联系方式',
                '联系人手机', '手机号码', '电话号码'
            ],
            'mail_address': [
                '邮寄地址', '收件地址', '快递地址', '邮件地址', '寄送地址',
                '收货地址', '通讯地址'
            ],
            'jdy_account': [
                '简道云账号', '简道云ID', 'JDY账号', 'JDY_ID', '账号ID',
                '用户ID', '客户ID', '系统账号'
            ]
        }
        
        # 常见分隔符
        self.separators = ['：', ':', '=', '：', '＝', '｜', '|', '\t']
    
    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        从图片中提取文本 - 简化版本
        
        Args:
            image_data: 图片二进制数据
            
        Returns:
            提取的文本内容
        """
        try:
            # 检查图片大小和格式
            if len(image_data) < 1000:
                logger.warning("图片文件太小，可能不是有效的图片")
                return ""
            
            # 检查图片头部信息
            if image_data.startswith(b'\xff\xd8\xff'):
                logger.info("检测到JPEG格式图片")
            elif image_data.startswith(b'\x89PNG'):
                logger.info("检测到PNG格式图片")
            else:
                logger.info("检测到其他格式图片")
            
            # 由于没有真实的OCR引擎，我们提供一个诚实的错误信息
            logger.error("OCR引擎不可用：需要安装Tesseract OCR")
            return ""
            
        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            return ""
    
    def parse_text_to_fields(self, text: str) -> Dict[str, str]:
        """
        解析文本并映射到表单字段
        
        Args:
            text: OCR识别的文本
            
        Returns:
            字段映射字典
        """
        result = {}
        
        if not text:
            return result
        
        # 按行分割文本
        lines = text.split('\n')
        
        # 处理每一行
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试不同的分隔符
            for separator in self.separators:
                if separator in line:
                    parts = line.split(separator, 1)  # 只分割第一个分隔符
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        if key and value:
                            # 查找匹配的字段
                            field_name = self._find_matching_field(key)
                            if field_name:
                                result[field_name] = value
                                logger.info(f"字段匹配成功: {key} -> {field_name} = {value}")
                    break
        
        return result
    
    def _find_matching_field(self, key: str) -> Optional[str]:
        """
        查找匹配的字段名
        
        Args:
            key: 待匹配的键名
            
        Returns:
            匹配的字段名，如果没有匹配则返回None
        """
        key = key.strip()
        
        # 精确匹配
        for field_name, patterns in self.field_mapping.items():
            if key in patterns:
                return field_name
        
        # 模糊匹配
        for field_name, patterns in self.field_mapping.items():
            for pattern in patterns:
                if pattern in key or key in pattern:
                    return field_name
        
        return None
    
    def process_image(self, image_data: bytes) -> Dict[str, any]:
        """
        处理图片的主要方法
        
        Args:
            image_data: 图片二进制数据
            
        Returns:
            处理结果字典
        """
        try:
            # 检查图片数据
            if not image_data or len(image_data) < 100:
                return {
                    'success': False,
                    'error': '图片数据无效或文件太小',
                    'extracted_text': '',
                    'parsed_fields': {},
                    'field_count': 0,
                    'ocr_available': False
                }
            
            # 直接返回OCR不可用的信息，不尝试提取文本
            return {
                'success': False,
                'error': 'OCR功能不可用。\n\n要启用真实的图片文字识别功能，请安装以下依赖：\n\n1. 安装Tesseract OCR引擎：\n   brew install tesseract tesseract-lang\n\n2. 安装Python依赖包：\n   pip install pytesseract pillow opencv-python\n\n3. 重启应用\n\n当前系统只能处理已有的文本数据，无法识别图片中的文字。',
                'extracted_text': '',
                'parsed_fields': {},
                'field_count': 0,
                'ocr_available': False,
                'image_received': True,  # 表示图片已接收
                'image_size': len(image_data)  # 图片大小
            }
            
        except Exception as e:
            logger.error(f"处理图片时发生错误: {str(e)}")
            return {
                'success': False,
                'error': f'处理图片时发生错误: {str(e)}',
                'extracted_text': '',
                'parsed_fields': {},
                'field_count': 0,
                'ocr_available': False
            }
