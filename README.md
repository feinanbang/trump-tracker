# Trump Truth Social 爬虫程序

一个专业的Trump Truth Social帖子爬虫系统，能够自动抓取、存储和分析Trump在Truth Social上的所有帖子。

## 功能特点

✅ **自动化爬取**: 每小时自动运行，不遗漏任何内容  
✅ **无头浏览器**: 后台运行，不占用屏幕和浏览器  
✅ **按天存储**: 按美国东部时区的日期规范存储数据  
✅ **历史数据**: 支持批量爬取过去任意天数的历史帖子  
✅ **数据完整**: 包含帖子内容、时间、互动数据、媒体链接等  
✅ **AI智能小结**: 使用Hugging Face API自动生成每日内容小结  
✅ **错误处理**: 完整的重试机制和日志记录  
✅ **数据分析**: 内置报告生成和统计功能  

## 系统要求

- Python 3.8 或更高版本
- Windows 10/11 (已针对Windows优化)
- 至少 2GB 可用内存
- 稳定的网络连接

## 快速开始

### 方法1: 使用批处理文件 (推荐)

1. 双击运行 `run_scraper.bat`
2. 程序会自动安装依赖并显示菜单
3. 选择相应的操作选项

### 方法2: 手动安装

1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
# 启动定时爬虫
python main.py

# 测试运行
python main.py --test

# 爬取历史数据
python main.py --historical 30

# 查看数据库状态
python main.py --status

# 生成AI小结
python main.py --summary 2025-07-07
```

## 使用说明

### 启动定时爬虫
```bash
python main.py
```
- 每小时自动运行一次
- 首次运行会自动爬取过去30天的历史数据
- 按 Ctrl+C 停止

### 测试运行
```bash
python main.py --test
```
- 运行一次爬取测试
- 查看程序是否正常工作

### 爬取历史数据
```bash
python main.py --historical 30
```
- 爬取过去30天的所有帖子
- 可以指定任意天数

### 查看数据状态
```bash
python main.py --status
```
- 显示数据库统计信息
- 查看最近7天的数据分布

### 生成AI智能小结
```bash
python main.py --summary 2025-07-07
```
- 为指定日期生成智能小结
- 需要先配置Hugging Face API (免费)
- 小结包含主要观点和原文链接

## 数据存储

### 数据库结构
程序使用SQLite数据库存储数据，包含两个主要表：

**帖子表 (trump_posts)**:
- `post_id`: 帖子唯一标识符
- `content`: 帖子文本内容
- `post_date`: 发帖日期 (美国东部时区)
- `post_time`: 发帖时间
- `timestamp_utc`: UTC时间戳
- `timestamp_et`: 东部时区时间戳
- `likes_count`: 点赞数
- `reposts_count`: 转发数
- `comments_count`: 评论数
- `media_urls`: 媒体文件链接 (JSON格式)
- `post_url`: 帖子链接
- `scraped_at`: 爬取时间

**小结表 (daily_summaries)**:
- `summary_date`: 小结日期
- `summary_content`: AI生成的小结内容
- `post_count`: 当日帖子数量
- `total_likes`: 当日总点赞数
- `total_reposts`: 当日总转发数
- `total_comments`: 当日总评论数
- `generated_by`: 生成方式 (AI/系统)
- `generated_at`: 生成时间

### 数据文件
- `trump_posts.db`: 主数据库文件
- `trump_scraper.log`: 运行日志文件

## 配置说明

### 基础配置
可以通过修改 `config.py` 文件来调整程序行为：

```python
# 调度配置
SCHEDULE_MINUTE = 0  # 每小时的第几分钟运行

# 爬虫配置
SCROLL_PAUSE_TIME = 2  # 页面滚动等待时间
MAX_SCROLL_ATTEMPTS = 10  # 最大滚动次数

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 5  # 重试间隔秒数
```

### AI小结配置

1. **获取免费API**:
   - 访问 [Hugging Face](https://huggingface.co/)
   - 注册免费账号
   - 生成Read权限的API Token

2. **配置环境变量**:
   - 方法1: 运行 `config_hf.example.bat` 自动配置
   - 方法2: 手动设置环境变量 `HUGGINGFACE_API_TOKEN`

3. **测试AI功能**:
   ```bash
   python test_summary.py
   ```

## 运行监控

### 日志文件
程序会自动生成详细的运行日志：
- 控制台输出：实时显示运行状态
- 日志文件：`trump_scraper.log` 保存所有运行记录

### 状态检查
定期运行状态检查命令：
```bash
python main.py --status
```

## 注意事项

⚠️ **合规使用**: 请遵守Truth Social的使用条款和robots.txt规则  
⚠️ **频率控制**: 程序已内置合理的请求频率限制  
⚠️ **网络稳定**: 确保网络连接稳定，避免数据丢失  
⚠️ **存储空间**: 长期运行需要足够的磁盘空间  

## 故障排除

### 常见问题

1. **Chrome浏览器问题**
   - 程序会自动下载ChromeDriver
   - 确保系统已安装Chrome浏览器

2. **网络连接问题**
   - 检查网络连接是否稳定
   - 程序会自动重试失败的请求

3. **权限问题**
   - 确保程序有写入文件的权限
   - Windows可能需要管理员权限

4. **Python版本问题**
   - 确保使用Python 3.8或更高版本
   - 运行 `python --version` 检查版本

### 日志分析
查看 `trump_scraper.log` 文件获取详细的错误信息。

## 项目结构

```
trump_tracker/
├── main.py                  # 主程序入口
├── config.py                # 配置文件
├── database.py              # 数据库管理
├── scraper.py               # 爬虫核心逻辑
├── scheduler.py             # 任务调度器
├── summarizer.py            # AI小结生成器
├── utils.py                 # 工具函数
├── requirements.txt         # 依赖包列表
├── run_scraper.bat          # Windows启动脚本
├── config_hf.example.bat    # AI配置助手
├── test_summary.py          # AI功能测试脚本
├── README.md               # 项目说明
├── trump_posts.db          # 数据库文件 (运行后生成)
└── trump_scraper.log       # 日志文件 (运行后生成)
```

## 开发者信息

这是一个专业的数据采集工具，遵循最佳实践：
- 完整的错误处理和重试机制
- 结构化的代码组织
- 详细的日志记录
- 灵活的配置选项
- 用户友好的界面

如有问题或建议，请查看日志文件或联系开发者。 