#!/bin/bash

# 智能表单填充功能 - OCR依赖安装脚本
# 适用于 macOS 系统

echo "🚀 开始安装智能表单填充功能的OCR依赖..."

# 检查是否安装了 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未检测到 Homebrew，请先安装 Homebrew："
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ 检测到 Homebrew"

# 安装 Tesseract OCR 引擎
echo "📦 安装 Tesseract OCR 引擎..."
if brew list tesseract &> /dev/null; then
    echo "✅ Tesseract 已安装"
else
    brew install tesseract
    if [ $? -eq 0 ]; then
        echo "✅ Tesseract 安装成功"
    else
        echo "❌ Tesseract 安装失败"
        exit 1
    fi
fi

# 安装中文语言包
echo "📦 安装中文语言包..."
if brew list tesseract-lang &> /dev/null; then
    echo "✅ 中文语言包已安装"
else
    brew install tesseract-lang
    if [ $? -eq 0 ]; then
        echo "✅ 中文语言包安装成功"
    else
        echo "⚠️  中文语言包安装失败，但不影响基本功能"
    fi
fi

# 验证 Tesseract 安装
echo "🔍 验证 Tesseract 安装..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract 可执行文件已安装"
    tesseract --version
    echo ""
    echo "📋 支持的语言："
    tesseract --list-langs
else
    echo "❌ Tesseract 安装验证失败"
    exit 1
fi

# 安装 Python 依赖
echo "🐍 安装 Python 依赖包..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ 检测到 Python $python_version"

# 安装依赖包
echo "📦 安装 pytesseract..."
python3 -m pip install pytesseract --timeout 60
if [ $? -eq 0 ]; then
    echo "✅ pytesseract 安装成功"
else
    echo "❌ pytesseract 安装失败"
    exit 1
fi

echo "📦 安装 Pillow..."
python3 -m pip install Pillow --timeout 60
if [ $? -eq 0 ]; then
    echo "✅ Pillow 安装成功"
else
    echo "❌ Pillow 安装失败"
    exit 1
fi

echo "📦 安装 opencv-python..."
python3 -m pip install opencv-python --timeout 60
if [ $? -eq 0 ]; then
    echo "✅ opencv-python 安装成功"
else
    echo "❌ opencv-python 安装失败"
    exit 1
fi

# 测试安装
echo "🧪 测试 OCR 功能..."
python3 -c "
try:
    import pytesseract
    import cv2
    from PIL import Image
    print('✅ 所有 OCR 依赖导入成功')
    
    # 测试 Tesseract 连接
    version = pytesseract.get_tesseract_version()
    print(f'✅ Tesseract 版本: {version}')
    
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️  测试时出现问题: {e}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 OCR 依赖安装完成！"
    echo ""
    echo "📋 安装总结："
    echo "   ✅ Tesseract OCR 引擎"
    echo "   ✅ 中文语言包"
    echo "   ✅ pytesseract Python 包"
    echo "   ✅ Pillow 图像处理库"
    echo "   ✅ OpenCV Python 包"
    echo ""
    echo "🚀 现在可以使用智能表单填充功能了！"
    echo "   重启应用：python3 app.py"
    echo "   访问：http://localhost:5001"
else
    echo "❌ 安装过程中出现问题，请检查错误信息"
    exit 1
fi
