#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务模块
提供图片文本识别和智能字段匹配功能
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional
import tempfile
import base64
import requests
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入OCR相关库，如果失败则使用简化版本
try:
    import cv2  # type: ignore
    import numpy as np
    from PIL import Image
    import pytesseract  # type: ignore
    OCR_AVAILABLE = True
    logger.info("完整OCR库导入成功")
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"OCR库导入失败: {str(e)}")
    # 创建占位符以避免NameError
    cv2 = None
    np = None
    Image = None
    pytesseract = None
    
    # 导入简化版本
    try:
        from simple_ocr import SimpleOCR
        SIMPLE_OCR_AVAILABLE = True
        logger.info("简化OCR库导入成功")
    except ImportError as e:
        SIMPLE_OCR_AVAILABLE = False
        logger.warning(f"简化OCR库导入失败: {str(e)}")
        SimpleOCR = None

class OCRService:
    """OCR服务类"""
    
    def __init__(self):
        """初始化OCR服务"""
        # 如果没有完整的OCR库，使用简化版本
        if not OCR_AVAILABLE and SIMPLE_OCR_AVAILABLE:
            self.simple_ocr = SimpleOCR()
            logger.info("使用简化OCR服务")
        else:
            self.simple_ocr = None

        # 字段映射配置 - 只保留4个关键字段
        self.field_mapping = {
            'company_name': [
                '公司名称', '甲方', '甲方名称', '企业名称', '单位名称', 
                '公司', '企业', '单位', '名称', '机构名称', '企业法人营业执照',
                '营业执照', '法人名称', '企业法人', '法人单位', '经营者',
                '商户名称', '店铺名称', '商家名称', '机构', '组织名称',
                '全称', '企业全称', '公司全称', '单位全称', '法人'
            ],
            'tax_number': [
                '税号', '纳税人识别号', '统一社会信用代码', '税务登记号',
                '纳税识别号', '信用代码', '社会信用代码', '统一代码',
                '社会信用代码号', '信用代码号', '税务号', '纳税号',
                '识别号', '登记号', '代码', '编号', '证件号码'
            ],
            'reg_address': [
                '注册地址', '地址', '注册地', '企业地址', '公司地址',
                '营业地址', '办公地址', '联系地址', '住所', '经营场所',
                '注册住所', '企业住所', '经营地址', '营业场所', '办公场所',
                '详细地址', '具体地址', '所在地', '位置', '场所'
            ],
            'bank_name': [
                '开户行', '开户银行', '银行', '开户行名称', '银行名称',
                '基本户开户行', '基本账户开户行', '开户机构', '银行机构',
                '开户银行名称', '银行全称', '开户行全称', '金融机构',
                '存款银行', '账户银行', '银行支行', '分行', '支行'
            ]
        }
        
        # 常见分隔符
        self.separators = ['：', ':', '=', '：', '＝', '｜', '|', '\t']
        
    def preprocess_image(self, image_data: bytes):
        """
        预处理图片以提高OCR识别率

        Args:
            image_data: 图片二进制数据

        Returns:
            处理后的图片数组或原始数据
        """
        if not OCR_AVAILABLE or cv2 is None or np is None:
            return image_data

        try:
            # 将字节数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            # 解码图片
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("无法解码图片")

            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 应用高斯模糊减少噪声
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # 形态学操作去除噪声
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            return processed

        except Exception as e:
            logger.error(f"图片预处理失败: {str(e)}")
            # 如果预处理失败，返回原始数据
            return image_data
    
    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        从图片中提取文本

        Args:
            image_data: 图片二进制数据

        Returns:
            提取的文本内容
        """
        if not OCR_AVAILABLE or pytesseract is None:
            logger.warning("OCR库未安装，使用演示模式。请安装 pytesseract, pillow, opencv-python 以启用真实OCR功能")
            # 返回空字符串，让用户知道OCR不可用
            return ""

        # 检查Tesseract是否可用
        try:
            # 测试Tesseract是否安装
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error(f"Tesseract OCR引擎不可用: {str(e)}")
            # 尝试使用在线OCR服务
            logger.info("尝试使用在线OCR服务...")
            return self._try_online_ocr(image_data)

        try:
            # 预处理图片
            processed_img = self.preprocess_image(image_data)

            if processed_img is None:
                raise ValueError("图片处理失败")

            # 配置Tesseract参数 - 增强字符识别范围和准确性
            # 包含所有数字、大小写英文字母、中文字符、常用标点符号
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            
            # 使用Tesseract进行OCR识别
            # 尝试多种语言组合以提高识别准确率
            text_results = []
            
            # 方法1: 中英文混合识别 - 主要方法
            try:
                text1 = pytesseract.image_to_string(
                    processed_img,
                    lang='chi_sim+eng',  # 中文简体+英文
                    config=custom_config
                )
                text_results.append(text1)
                logger.info(f"中英文混合识别结果长度: {len(text1)}")
            except Exception as e:
                logger.warning(f"中英文混合识别失败: {str(e)}")
            
            # 方法2: 纯英文识别（对数字和英文字母更准确）
            try:
                text2 = pytesseract.image_to_string(
                    processed_img,
                    lang='eng',
                    config=custom_config + ' -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz()[]{}:;,.-_=+*&%$#@^~`/\\ '
                )
                text_results.append(text2)
                logger.info(f"纯英文识别结果长度: {len(text2)}")
            except Exception as e:
                logger.warning(f"纯英文识别失败: {str(e)}")
            
            # 方法3: 数字优化识别
            try:
                text3 = pytesseract.image_to_string(
                    processed_img,
                    lang='eng',
                    config='--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
                )
                text_results.append(text3)
                logger.info(f"数字优化识别结果长度: {len(text3)}")
            except Exception as e:
                logger.warning(f"数字优化识别失败: {str(e)}")
            
            # 方法4: 单行文本识别模式
            try:
                text4 = pytesseract.image_to_string(
                    processed_img,
                    lang='chi_sim+eng',
                    config='--oem 3 --psm 7'  # 单行文本模式
                )
                text_results.append(text4)
                logger.info(f"单行文本识别结果长度: {len(text4)}")
            except Exception as e:
                logger.warning(f"单行文本识别失败: {str(e)}")
            
            # 合并识别结果
            text = self._merge_ocr_results(text_results)

            # 清理文本
            text = self._clean_text(text)

            logger.info(f"OCR识别完成，提取文本长度: {len(text)}")
            return text

        except Exception as e:
            logger.error(f"OCR文本提取失败: {str(e)}")
            return ""

    def _try_online_ocr(self, image_data: bytes) -> str:
        """
        尝试使用在线OCR服务

        Args:
            image_data: 图片二进制数据

        Returns:
            提取的文本内容
        """
        logger.warning("在线OCR服务当前不可用")
        logger.info("免费的OCR.space API服务可能暂时不可用或已达到使用限制")
        
        # 直接返回空字符串，让系统使用简化OCR服务
        return ""
        
        # 注释掉原来的在线OCR实现，因为免费服务不稳定
        """
        try:
            # 使用免费的OCR.space API
            # 注意：这是一个演示用的免费服务，有使用限制

            # 将图片转换为base64
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 准备API请求
            url = 'https://api.ocr.space/parse/image'
            payload = {
                'base64Image': f'data:image/png;base64,{image_base64}',
                'language': 'chs',  # 中文简体
                'isOverlayRequired': False,
                'apikey': 'helloworld',  # 免费API密钥
                'OCREngine': 2
            }

            # 发送请求
            response = requests.post(url, data=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if result.get('IsErroredOnProcessing', True):
                    logger.error(f"在线OCR处理失败: {result.get('ErrorMessage', '未知错误')}")
                    return ""

                # 提取文本
                text_results = result.get('ParsedResults', [])
                if text_results:
                    extracted_text = text_results[0].get('ParsedText', '')
                    logger.info(f"在线OCR识别成功，提取文本长度: {len(extracted_text)}")
                    return extracted_text.strip()
                else:
                    logger.warning("在线OCR未识别到任何文本")
                    return ""
            else:
                logger.error(f"在线OCR API请求失败: {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"在线OCR网络请求失败: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"在线OCR处理异常: {str(e)}")
            return ""
        """

    def _get_demo_text(self) -> str:
        """
        获取演示用的文本（当OCR库不可用时）
        """
        return """公司名称：演示科技有限公司
税号：91330000123456789X
注册地址：浙江省杭州市西湖区演示路88号
注册电话：0571-88888888
开户行：中国演示银行杭州分行
银行账号：1234567890123456789
联系人：张演示
联系电话：13800138000
邮寄地址：浙江省杭州市西湖区演示路88号
简道云账号：demo12345678abcdefghijklmnop"""
    
    def _clean_text(self, text: str) -> str:
        """
        清理OCR识别的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符但保留中文标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff：:=（）()【】\[\]{}《》<>""''；;，,。.？?！!|/\\-_+*&%$#@^~`]', '', text)
        
        # 修复常见OCR错误
        replacements = {
            '0': 'O',  # 数字0可能被识别为字母O
            'l': '1',  # 字母l可能被识别为数字1
            'S': '5',  # 字母S可能被识别为数字5
        }
        
        # 只在特定上下文中进行替换
        for old, new in replacements.items():
            # 在数字上下文中进行替换
            text = re.sub(rf'(?<=\d){old}(?=\d)', new, text)
        
        return text.strip()
    
    def _merge_ocr_results(self, text_results: List[str]) -> str:
        """
        合并多个OCR识别结果，选择最佳结果
        
        Args:
            text_results: OCR识别结果列表
            
        Returns:
            合并后的最佳文本
        """
        if not text_results:
            return ""
        
        # 过滤空结果
        valid_results = [text.strip() for text in text_results if text.strip()]
        
        if not valid_results:
            return ""
        
        if len(valid_results) == 1:
            return valid_results[0]
        
        # 选择最长的结果作为主要结果
        main_result = max(valid_results, key=len)
        
        # 从其他结果中提取可能遗漏的数字和关键信息
        all_numbers = set()
        all_phones = set()
        all_accounts = set()
        
        for result in valid_results:
            # 提取数字序列
            numbers = re.findall(r'\d{3,}', result)
            all_numbers.update(numbers)
            
            # 提取手机号
            phones = re.findall(r'1[3-9]\d{9}', result)
            all_phones.update(phones)
            
            # 提取可能的账号
            accounts = re.findall(r'\d{10,25}', result)
            all_accounts.update(accounts)
        
        # 将提取的关键信息补充到主结果中
        supplementary_info = []
        
        for number in all_numbers:
            if number not in main_result:
                supplementary_info.append(number)
        
        if supplementary_info:
            main_result += "\n" + "\n".join(supplementary_info)
        
        return main_result
    
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
                                # 对特定字段进行值的清理和验证
                                cleaned_value = self._clean_field_value(field_name, value)
                                if cleaned_value:
                                    result[field_name] = cleaned_value
                                    logger.info(f"字段匹配成功: {key} -> {field_name} = {cleaned_value}")
                    break

        # 如果没有找到某些关键字段，尝试使用正则表达式进行模式匹配
        result = self._pattern_match_fields(text, result)

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

    def _clean_field_value(self, field_name: str, value: str) -> str:
        """
        清理和验证字段值

        Args:
            field_name: 字段名
            value: 原始值

        Returns:
            清理后的值
        """
        value = value.strip()

        # 移除常见的无用字符
        value = re.sub(r'^[：:=\s]+|[：:=\s]+$', '', value)

        if field_name == 'tax_number':
            # 税号清理：保留字母和数字
            value = re.sub(r'[^A-Za-z0-9]', '', value)
            value = value.upper()
            # 修复常见的OCR识别错误
            value = self._fix_ocr_errors(value, 'tax_number')

        return value

    def _fix_ocr_errors(self, text: str, field_type: str = None) -> str:
        """
        修复常见的OCR识别错误
        
        Args:
            text: 原始文本
            field_type: 字段类型 ('tax_number', 'phone', 'account')
            
        Returns:
            修复后的文本
        """
        if not text:
            return text
        
        # 常见的OCR字符识别错误映射
        char_fixes = {
            'O': '0',  # 字母O -> 数字0
            'o': '0',  # 小写o -> 数字0
            'I': '1',  # 字母I -> 数字1
            'l': '1',  # 小写l -> 数字1
            'S': '5',  # 字母S -> 数字5
            'Z': '2',  # 字母Z -> 数字2
            'B': '8',  # 字母B -> 数字8
            'G': '6',  # 字母G -> 数字6
            'D': '0',  # 字母D -> 数字0 (在某些情况下)
            'Q': '0',  # 字母Q -> 数字0 (在某些情况下)
        }
        
        fixed_text = text
        
        if field_type == 'tax_number':
            # 对于税号，全面修复数字位置的错误
            # 统一社会信用代码：18位字母数字组合
            for old_char, new_char in char_fixes.items():
                fixed_text = fixed_text.replace(old_char, new_char)
        elif field_type in ['phone', 'account']:
            # 对于电话号码和账号，修复所有数字错误
            for old_char, new_char in char_fixes.items():
                fixed_text = fixed_text.replace(old_char, new_char)
        else:
            # 对于其他字段，只修复明显的数字序列中的错误
            import re
            # 查找数字序列并修复
            def fix_number_sequence(match):
                number_str = match.group(0)
                for old_char, new_char in char_fixes.items():
                    number_str = number_str.replace(old_char, new_char)
                return number_str
            
            # 修复3位以上的数字序列
            fixed_text = re.sub(r'[0-9OoIlSZBGDQ]{3,}', fix_number_sequence, fixed_text)
        
        return fixed_text

    def _pattern_match_fields(self, text: str, existing_result: Dict[str, str]) -> Dict[str, str]:
        """
        使用正则表达式模式匹配字段 - 专门针对用户需要的6个关键字段优化

        Args:
            text: 完整文本
            existing_result: 已有的解析结果

        Returns:
            更新后的结果字典
        """
        result = existing_result.copy()

        # 1. 智能识别公司名称 - 最高优先级
        if 'company_name' not in result:
            company_patterns = [
                # 直接标识的公司名称
                r'公司名称[：:\s]*([^\n\r]+?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                r'企业名称[：:\s]*([^\n\r]+?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                r'名\s*称[：:\s]*([^\n\r]+?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                r'甲方[：:\s]*([^\n\r]+?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                r'法人[：:\s]*([^\n\r]+?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                # 包含公司关键词的名称
                r'([^\n\r]*?(?:有限公司|股份有限公司|集团有限公司|科技有限公司|贸易有限公司|投资有限公司|实业有限公司|发展有限公司|建设有限公司|工程有限公司|咨询有限公司|服务有限公司|管理有限公司))(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                r'([^\n\r]*?(?:公司|企业|集团|中心|研究院|工厂|厂|店|社|部|局|委|会))(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)',
                # 营业执照第一行通常是公司名称
                r'^([^\n\r]*?(?:有限公司|股份有限公司|集团|企业|公司|中心|研究院|工厂)[^\n\r]*?)$',
                # 通用模式：不包含数字开头的长文本
                r'^([^\n\r\d][^\n\r]{6,50}?)(?=\s*税号|\s*统一社会信用代码|\s*地址|\s*$)'
            ]
            
            for pattern in company_patterns:
                company_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if company_match:
                    company_name = company_match.group(1).strip()
                    # 严格过滤：长度、内容、格式检查
                    if (len(company_name) >= 4 and len(company_name) <= 100 and 
                        not any(word in company_name for word in ['税号', '地址', '电话', '账号', '银行', '开户行', '代码']) and 
                        not re.match(r'^\d+$', company_name) and
                        not re.match(r'^[0-9A-Z]{15,18}$', company_name)):  # 排除税号
                        company_name = re.sub(r'^[：:\s]+|[：:\s]+$', '', company_name)
                        result['company_name'] = company_name
                        logger.info(f"智能识别公司名称: {company_name}")
                        break

        # 2. 智能识别税号（统一社会信用代码）- 高优先级
        if 'tax_number' not in result:
            tax_patterns = [
                # 直接标识的税号
                r'税号[：:\s]*([A-Z0-9]{15,18})',
                r'统一社会信用代码[：:\s]*([A-Z0-9]{15,18})',
                r'信用代码[：:\s]*([A-Z0-9]{15,18})',
                r'纳税人识别号[：:\s]*([A-Z0-9]{15,18})',
                r'代码[：:\s]*([A-Z0-9]{15,18})',
                r'编号[：:\s]*([A-Z0-9]{15,18})',
                # 标准格式匹配
                r'9[0-9A-HJ-NPQRTUWXY]{17}',  # 18位统一社会信用代码
                r'[0-9A-HJ-NPQRTUWXY]{18}',   # 18位统一社会信用代码（不限开头）
                r'\d{15}',                     # 15位旧版税号
                r'[0-9A-Z]{15,18}',           # 15-18位字母数字组合
                # 宽松匹配
                r'[A-Z0-9]{15,18}'
            ]
            
            for pattern in tax_patterns:
                tax_matches = re.findall(pattern, text.upper())
                for tax_number in tax_matches:
                    # 修复OCR错误并验证税号格式
                    tax_number = self._fix_ocr_errors(tax_number, 'tax_number')
                    if self._validate_tax_number(tax_number):
                        result['tax_number'] = tax_number
                        logger.info(f"智能识别税号: {tax_number}")
                        break
                if 'tax_number' in result:
                    break

        # 3. 智能识别注册地址 - 高优先级
        if 'reg_address' not in result:
            address_patterns = [
                # 直接标识的地址
                r'注册地址[：:\s]*([^\n\r]+?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                r'地址[：:\s]*([^\n\r]+?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                r'住所[：:\s]*([^\n\r]+?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                r'详细地址[：:\s]*([^\n\r]+?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                r'具体地址[：:\s]*([^\n\r]+?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                # 包含地理标识的地址
                r'([^\n\r]*?(?:省|市|区|县|街|路|号|栋|楼|室|层|村|镇|乡)[^\n\r]*?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                # 主要城市地址
                r'([^\n\r]*?(?:北京|上海|天津|重庆|广东|江苏|浙江|山东|河南|四川|湖北|湖南|河北|福建|安徽|陕西|辽宁|山西|黑龙江|吉林|江西|广西|云南|贵州|甘肃|海南|青海|宁夏|新疆|西藏|内蒙古)[^\n\r]*?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)',
                r'([^\n\r]*?(?:昆明|北京|上海|广州|深圳|杭州|南京|成都|武汉|西安|郑州|济南|福州|合肥|长沙|石家庄|太原|沈阳|长春|哈尔滨|南昌|南宁|贵阳|兰州|海口|西宁|银川|乌鲁木齐|拉萨|呼和浩特)[^\n\r]*?)(?=\s*电话|\s*开户行|\s*银行|\s*账号|\s*$)'
            ]
            
            for pattern in address_patterns:
                address_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if address_match:
                    address = address_match.group(1).strip()
                    # 严格过滤：长度、内容检查
                    if (len(address) >= 8 and len(address) <= 200 and 
                        not any(word in address for word in ['税号', '电话', '账号', '银行', '公司名称', '开户行']) and
                        not re.match(r'^\d+$', address) and
                        not re.match(r'^[0-9A-Z]{15,18}$', address)):  # 排除税号
                        address = re.sub(r'^[：:\s]+|[：:\s]+$', '', address)
                        result['reg_address'] = address
                        logger.info(f"智能识别注册地址: {address}")
                        break

        # 4. 智能识别开户行 - 中优先级
        if 'bank_name' not in result:
            bank_patterns = [
                # 直接标识的银行
                r'开户行[：:\s]*([^\n\r]*?(?:银行|农村信用社|邮政储蓄|信用合作社)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                r'银行[：:\s]*([^\n\r]*?(?:银行|农村信用社|邮政储蓄|信用合作社)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                r'开户银行[：:\s]*([^\n\r]*?(?:银行|农村信用社|邮政储蓄|信用合作社)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                # 主要银行名称匹配
                r'([^\n\r]*?(?:中国工商银行|中国农业银行|中国银行|中国建设银行|交通银行|招商银行|浦发银行|中信银行|中国光大银行|华夏银行|中国民生银行|广发银行|平安银行|兴业银行|上海银行|北京银行|宁波银行|南京银行)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                r'([^\n\r]*?(?:工商银行|农业银行|建设银行|中国银行|交通银行|招商银行|浦发银行|中信银行|光大银行|华夏银行|民生银行|广发银行|平安银行|兴业银行)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                # 通用银行匹配
                r'([^\n\r]*?(?:银行|农村信用社|邮政储蓄|信用合作社)[^\n\r]*?)(?=\s*账号|\s*帐号|\s*$)',
                r'([^\n\r]*银行[^\n\r]*)',
                r'([^\n\r]*信用社[^\n\r]*)',
                r'([^\n\r]*邮政储蓄[^\n\r]*)'
            ]
            
            for pattern in bank_patterns:
                bank_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if bank_match:
                    bank_name = bank_match.group(1).strip()
                    # 严格过滤：长度、内容检查
                    if (len(bank_name) >= 4 and len(bank_name) <= 100 and 
                        not any(word in bank_name for word in ['税号', '地址', '电话', '公司名称']) and
                        not re.match(r'^\d+$', bank_name) and
                        not re.match(r'^[0-9A-Z]{15,18}$', bank_name)):  # 排除税号
                        bank_name = re.sub(r'^[：:\s]+|[：:\s]+$', '', bank_name)
                        result['bank_name'] = bank_name
                        logger.info(f"智能识别开户行: {bank_name}")
                        break

        # 5. 智能识别注册电话 - 中优先级
        if 'reg_phone' not in result:
            phone_patterns = [
                # 直接标识的注册电话
                r'注册电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                r'企业电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                r'公司电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                r'固定电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                r'座机[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                r'办公电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*开户行|\s*银行|\s*账号|\s*联系人|\s*$)',
                # 电话号码格式匹配（区号+号码）
                r'([0-9]{3,4}\-[0-9]{7,8})',  # 0571-88888888格式
                r'(\([0-9]{3,4}\)[0-9]{7,8})',  # (0571)88888888格式
                r'([0-9]{3,4}\s[0-9]{7,8})',  # 0571 88888888格式
                # 手机号码格式（作为备选）
                r'(1[3-9][0-9]{9})'  # 11位手机号
            ]
            
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, text)
                for phone_number in phone_matches:
                    # 清理电话号码
                    phone_clean = re.sub(r'[^\d\-\(\)\s]', '', phone_number).strip()
                    # 验证电话号码格式
                    if self._validate_phone_number(phone_clean):
                        result['reg_phone'] = phone_clean
                        logger.info(f"智能识别注册电话: {phone_clean}")
                        break
                if 'reg_phone' in result:
                    break

        # 6. 智能识别银行账号 - 中优先级
        if 'bank_account' not in result:
            account_patterns = [
                # 直接标识的银行账号
                r'银行账号[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'账号[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'银行账户[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'账户号[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'基本户账号[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'基本账户[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'对公账户[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'企业账户[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                r'公司账户[：:\s]*([0-9\s]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                # 纯数字账号匹配（10-25位）
                r'([0-9]{10,25})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)',
                # 带空格的账号匹配
                r'([0-9\s]{12,30})(?=\s*联系人|\s*联系电话|\s*邮寄地址|\s*简道云|\s*$)'
            ]
            
            for pattern in account_patterns:
                account_matches = re.findall(pattern, text)
                for account_number in account_matches:
                    # 清理账号（移除空格）
                    account_clean = re.sub(r'\s', '', account_number).strip()
                    # 验证账号格式
                    if self._validate_bank_account(account_clean):
                        result['bank_account'] = account_clean
                        logger.info(f"智能识别银行账号: {account_clean}")
                        break
                if 'bank_account' in result:
                    break

        # 7. 智能识别联系人 - 低优先级
        if 'contact_name' not in result:
            contact_patterns = [
                r'联系人[：:\s]*([^\n\r\d]+?)(?=\s*联系电话|\s*手机|\s*邮寄地址|\s*简道云|\s*$)',
                r'负责人[：:\s]*([^\n\r\d]+?)(?=\s*联系电话|\s*手机|\s*邮寄地址|\s*简道云|\s*$)',
                r'经办人[：:\s]*([^\n\r\d]+?)(?=\s*联系电话|\s*手机|\s*邮寄地址|\s*简道云|\s*$)',
                r'联系人姓名[：:\s]*([^\n\r\d]+?)(?=\s*联系电话|\s*手机|\s*邮寄地址|\s*简道云|\s*$)'
            ]
            
            for pattern in contact_patterns:
                contact_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if contact_match:
                    contact_name = contact_match.group(1).strip()
                    if (len(contact_name) >= 2 and len(contact_name) <= 20 and 
                        not any(word in contact_name for word in ['税号', '地址', '电话', '账号', '银行', '公司']) and
                        not re.match(r'^\d+$', contact_name)):
                        contact_name = re.sub(r'^[：:\s]+|[：:\s]+$', '', contact_name)
                        result['contact_name'] = contact_name
                        logger.info(f"智能识别联系人: {contact_name}")
                        break

        # 8. 智能识别联系电话 - 低优先级
        if 'contact_phone' not in result:
            contact_phone_patterns = [
                r'联系电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*邮寄地址|\s*简道云|\s*$)',
                r'手机[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*邮寄地址|\s*简道云|\s*$)',
                r'手机号[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*邮寄地址|\s*简道云|\s*$)',
                r'移动电话[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*邮寄地址|\s*简道云|\s*$)',
                r'联系手机[：:\s]*([0-9\-\s\(\)]{7,20})(?=\s*邮寄地址|\s*简道云|\s*$)',
                # 手机号码格式匹配
                r'(1[3-9][0-9]{9})'  # 11位手机号
            ]
            
            for pattern in contact_phone_patterns:
                phone_matches = re.findall(pattern, text)
                for phone_number in phone_matches:
                    phone_clean = re.sub(r'[^\d\-\(\)\s]', '', phone_number).strip()
                    if self._validate_phone_number(phone_clean):
                        result['contact_phone'] = phone_clean
                        logger.info(f"智能识别联系电话: {phone_clean}")
                        break
                if 'contact_phone' in result:
                    break

        # 9. 智能识别邮寄地址 - 低优先级
        if 'mail_address' not in result:
            mail_patterns = [
                r'邮寄地址[：:\s]*([^\n\r]+?)(?=\s*简道云|\s*$)',
                r'通讯地址[：:\s]*([^\n\r]+?)(?=\s*简道云|\s*$)',
                r'收件地址[：:\s]*([^\n\r]+?)(?=\s*简道云|\s*$)',
                r'快递地址[：:\s]*([^\n\r]+?)(?=\s*简道云|\s*$)',
                r'寄送地址[：:\s]*([^\n\r]+?)(?=\s*简道云|\s*$)'
            ]
            
            for pattern in mail_patterns:
                mail_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if mail_match:
                    mail_address = mail_match.group(1).strip()
                    if (len(mail_address) >= 8 and len(mail_address) <= 200 and 
                        not any(word in mail_address for word in ['税号', '电话', '账号', '银行', '公司名称']) and
                        not re.match(r'^\d+$', mail_address)):
                        mail_address = re.sub(r'^[：:\s]+|[：:\s]+$', '', mail_address)
                        result['mail_address'] = mail_address
                        logger.info(f"智能识别邮寄地址: {mail_address}")
                        break

        # 10. 智能识别简道云账号 - 低优先级
        if 'jdy_account' not in result:
            jdy_patterns = [
                r'简道云账号[：:\s]*([^\n\r\s]+?)(?=\s*$)',
                r'简道云[：:\s]*([^\n\r\s]+?)(?=\s*$)',
                r'JDY账号[：:\s]*([^\n\r\s]+?)(?=\s*$)',
                r'jdy账号[：:\s]*([^\n\r\s]+?)(?=\s*$)',
                # 匹配长字符串（可能是简道云账号）
                r'([a-zA-Z0-9]{15,30})(?=\s*$)'
            ]
            
            for pattern in jdy_patterns:
                jdy_matches = re.findall(pattern, text, re.IGNORECASE)
                for jdy_account in jdy_matches:
                    jdy_clean = jdy_account.strip()
                    if (len(jdy_clean) >= 10 and len(jdy_clean) <= 50 and 
                        not jdy_clean.isdigit() and  # 不是纯数字
                        not re.match(r'^[0-9A-Z]{15,18}$', jdy_clean)):  # 不是税号格式
                        result['jdy_account'] = jdy_clean
                        logger.info(f"智能识别简道云账号: {jdy_clean}")
                        break
                if 'jdy_account' in result:
                    break

        return result
    
    def _validate_phone_number(self, phone: str) -> bool:
        """
        验证电话号码格式
        
        Args:
            phone: 电话号码
            
        Returns:
            是否为有效电话号码
        """
        if not phone:
            return False
        
        # 移除所有非数字字符进行验证
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # 手机号码：11位，以1开头
        if len(digits_only) == 11 and digits_only.startswith('1'):
            return True
        
        # 固定电话：7-12位（包含区号）
        if 7 <= len(digits_only) <= 12:
            return True
        
        return False
    
    def _validate_bank_account(self, account: str) -> bool:
        """
        验证银行账号格式
        
        Args:
            account: 银行账号
            
        Returns:
            是否为有效银行账号
        """
        if not account:
            return False
        
        # 移除所有非数字字符进行验证
        digits_only = re.sub(r'[^\d]', '', account)
        
        # 银行账号：通常10-25位数字
        if 10 <= len(digits_only) <= 25 and digits_only.isdigit():
            return True
        
        return False
    
    def _validate_tax_number(self, tax_number: str) -> bool:
        """
        验证税号格式是否正确
        
        Args:
            tax_number: 税号
            
        Returns:
            是否为有效税号
        """
        if not tax_number:
            return False
        
        # 18位统一社会信用代码验证
        if len(tax_number) == 18:
            # 第一位应该是数字或大写字母（除I、O、S、V、Z）
            if not re.match(r'^[0-9A-HJ-NPQRTUWXY]', tax_number.upper()):
                return False
            return True
        
        # 15位旧版税号验证
        if len(tax_number) == 15:
            return tax_number.isdigit()
        
        return False
    
    def process_image(self, image_data: bytes) -> Dict[str, any]:
        """
        处理图片的主要方法

        Args:
            image_data: 图片二进制数据

        Returns:
            处理结果字典
        """
        try:
            # 检查OCR是否可用
            if not OCR_AVAILABLE:
                # 尝试使用简化版本
                if self.simple_ocr:
                    return self.simple_ocr.process_image(image_data)
                else:
                    return {
                        'success': False,
                        'error': 'OCR功能不可用。请安装必要的依赖包：\n\npip install pytesseract pillow opencv-python\nbrew install tesseract tesseract-lang\n\n然后重启应用。',
                        'extracted_text': '',
                        'parsed_fields': {},
                        'field_count': 0,
                        'ocr_available': False
                    }

            # 检查Tesseract引擎是否可用
            try:
                pytesseract.get_tesseract_version()
                # Tesseract可用，使用本地OCR
                extracted_text = self.extract_text_from_image(image_data)
            except Exception as e:
                logger.error(f"Tesseract OCR引擎不可用: {str(e)}")
                logger.info("Tesseract不可用，尝试使用简化OCR服务...")
                
                # 直接使用简化OCR服务，不再尝试在线OCR
                if self.simple_ocr:
                    logger.info("使用简化OCR服务处理图片")
                    return self.simple_ocr.process_image(image_data)
                else:
                    return {
                        'success': False,
                        'error': 'OCR识别失败。Tesseract不可用且简化OCR服务也不可用。\n\n请安装Tesseract OCR引擎：\n\n方案1（推荐）：\nbrew install tesseract tesseract-lang\n\n方案2：\nconda install -c conda-forge tesseract\n\n安装完成后重启应用。',
                        'extracted_text': '',
                        'parsed_fields': {},
                        'field_count': 0,
                        'ocr_available': True,
                        'tesseract_available': False
                    }

            # 解析字段
            parsed_fields = self.parse_text_to_fields(extracted_text)

            return {
                'success': True,
                'extracted_text': extracted_text,
                'parsed_fields': parsed_fields,
                'field_count': len(parsed_fields),
                'ocr_available': True
            }

        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'extracted_text': '',
                'parsed_fields': {},
                'field_count': 0,
                'ocr_available': OCR_AVAILABLE
            }
