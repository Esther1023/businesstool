# ⚡ OCR系统快速部署指南

## 🚀 Railway部署（推荐，5分钟完成）

### 1. 准备代码
```bash
# 确保所有文件都已提交
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 2. Railway部署
1. 访问 [railway.app](https://railway.app)
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的仓库
5. 等待自动部署完成（约2-3分钟）

### 3. 配置环境变量
在Railway项目设置中添加：
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
```

### 4. 获取域名
- Railway会自动分配一个域名，如：`your-app-name.railway.app`
- 可以在项目设置中绑定自定义域名

### 5. 验证部署
```bash
# 使用提供的测试脚本
python3 test_deployment.py https://your-app-name.railway.app
```

## 🎨 Render部署（免费选项）

### 1. 创建Web Service
1. 访问 [render.com](https://render.com)
2. 点击 "New" → "Web Service"
3. 连接GitHub仓库

### 2. 配置设置
- **Name**: ocr-system
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 3. 环境变量
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

## 🐳 Docker部署

### 本地测试
```bash
# 构建镜像
docker build -t ocr-system .

# 运行容器
docker run -p 8080:8080 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  -e PORT=8080 \
  ocr-system
```

### 云平台部署
可以将Docker镜像推送到：
- Google Cloud Run
- AWS ECS
- Azure Container Instances

## ⚙️ 必需的环境变量

```bash
# 必需
FLASK_ENV=production
SECRET_KEY=your-super-secret-key

# 可选
LOG_LEVEL=INFO
PORT=8080  # 通常由平台自动设置
```

## ✅ 部署检查清单

- [ ] 代码已推送到Git仓库
- [ ] requirements.txt包含所有依赖
- [ ] 环境变量已正确设置
- [ ] SECRET_KEY已更改为强密码
- [ ] 应用可以正常启动
- [ ] 所有功能测试通过

## 🔧 常见问题快速修复

### 问题：应用无法启动
```bash
# 检查日志
# Railway: 在项目面板查看
# Render: 在服务页面查看日志
# Docker: docker logs container_name
```

### 问题：OCR功能不工作
确保aptfile包含：
```
tesseract-ocr
tesseract-ocr-chi-sim
tesseract-ocr-eng
```

### 问题：文件上传失败
检查平台的文件大小限制，通常为：
- Railway: 100MB
- Render: 100MB
- Heroku: 30MB

## 📞 获取帮助

- 查看详细文档：`DEPLOYMENT.md`
- 运行测试脚本：`python3 test_deployment.py <URL>`
- 检查健康状态：`https://your-app.com/health`

---
**预计部署时间：5-10分钟** ⏱️
