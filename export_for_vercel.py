#!/usr/bin/env python3
"""
为Vercel部署导出数据库数据到JSON
"""

import sqlite3
import json
from datetime import datetime

def export_database_to_json():
    """导出数据库到JSON文件"""
    try:
        # 连接数据库
        conn = sqlite3.connect('trump_posts.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取所有小结
        cursor.execute('''
            SELECT summary_date, summary_content, post_count, generated_at, generated_by 
            FROM daily_summaries 
            ORDER BY summary_date DESC
        ''')
        
        summaries = []
        for row in cursor.fetchall():
            summaries.append({
                'analysis_date': row['summary_date'],
                'post_count': row['post_count'],
                'summary_text': row['summary_content'],
                'generated_at': row['generated_at'],
                'generated_by': row['generated_by']
            })
        
        # 获取统计数据
        cursor.execute('SELECT COUNT(*) as total FROM trump_posts')
        total_posts = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT DATE(timestamp_et) as date, COUNT(*) as post_count 
            FROM trump_posts 
            GROUP BY DATE(timestamp_et) 
            ORDER BY date DESC 
            LIMIT 7
        ''')
        
        daily_stats = []
        for row in cursor.fetchall():
            daily_stats.append({
                'date': row['date'], 
                'post_count': row['post_count']
            })
        
        # 获取一些最新帖子
        cursor.execute('''
            SELECT post_id, content, timestamp_et, likes_count 
            FROM trump_posts 
            ORDER BY timestamp_et DESC 
            LIMIT 10
        ''')
        
        recent_posts = []
        for row in cursor.fetchall():
            recent_posts.append({
                'post_id': row['post_id'],
                'content': row['content'],
                'created_at': row['timestamp_et'],
                'engagement_score': row['likes_count']
            })
        
        conn.close()
        
        # 创建导出数据
        export_data = {
            'statistics': {
                'total_posts': total_posts,
                'total_days': len(daily_stats),
                'daily_stats': daily_stats
            },
            'summaries': summaries,
            'recent_posts': recent_posts,
            'export_time': datetime.now().isoformat(),
            'status': 'exported_data'
        }
        
        # 保存为JSON
        with open('latest_data.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 导出完成！")
        print(f"📊 包含 {len(summaries)} 条Claude分析")
        print(f"📱 包含 {total_posts} 条帖子数据")
        print(f"💾 文件已保存为 latest_data.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

if __name__ == "__main__":
    export_database_to_json() 