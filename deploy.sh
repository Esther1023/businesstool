#!/bin/bash

# OCR图片识别系统部署脚本
# 支持多种部署平台

set -e

echo "🚀 开始部署OCR图片识别系统..."

# 检查必要文件
echo "📋 检查部署文件..."
required_files=("app.py" "requirements.txt" "Procfile" "config.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少必要文件: $file"
        exit 1
    fi
done
echo "✅ 所有必要文件检查完成"

# 检查环境变量
echo "🔧 检查环境变量..."
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=production
    echo "⚠️  FLASK_ENV未设置，默认使用production"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  建议设置SECRET_KEY环境变量"
fi

# 安装依赖（本地测试用）
if [ "$1" = "local" ]; then
    echo "📦 安装本地依赖..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
    
    echo "🧪 运行本地测试..."
    python app.py &
    APP_PID=$!
    sleep 5
    
    # 简单健康检查
    if curl -f http://localhost:5001 > /dev/null 2>&1; then
        echo "✅ 本地测试成功"
        kill $APP_PID
    else
        echo "❌ 本地测试失败"
        kill $APP_PID
        exit 1
    fi
fi

echo "🎉 部署准备完成！"
echo ""
echo "📝 下一步操作："
echo "1. 将代码推送到Git仓库"
echo "2. 在Railway/Render等平台连接仓库"
echo "3. 设置环境变量"
echo "4. 部署应用"
