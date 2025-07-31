# 🚀 OCR图片识别系统生产环境部署指南

## 📋 目录
1. [部署平台选择](#部署平台选择)
2. [Railway部署教程](#railway部署教程)
3. [Render部署教程](#render部署教程)
4. [Docker部署教程](#docker部署教程)
5. [环境变量配置](#环境变量配置)
6. [部署后验证](#部署后验证)
7. [常见问题排查](#常见问题排查)

## 🏆 部署平台选择

### 推荐平台对比

| 平台 | 优点 | 缺点 | 费用 | 适用场景 |
|------|------|------|------|----------|
| **Railway** ⭐⭐⭐⭐⭐ | 简单易用、自动部署、支持Docker | 相对较新 | 免费5$/月 | **最推荐** |
| **Render** ⭐⭐⭐⭐ | 免费HTTPS、自动部署 | 免费版有限制 | 免费版可用 | 个人项目 |
| **Heroku** ⭐⭐⭐ | 成熟稳定、插件丰富 | 价格较高 | 7$/月起 | 企业级应用 |

## 🚂 Railway部署教程（推荐）

### 步骤1：准备代码仓库
```bash
# 1. 初始化Git仓库（如果还没有）
git init
git add .
git commit -m "Initial commit for production deployment"

# 2. 推送到GitHub/GitLab
git remote add origin https://github.com/yourusername/ocr-system.git
git push -u origin main
```

### 步骤2：Railway部署
1. 访问 [Railway.app](https://railway.app)
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择您的OCR项目仓库
5. Railway会自动检测到Python项目并开始部署

### 步骤3：配置环境变量
在Railway项目设置中添加以下环境变量：
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
PORT=8080
LOG_LEVEL=INFO
```

### 步骤4：自定义域名（可选）
1. 在Railway项目设置中点击 "Domains"
2. 添加自定义域名或使用Railway提供的域名
3. Railway会自动配置HTTPS

## 🎨 Render部署教程

### 步骤1：创建Render账号
1. 访问 [Render.com](https://render.com)
2. 使用GitHub账号注册/登录

### 步骤2：创建Web Service
1. 点击 "New" → "Web Service"
2. 连接GitHub仓库
3. 配置部署设置：
   - **Name**: ocr-system
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 步骤3：配置环境变量
在Render的Environment页面添加：
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

## 🐳 Docker部署教程

### 本地Docker测试
```bash
# 1. 构建镜像
docker build -t ocr-system .

# 2. 运行容器
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  ocr-system
```

### 云平台Docker部署
可以将Docker镜像部署到：
- Google Cloud Run
- AWS ECS
- Azure Container Instances
- 阿里云容器服务

## 🔧 环境变量配置

### 必需的环境变量
```bash
FLASK_ENV=production          # 生产环境标识
SECRET_KEY=your-secret-key    # Flask密钥（必须更改）
PORT=8080                     # 端口号（平台自动设置）
```

### 可选的环境变量
```bash
LOG_LEVEL=INFO               # 日志级别
HOST=0.0.0.0                # 主机地址
OCR_TIMEOUT=30              # OCR处理超时时间
```

### 安全注意事项
- ⚠️ **必须更改SECRET_KEY**：使用强随机字符串
- 🔒 **不要在代码中硬编码密钥**
- 🛡️ **启用HTTPS**：大多数平台自动提供

## ✅ 部署后验证

### 功能测试清单
- [ ] 首页正常加载
- [ ] OCR图片上传和识别
- [ ] 表单自动填充
- [ ] 合同生成和下载
- [ ] 服务期限计算
- [ ] 费用计算功能
- [ ] 备忘录功能

### 性能检查
```bash
# 使用curl测试响应时间
curl -w "@curl-format.txt" -o /dev/null -s "https://your-app.railway.app"

# 创建curl-format.txt文件
echo "     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n" > curl-format.txt
```

## 🔍 常见问题排查

### 问题1：OCR功能不工作
**症状**：图片上传后无法识别文字
**解决方案**：
1. 检查Tesseract是否正确安装（查看aptfile）
2. 确认opencv-python-headless版本兼容
3. 检查应用日志中的错误信息

### 问题2：文件上传失败
**症状**：上传大文件时出现错误
**解决方案**：
1. 检查MAX_CONTENT_LENGTH配置
2. 确认平台的文件大小限制
3. 考虑使用云存储服务

### 问题3：应用启动失败
**症状**：部署后应用无法启动
**解决方案**：
1. 检查requirements.txt中的依赖版本
2. 确认Procfile配置正确
3. 查看平台的构建日志

### 问题4：中文字符显示异常
**症状**：OCR识别的中文显示乱码
**解决方案**：
1. 确认安装了中文语言包（tesseract-ocr-chi-sim）
2. 检查字符编码设置
3. 验证字体文件是否正确加载

## 📊 监控和维护

### 日志监控
- Railway：在项目面板查看实时日志
- Render：在服务详情页面查看日志
- Docker：使用 `docker logs container_name`

### 性能监控
建议集成以下监控服务：
- **Sentry**：错误追踪
- **New Relic**：性能监控
- **Uptime Robot**：可用性监控

### 定期维护
- 📅 每月检查依赖更新
- 🔄 定期备份重要数据
- 📈 监控资源使用情况
- 🔐 定期更新密钥和证书

## 🆘 获取帮助

如果遇到部署问题，可以：
1. 查看平台官方文档
2. 检查应用日志
3. 在GitHub Issues中提问
4. 联系技术支持

---

**祝您部署成功！** 🎉
