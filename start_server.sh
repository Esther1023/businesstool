#!/bin/bash

# 设置端口为8081（因为8080已被占用）
export PORT=8081

echo "Starting server on port $PORT..."

# 启动Flask应用
python app.py