#!/usr/bin/env python3
"""
查看已生成的所有小结
"""

from database import TrumpPostsDB

def main():
    print("📋 Trump Truth Social 小结数据库")
    print("=" * 60)
    
    db = TrumpPostsDB()
    
    # 获取所有小结
    summaries = db.get_recent_summaries(20)  # 获取最近20条
    
    if not summaries:
        print("❌ 暂无小结数据")
        return
    
    print(f"📊 共找到 {len(summaries)} 条小结：")
    print()
    
    for i, summary in enumerate(summaries, 1):
        date = summary['summary_date']
        generated_by = summary['generated_by']
        post_count = summary['post_count']
        generated_at = summary['generated_at']
        
        print(f"{i}. 📅 {date}")
        print(f"   🤖 生成方式: {generated_by}")
        print(f"   📝 帖子数量: {post_count}")
        print(f"   ⏰ 生成时间: {generated_at}")
        
        # 直接显示小结内容
        print(f"   📄 小结内容:")
        print("   " + "-" * 50)
        # 缩进显示小结内容
        content_lines = summary['summary_content'].split('\n')
        for line in content_lines[:10]:  # 只显示前10行
            print(f"   {line}")
        
        if len(content_lines) > 10:
            print(f"   ... (还有{len(content_lines)-10}行，内容较长)")
        
        print("   " + "-" * 50)
        print()

if __name__ == "__main__":
    main() 