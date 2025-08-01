#!/bin/bash
echo "🧪 测试OCR功能..."
source venv/bin/activate

echo "1. 测试原始OCR服务..."
python3 test_ocr.py

echo ""
echo "2. 测试优化OCR服务..."
python3 test_ocr_optimized.py
