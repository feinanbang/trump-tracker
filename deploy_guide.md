# 🚀 Trump Tracker 部署指南

## 🎯 域名：trump-tracker.online

本指南将帮助您将Trump Truth Social分析网站部署到您的域名 `trump-tracker.online`。

## 📋 部署选项

### ⭐ 推荐方案：Vercel（免费）

**优势：**
- ✅ 完全免费
- ✅ 自动HTTPS证书
- ✅ 全球CDN加速
- ✅ 自动部署
- ✅ 支持自定义域名

### 🚀 Vercel部署步骤

#### 第1步：创建GitHub仓库

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: Trump Truth Social Tracker"

# 创建GitHub仓库（在GitHub网站上创建）
# 然后连接本地仓库
git remote add origin https://github.com/您的用户名/trump-tracker.git
git branch -M main
git push -u origin main
```

#### 第2步：Vercel部署

1. 访问 [vercel.com](https://vercel.com)
2. 使用GitHub账号登录
3. 点击 "New Project"
4. 选择您的 `trump-tracker` 仓库
5. 配置项目：
   - **Framework Preset**: Other
   - **Build Command**: 留空
   - **Output Directory**: 留空
   - **Install Command**: `pip install -r requirements_web.txt`

#### 第3步：配置自定义域名

1. 在Vercel项目设置中找到 "Domains"
2. 添加域名：`trump-tracker.online`
3. Vercel会提供DNS配置信息

#### 第4步：配置DNS解析

在您的域名注册商处配置以下DNS记录：

```
类型    名称    值
A       @       76.76.19.61
CNAME   www     cname.vercel-dns.com
```

> **注意**：具体IP地址和CNAME值请以Vercel提供的为准

#### 第5步：等待生效

- DNS传播通常需要几分钟到几小时
- HTTPS证书会自动配置
- 配置完成后访问：https://trump-tracker.online

## 📊 数据库配置

### 生产环境数据库

由于Vercel是无服务器环境，需要配置在线数据库：

#### 选项1：SQLite + GitHub（推荐用于演示）
- 将数据库文件上传到GitHub
- 定期更新（需要手动操作）

#### 选项2：PostgreSQL（推荐用于生产）
- 使用免费的 [Supabase](https://supabase.com)
- 或者 [PlanetScale](https://planetscale.com)

### 数据同步

```bash
# 将本地数据库复制到项目目录
cp data/trump_posts.db ./trump_posts.db

# 提交到GitHub
git add trump_posts.db
git commit -m "Update database"
git push
```

## 🔄 自动更新机制

### 当前方案：半手动更新
1. 本地爬虫运行，更新数据库
2. 将更新的数据库推送到GitHub
3. Vercel自动重新部署

### 高级方案：自动化CI/CD
- 使用GitHub Actions
- 定时运行爬虫
- 自动更新数据库
- 自动部署

## 🛠️ 故障排除

### 常见问题

1. **网站显示空白**
   - 检查数据库文件是否存在
   - 查看Vercel部署日志

2. **域名无法访问**
   - 确认DNS配置正确
   - 等待DNS传播（最多24小时）

3. **HTTPS证书问题**
   - Vercel会自动配置
   - 如有问题，检查域名验证

### 调试方法

```bash
# 本地测试
python web_app.py

# 检查数据库
python -c "from database import TrumpPostsDB; db = TrumpPostsDB(); print(db.get_stats())"
```

## 🎯 访问地址

部署完成后，您的网站将可以通过以下地址访问：

- **主域名**：https://trump-tracker.online
- **www域名**：https://www.trump-tracker.online
- **Vercel域名**：https://trump-tracker.vercel.app（备用）

## 📈 后续优化

1. **性能优化**
   - 添加缓存机制
   - 优化数据库查询
   - 压缩静态资源

2. **功能扩展**
   - 添加搜索功能
   - 数据可视化图表
   - RSS订阅功能

3. **SEO优化**
   - 添加meta标签
   - 生成sitemap
   - 优化页面标题

恭喜！🎉 您的Trump Truth Social分析网站即将上线！ 