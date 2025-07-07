#!/usr/bin/env python3
"""
展示数据库中帖子的完整存储格式
"""

import json
from database import TrumpPostsDB

def show_data_format():
    """展示数据库中帖子的存储格式"""
    db = TrumpPostsDB()
    
    print("=" * 80)
    print("Trump Truth Social 帖子数据存储格式")
    print("=" * 80)
    
    # 获取最新的几个帖子作为示例
    dates = ['2025-07-07', '2025-07-06', '2025-07-05']
    
    sample_count = 0
    for date in dates:
        posts = db.get_posts_by_date(date)
        if posts and sample_count < 3:  # 只显示前3个帖子作为示例
            for post in posts[:2]:  # 每个日期最多显示2个
                sample_count += 1
                print(f"\n【示例帖子 {sample_count}】")
                print("-" * 60)
                
                # 显示所有字段
                for key, value in post.items():
                    if key == 'media_urls' and value:
                        try:
                            media_list = json.loads(value)
                            print(f"{key:20s}: {media_list}")
                        except:
                            print(f"{key:20s}: {value}")
                    elif isinstance(value, str) and len(value) > 100:
                        # 长文本截断显示
                        print(f"{key:20s}: {value[:100]}...")
                    else:
                        print(f"{key:20s}: {value}")
                
                if sample_count >= 3:
                    break
        
        if sample_count >= 3:
            break
    
    print("\n" + "=" * 80)
    print("数据库表结构说明")
    print("=" * 80)
    
    field_descriptions = {
        'id': '自增主键',
        'post_id': 'Truth Social帖子唯一ID',
        'content': '帖子文本内容',
        'post_date': '发帖日期 (YYYY-MM-DD)',
        'post_time': '发帖时间 (HH:MM:SS)',
        'timestamp_utc': 'UTC时间戳 (ISO格式)',
        'timestamp_et': '美国东部时间戳 (ISO格式)',
        'likes_count': '点赞数',
        'reposts_count': '转发数',
        'comments_count': '评论数',
        'media_urls': '媒体文件链接 (JSON数组)',
        'post_url': '帖子完整URL',
        'scraped_at': '爬取时间戳',
        'created_at': '数据库插入时间'
    }
    
    for field, description in field_descriptions.items():
        print(f"{field:20s}: {description}")
    
    # 数据库统计
    print("\n" + "=" * 80)
    print("数据库统计信息")
    print("=" * 80)
    
    total_posts = db.get_posts_count()
    print(f"总帖子数: {total_posts}")
    
    for date in ['2025-07-07', '2025-07-06', '2025-07-05', '2025-07-04', '2025-07-03']:
        posts = db.get_posts_by_date(date)
        if posts:
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_reposts = sum(post.get('reposts_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) for post in posts)
            
            print(f"{date}: {len(posts):2d}个帖子 | 赞:{total_likes:,} | 转:{total_reposts:,} | 评:{total_comments:,}")
    
    print("\n" + "=" * 80)
    print("存储文件信息")
    print("=" * 80)
    
    import os
    from utils import get_file_size
    
    db_file = "trump_posts.db"
    log_file = "trump_scraper.log"
    
    if os.path.exists(db_file):
        print(f"数据库文件: {db_file} ({get_file_size(db_file)})")
    
    if os.path.exists(log_file):
        print(f"日志文件: {log_file} ({get_file_size(log_file)})")
    
    print(f"数据库位置: {os.path.abspath(db_file)}")

if __name__ == "__main__":
    show_data_format() 