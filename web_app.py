#!/usr/bin/env python3
"""
Trump Truth Social 分析网站
Flask后端应用
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import pytz
import json
import re
from database import TrumpPostsDB
from config import TIMEZONE

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trump_tracker_2025'


def format_analysis(content):
    """格式化Claude分析内容为HTML"""
    if not content:
        return ""
    
    # 先处理HTML转义
    content = content.replace('<br>', '\n').replace('<br/>', '\n')
    
    # 分割成段落
    paragraphs = content.split('\n\n')
    formatted_html = []
    
    for para in paragraphs:
        if not para.strip():
            continue
            
        # 处理标题
        if para.startswith('##'):
            title = para.replace('##', '').strip()
            formatted_html.append(f'<h2>{title}</h2>')
        elif para.startswith('**核心观点**'):
            content_part = para.replace('**核心观点**:', '').strip()
            formatted_html.append(f'''
                <div class="analysis-section core-points">
                    <h3>🎯 核心观点</h3>
                    <p>{content_part}</p>
                </div>
            ''')
        elif para.startswith('**主要内容**'):
            content_part = para.replace('**主要内容**:', '').strip()
            # 处理列表项
            if '- ' in content_part:
                items = content_part.split('- ')
                list_html = '<ul>'
                for item in items:
                    if item.strip():
                        list_html += f'<li>{item.strip()}</li>'
                list_html += '</ul>'
                formatted_html.append(f'''
                    <div class="analysis-section main-content">
                        <h3>📋 主要内容</h3>
                        {list_html}
                    </div>
                ''')
            else:
                formatted_html.append(f'''
                    <div class="analysis-section main-content">
                        <h3>📋 主要内容</h3>
                        <p>{content_part}</p>
                    </div>
                ''')
        elif para.startswith('**语调特点**'):
            content_part = para.replace('**语调特点**:', '').strip()
            formatted_html.append(f'''
                <div class="analysis-section tone-analysis">
                    <h3>🎭 语调特点</h3>
                    <p>{content_part}</p>
                </div>
            ''')
        elif para.startswith('**值得关注**'):
            content_part = para.replace('**值得关注**:', '').strip()
            formatted_html.append(f'''
                <div class="analysis-section notable-points">
                    <h3>⚠️ 值得关注</h3>
                    <p>{content_part}</p>
                </div>
            ''')
        else:
            # 处理加粗文本
            para = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', para)
            # 处理换行
            para = para.replace('\n', '<br>')
            if para.strip():
                formatted_html.append(f'<p>{para}</p>')
    
    return ''.join(formatted_html)


# 注册模板函数
app.jinja_env.globals['format_analysis'] = format_analysis

# 时区设置
et_tz = pytz.timezone(TIMEZONE)

# 初始化数据库（安全模式）
def get_db():
    """安全获取数据库连接"""
    try:
        return TrumpPostsDB()
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


@app.route('/')
def index():
    """主页 - 显示最新分析和统计"""
    try:
        db = get_db()
        if not db:
            # 数据库不可用时显示示例页面
            return render_template('index.html', 
                                 summaries=[],
                                 stats={'total_posts': 0, 'total_summaries': 0, 'coverage_days': 0})
        
        # 获取最近7天的数据
        recent_summaries = []
        today = datetime.now(et_tz)
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            posts = db.get_posts_by_date(date)
            summary = db.get_summary_by_date(date)
            
            if posts:
                recent_summaries.append({
                    'date': date,
                    'post_count': len(posts),
                    'has_summary': bool(summary),
                    'summary': summary
                })
        
        # 获取总体统计
        total_posts = db.get_posts_count()
        total_summaries = db.get_summaries_count()
        
        stats = {
            'total_posts': total_posts,
            'total_summaries': total_summaries,
            'coverage_days': len([s for s in recent_summaries if s['post_count'] > 0])
        }
        
        return render_template('index.html', 
                             summaries=recent_summaries,
                             stats=stats)
    
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/daily/<date>')
def daily_analysis(date):
    """每日详细分析页面"""
    try:
        db = get_db()
        if not db:
            return "数据库不可用", 500
            
        posts = db.get_posts_by_date(date)
        summary = db.get_summary_by_date(date)
        
        if not posts:
            return "该日期没有数据", 404
        
        # 按时间排序帖子
        sorted_posts = sorted(posts, key=lambda x: x.get('post_time', ''))
        
        # 计算统计数据
        total_likes = sum(post.get('likes_count', 0) for post in posts)
        total_reposts = sum(post.get('reposts_count', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        
        stats = {
            'post_count': len(posts),
            'total_likes': total_likes,
            'total_reposts': total_reposts,
            'total_comments': total_comments
        }
        
        return render_template('daily.html',
                             date=date,
                             posts=sorted_posts,
                             summary=summary,
                             stats=stats)
    
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/api/posts/<date>')
def api_posts(date):
    """API接口 - 获取指定日期的帖子数据"""
    try:
        posts = db.get_posts_by_date(date)
        return jsonify({
            'success': True,
            'date': date,
            'count': len(posts),
            'posts': posts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/summary/<date>')
def api_summary(date):
    """API接口 - 获取指定日期的分析小结"""
    try:
        summary = db.get_summary_by_date(date)
        return jsonify({
            'success': True,
            'date': date,
            'has_summary': bool(summary),
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def api_stats():
    """API接口 - 获取总体统计数据"""
    try:
        total_posts = db.get_posts_count()
        total_summaries = db.get_summaries_count()
        
        # 最近7天数据
        recent_data = []
        today = datetime.now(et_tz)
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            posts = db.get_posts_by_date(date)
            recent_data.append({
                'date': date,
                'post_count': len(posts)
            })
        
        return jsonify({
            'success': True,
            'total_posts': total_posts,
            'total_summaries': total_summaries,
            'recent_data': recent_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')


@app.route('/archive')
def archive():
    """历史归档页面"""
    try:
        # 获取所有有数据的日期
        all_dates = []
        today = datetime.now(et_tz)
        
        # 检查最近30天
        for i in range(30):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            posts = db.get_posts_by_date(date)
            summary = db.get_summary_by_date(date)
            
            if posts:
                all_dates.append({
                    'date': date,
                    'post_count': len(posts),
                    'has_summary': bool(summary)
                })
        
        return render_template('archive.html', dates=all_dates)
    
    except Exception as e:
        return f"Error: {e}", 500


# Vercel entry point
app_instance = app

if __name__ == '__main__':
    print("🚀 启动Trump Truth Social分析网站...")
    print("📊 访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 