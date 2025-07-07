# 数据库配置
DATABASE_PATH = "trump_posts.db"

# 爬虫配置
TRUTH_SOCIAL_URL = "https://truthsocial.com/@realDonaldTrump"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 滚动配置 - 针对人性化匿名访问优化
MAX_SCROLL_ATTEMPTS = 30  # 减少滚动次数，专注质量
MAX_NO_NEW_POSTS = 8     # 增加连续无新帖子的容忍度
SCROLL_PAUSE_TIME = 4    # 增加等待时间，确保内容充分加载

# 调度配置
SCHEDULE_HOUR = 1  # 每小时运行一次
SCHEDULE_MINUTE = 0

# 时区配置
TIMEZONE = "US/Eastern"

# 浏览器选项 - 保留兼容性
BROWSER_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080"
]

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "trump_scraper.log"

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 10 