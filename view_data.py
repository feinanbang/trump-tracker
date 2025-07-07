#!/usr/bin/env python3
"""
查看数据库中爬取的帖子数据
"""

from database import TrumpPostsDB

def main():
    db = TrumpPostsDB()
    
    print("=== Trump Truth Social 爬取数据总览 ===")
    print()
    
    # 获取所有帖子
    dates = ['2025-07-07', '2025-07-06', '2025-07-05', '2025-07-04', '2025-07-03', '2025-07-02', '2025-07-01']
    
    total_posts = 0
    
    for date in dates:
        posts = db.get_posts_by_date(date)
        if posts:
            total_posts += len(posts)
            print(f"【{date}】({len(posts)}个帖子):")
            
            for i, post in enumerate(posts, 1):
                content = post['content']
                if len(content) > 100:
                    content = content[:100] + "..."
                
                print(f"  {i}. {post['post_time']} - {content}")
            print()
    
    if total_posts == 0:
        print("没有找到帖子数据")
    else:
        print(f"总计: {total_posts} 个帖子")

if __name__ == "__main__":
    main() 