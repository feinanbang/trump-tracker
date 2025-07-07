import logging
import os
from datetime import datetime
import pytz
from typing import Dict, List

from config import LOG_LEVEL, LOG_FILE, TIMEZONE


def setup_logging():
    """设置日志配置"""
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库日志级别
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logging.info("日志系统初始化完成")


def get_current_et_time() -> datetime:
    """获取当前东部时间"""
    et_tz = pytz.timezone(TIMEZONE)
    return datetime.now(et_tz)


def format_et_date(date_str: str) -> str:
    """格式化东部时间日期"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y年%m月%d日')
    except ValueError:
        return date_str


def create_summary_report(posts: List[Dict]) -> str:
    """创建爬取结果摘要报告"""
    if not posts:
        return "没有爬取到新帖子"
    
    # 按日期分组
    posts_by_date = {}
    for post in posts:
        date = post.get('post_date', 'Unknown')
        if date not in posts_by_date:
            posts_by_date[date] = []
        posts_by_date[date].append(post)
    
    # 生成报告
    report_lines = [
        f"爬取摘要报告 - {get_current_et_time().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        f"总计爬取帖子数: {len(posts)}",
        f"涉及日期数: {len(posts_by_date)}",
        "",
        "按日期分布:"
    ]
    
    # 按日期排序
    sorted_dates = sorted(posts_by_date.keys(), reverse=True)
    
    for date in sorted_dates:
        date_posts = posts_by_date[date]
        total_likes = sum(post.get('likes_count', 0) for post in date_posts)
        total_reposts = sum(post.get('reposts_count', 0) for post in date_posts)
        total_comments = sum(post.get('comments_count', 0) for post in date_posts)
        
        report_lines.extend([
            f"  {format_et_date(date)}:",
            f"    帖子数: {len(date_posts)}",
            f"    总点赞数: {total_likes:,}",
            f"    总转发数: {total_reposts:,}",
            f"    总评论数: {total_comments:,}",
            ""
        ])
    
    return "\n".join(report_lines)


def validate_post_data(post_data: Dict) -> bool:
    """验证帖子数据完整性"""
    required_fields = [
        'post_id', 'content', 'post_date', 'post_time',
        'timestamp_utc', 'timestamp_et'
    ]
    
    for field in required_fields:
        if field not in post_data or not post_data[field]:
            return False
    
    return True


def clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = ' '.join(text.split())
    
    # 移除特殊字符（保留基本标点）
    # 这里可以根据需要调整清理规则
    
    return text.strip()


def get_file_size(file_path: str) -> str:
    """获取文件大小的可读格式"""
    if not os.path.exists(file_path):
        return "文件不存在"
    
    size_bytes = os.path.getsize(file_path)
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def check_system_requirements():
    """检查系统要求"""
    import sys
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        raise RuntimeError("需要Python 3.8或更高版本")
    
    # 检查必要的模块
    required_modules = {
        'selenium': 'selenium',
        'beautifulsoup4': 'bs4',
        'requests': 'requests',
        'apscheduler': 'apscheduler',
        'pytz': 'pytz',
        'lxml': 'lxml'
    }
    
    missing_modules = []
    for package_name, module_name in required_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(package_name)
    
    if missing_modules:
        raise RuntimeError(f"缺少必要模块: {', '.join(missing_modules)}")
    
    logging.info("系统要求检查通过") 