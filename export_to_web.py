#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据库内容到Web应用可读的JSON格式
Export database content to JSON format for web application
"""

import sqlite3
import json
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_to_database():
    """连接到数据库"""
    try:
        conn = sqlite3.connect('data/trump_posts.db')
        conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return None


def get_daily_statistics(conn):
    """获取每日统计数据"""
    try:
        cursor = conn.cursor()
        
        # 获取每日帖子数量
        query = """
        SELECT DATE(created_at) as date, COUNT(*) as post_count
        FROM posts
        WHERE created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """
        cursor.execute(query)
        daily_stats = [dict(row) for row in cursor.fetchall()]
        
        # 获取总体统计
        cursor.execute("SELECT COUNT(*) as total_posts FROM posts")
        total_posts = cursor.fetchone()['total_posts']
        
        cursor.execute("SELECT COUNT(DISTINCT DATE(created_at)) as total_days FROM posts")
        total_days = cursor.fetchone()['total_days']
        
        # 获取最新帖子时间
        cursor.execute("SELECT MAX(created_at) as latest_post FROM posts")
        latest_post = cursor.fetchone()['latest_post']
        
        return {
            'total_posts': total_posts,
            'total_days': total_days,
            'latest_post': latest_post,
            'daily_stats': daily_stats
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return None

def get_claude_summaries(conn):
    """获取Claude分析摘要"""
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT analysis_date, summary_text, post_count, key_topics
        FROM claude_summaries 
        ORDER BY analysis_date DESC
        """
        cursor.execute(query)
        summaries = []
        
        for row in cursor.fetchall():
            summary_data = dict(row)
            # 解析key_topics JSON
            if summary_data['key_topics']:
                try:
                    summary_data['key_topics'] = json.loads(summary_data['key_topics'])
                except:
                    summary_data['key_topics'] = []
            else:
                summary_data['key_topics'] = []
            
            summaries.append(summary_data)
        
        return summaries
    except Exception as e:
        logger.error(f"获取Claude摘要失败: {e}")
        return []

def get_recent_posts(conn, days=7):
    """获取最近几天的帖子"""
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT post_id, content, created_at, engagement_score
        FROM posts 
        WHERE created_at >= date('now', '-{} days')
        ORDER BY created_at DESC
        LIMIT 50
        """.format(days)
        
        cursor.execute(query)
        posts = [dict(row) for row in cursor.fetchall()]
        
        return posts
    except Exception as e:
        logger.error(f"获取最近帖子失败: {e}")
        return []

def export_to_json():
    """导出所有数据到JSON文件"""
    try:
        # 确保目录存在
        os.makedirs('data_exports', exist_ok=True)
        
        # 连接数据库
        conn = connect_to_database()
        if not conn:
            logger.error("无法连接到数据库")
            return False
        
        # 获取数据
        logger.info("正在获取统计数据...")
        statistics = get_daily_statistics(conn)
        
        logger.info("正在获取Claude分析摘要...")
        summaries = get_claude_summaries(conn)
        
        logger.info("正在获取最近帖子...")
        recent_posts = get_recent_posts(conn)
        
        # 组装数据
        export_data = {
            'export_time': datetime.now().isoformat(),
            'statistics': statistics or {
                'total_posts': 0,
                'total_days': 0,
                'latest_post': None,
                'daily_stats': []
            },
            'summaries': summaries,
            'recent_posts': recent_posts,
            'status': 'success'
        }
        
        # 导出主要数据文件
        main_file = 'data_exports/latest_data.json'
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        # 导出带时间戳的备份文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'data_exports/backup_{timestamp}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        conn.close()
        
        logger.info(f"数据导出成功:")
        logger.info(f"- 主文件: {main_file}")
        logger.info(f"- 备份文件: {backup_file}")
        logger.info(f"- 总帖子数: {export_data['statistics']['total_posts']}")
        logger.info(f"- Claude分析数: {len(summaries)}")
        logger.info(f"- 最近帖子数: {len(recent_posts)}")
        
        return True
        
    except Exception as e:
        logger.error(f"导出过程失败: {e}")
        return False

def create_sample_data():
    """如果数据库为空，创建示例数据"""
    try:
        # 基于我们已知的分析创建示例数据
        sample_data = {
            'export_time': datetime.now().isoformat(),
            'statistics': {
                'total_posts': 60,
                'total_days': 4,
                'latest_post': '2025-07-07 18:30:00',
                'daily_stats': [
                    {'date': '2025-07-07', 'post_count': 5},
                    {'date': '2025-07-06', 'post_count': 8},
                    {'date': '2025-07-05', 'post_count': 14},
                    {'date': '2025-07-04', 'post_count': 33}
                ]
            },
            'summaries': [
                {
                    'analysis_date': '2025-07-07',
                    'post_count': 5,
                    'summary_text': '今日Trump继续推进REMIGRATION政策讨论，强调边境安全与移民政策的重要性。同时回应了媒体对其政策的质疑，展现出坚定的政策立场。',
                    'key_topics': ['REMIGRATION', '边境安全', '媒体回应', '政策坚持']
                },
                {
                    'analysis_date': '2025-07-06',
                    'post_count': 8,
                    'summary_text': 'Trump正式宣布"REMIGRATION"政策概念，这是一个重大的移民政策转向。帖子显示了对现有移民体系的根本性重新思考，强调美国优先和边境控制的重要性。',
                    'key_topics': ['REMIGRATION政策', '移民改革', '美国优先', '边境控制']
                },
                {
                    'analysis_date': '2025-07-05',
                    'post_count': 14,
                    'summary_text': '独立日当天，Trump发布了庆祝美国独立的帖子，同时关注德州的洪灾情况。展现了作为领导者对国家庆典和自然灾害的双重关注，体现了政治责任感。',
                    'key_topics': ['独立日庆祝', '德州洪灾', '领导力展现', '国家责任']
                },
                {
                    'analysis_date': '2025-07-04',
                    'post_count': 33,
                    'summary_text': 'Trump庆祝"ONE BIG BEAUTIFUL BILL ACT"的重大胜利，这是一项重要的立法成就。通过多条帖子表达了对这一政策胜利的喜悦，并感谢了支持者们的努力。',
                    'key_topics': ['立法胜利', 'ONE BIG BEAUTIFUL BILL', '政策成就', '支持者感谢']
                }
            ],
            'recent_posts': [
                {
                    'post_id': 'sample_001',
                    'content': 'The REMIGRATION policy is working beautifully! America First means America First, and we are taking back control of our borders like never before!',
                    'created_at': '2025-07-07 18:30:00',
                    'engagement_score': 95
                },
                {
                    'post_id': 'sample_002', 
                    'content': 'Fake News Media doesn\'t want to report on the tremendous success of our border policies. They hate success, they hate America First!',
                    'created_at': '2025-07-07 16:45:00',
                    'engagement_score': 88
                }
            ],
            'status': 'sample_data'
        }
        
        # 确保目录存在
        os.makedirs('data_exports', exist_ok=True)
        
        # 保存示例数据
        with open('data_exports/latest_data.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        logger.info("已创建示例数据文件")
        return True
        
    except Exception as e:
        logger.error(f"创建示例数据失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始数据导出...")
    
    # 检查数据库是否存在
    if os.path.exists('data/trump_posts.db'):
        success = export_to_json()
        if not success:
            logger.warning("数据库导出失败，创建示例数据...")
            create_sample_data()
    else:
        logger.warning("数据库文件不存在，创建示例数据...")
        create_sample_data()
    
    logger.info("数据导出完成!") 