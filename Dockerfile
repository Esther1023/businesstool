# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 更新 pip 版本（在安装依赖之前）
RUN pip install --upgrade pip

# 创建非 root 用户（在复制文件之前）
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 复制requirements文件
COPY --chown=appuser:appuser requirements.txt .

# 安装Python依赖（现在以非 root 用户运行）
RUN pip install --user --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p logs uploads out_data

# 设置环境变量
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PATH="/home/appuser/.local/bin:${PATH}"

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD gunicorn --bind 0.0.0.0:$PORT app:app --workers 1 --timeout 120