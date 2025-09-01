# 🚀 GitHub推送指南

## 当前状态
- ✅ 代码已准备完毕
- ✅ GitHub仓库已创建：https://github.com/Esther1023/businesstool
- ⚠️ 需要解决权限问题

## 🔑 解决方案：使用个人访问令牌

### 步骤1：创建GitHub个人访问令牌

1. **登录GitHub**：访问 https://github.com/login
2. **进入设置**：点击右上角头像 → Settings
3. **开发者设置**：左侧菜单 → Developer settings
4. **个人令牌**：Personal access tokens → Tokens (classic)
5. **生成新令牌**：Generate new token (classic)
6. **配置令牌**：
   ```
   Note: OCR System Deployment
   Expiration: 90 days
   Scopes: ✅ repo (完整仓库访问)
   ```
7. **生成并复制**：点击Generate token，立即复制令牌

### 步骤2：推送代码

在终端中执行以下命令：

```bash
# 1. 确认远程仓库
git remote -v

# 2. 推送到GitHub（会要求输入用户名和密码）
git push github master
```

**重要**：当提示输入密码时，粘贴您刚才复制的个人访问令牌！

### 步骤3：验证推送成功

推送成功后，访问您的GitHub仓库确认代码已上传：
https://github.com/Esther1023/businesstool

## 🔄 替代方案：使用SSH

如果您配置了SSH密钥，也可以使用SSH方式：

```bash
# 更改为SSH URL
git remote set-url github git@github.com:Esther1023/businesstool.git

# 推送
git push github master
```

## 📋 推送后的下一步

1. **验证代码**：确认所有文件都已上传到GitHub
2. **部署到Railway**：
   - 访问 https://railway.app
   - 连接GitHub仓库
   - 自动部署
3. **设置环境变量**：
   ```
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key
   ```

## 🆘 如果仍有问题

### 常见错误和解决方案

1. **403 Permission denied**
   - 确认使用正确的GitHub用户名
   - 使用个人访问令牌而不是密码

2. **Repository not found**
   - 确认仓库URL正确
   - 确认仓库是public或您有访问权限

3. **Authentication failed**
   - 重新生成个人访问令牌
   - 确认令牌有repo权限

### 手动上传方案

如果Git推送仍有问题，您可以：

1. 将所有文件打包成ZIP
2. 在GitHub仓库页面点击"Upload files"
3. 拖拽ZIP文件上传
4. 提交更改

## 📞 获取帮助

- GitHub文档：https://docs.github.com/en/authentication
- 个人访问令牌指南：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

**准备好了吗？让我们开始推送代码！** 🚀
