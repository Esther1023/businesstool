#!/bin/bash
echo "🚀 启动智能表单填充应用..."
echo "📍 项目目录: $(pwd)"
echo "🐍 Python环境: 虚拟环境"
echo "🔗 访问地址: http://localhost:5001"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动应用
python3 app.py
