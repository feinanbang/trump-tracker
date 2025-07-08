#!/usr/bin/env python3
"""
Trump Truth Social 分析网站
Flask后端应用 - JSON数据版本
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import pytz
import json
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trump_tracker_2025'


def load_data():
    """从JSON文件加载数据"""
    try:
        data_file = 'data_exports/latest_data.json'
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回空数据结构
            return {
                'statistics': {
                    'total_posts': 0,
                    'total_days': 0,
                    'latest_post': None,
                    'daily_stats': []
                },
                'summaries': [],
                'recent_posts': [],
                'status': 'no_data'
            }
    except Exception as e:
        print(f"加载数据文件失败: {e}")
        return {
            'statistics': {
                'total_posts': 0,
                'total_days': 0,
                'latest_post': None,
                'daily_stats': []
            },
            'summaries': [],
            'recent_posts': [],
            'status': 'error'
        }


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


@app.route('/')
def index():
    """主页 - 显示最新分析和统计"""
    try:
        data = load_data()
        
        # 格式化统计数据
        stats = {
            'total_posts': data['statistics']['total_posts'],
            'total_summaries': len(data['summaries']),
            'coverage_days': data['statistics']['total_days']
        }
        
        # 格式化摘要数据，为模板兼容性调整格式
        recent_summaries = []
        for summary in data['summaries'][:7]:  # 最近7天
            recent_summaries.append({
                'date': summary['analysis_date'],
                'post_count': summary['post_count'],
                'has_summary': True,
                'summary': {
                    'summary_text': summary['summary_text'],
                    'key_topics': json.dumps(summary['key_topics'], ensure_ascii=False)
                }
            })
        
        return render_template('index.html', 
                             summaries=recent_summaries,
                             stats=stats)
    
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/daily/<date>')
def daily_analysis(date):
    """每日详细分析页面"""
    try:
        data = load_data()
        
        # 查找指定日期的摘要
        summary = None
        post_count = 0
        
        for s in data['summaries']:
            if s['analysis_date'] == date:
                summary = {
                    'summary_text': s['summary_text'],
                    'key_topics': json.dumps(s['key_topics'], ensure_ascii=False)
                }
                post_count = s['post_count']
                break
        
        if not summary:
            return "该日期没有分析数据", 404
        
        # 获取该日期的帖子（从recent_posts中筛选）
        posts = []
        for post in data['recent_posts']:
            if post['created_at'].startswith(date):
                posts.append({
                    'content': post['content'],
                    'post_time': post['created_at'].split(' ')[1] if ' ' in post['created_at'] else '',
                    'likes_count': post.get('engagement_score', 0),
                    'reposts_count': 0,
                    'comments_count': 0
                })
        
        # 计算统计数据
        stats = {
            'post_count': post_count,
            'total_likes': sum(post.get('likes_count', 0) for post in posts),
            'total_reposts': 0,
            'total_comments': 0
        }
        
        return render_template('daily.html',
                             date=date,
                             posts=posts,
                             summary=summary,
                             stats=stats)
    
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/api/posts/<date>')
def api_posts(date):
    """API接口 - 获取指定日期的帖子数据"""
    try:
        data = load_data()
        
        # 获取该日期的帖子
        posts = []
        for post in data['recent_posts']:
            if post['created_at'].startswith(date):
                posts.append(post)
        
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
        data = load_data()
        
        # 查找指定日期的摘要
        summary = None
        for s in data['summaries']:
            if s['analysis_date'] == date:
                summary = s
                break
        
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
        data = load_data()
        
        return jsonify({
            'success': True,
            'total_posts': data['statistics']['total_posts'],
            'total_summaries': len(data['summaries']),
            'recent_data': data['statistics']['daily_stats']
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
        data = load_data()
        
        # 获取所有有分析的日期
        all_dates = []
        for summary in data['summaries']:
            all_dates.append({
                'date': summary['analysis_date'],
                'post_count': summary['post_count'],
                'has_summary': True
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