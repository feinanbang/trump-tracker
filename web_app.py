#!/usr/bin/env python3
"""
Trump Truth Social 分析网站
Flask后端应用 - 数据库优先，硬编码备用
"""

from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pytz
import json
import re
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trump_tracker_2025'

# 数据库配置
DATABASE_PATH = "trump_posts.db"
TIMEZONE = "US/Eastern"


def get_db_connection():
    """获取数据库连接"""
    try:
        if os.path.exists(DATABASE_PATH):
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            print(f"数据库文件不存在: {DATABASE_PATH}")
            return None
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def get_real_summaries_from_db():
    """从数据库获取真实的Claude分析"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
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
                'key_topics': [],  # 简化处理
                'generated_at': row['generated_at'],
                'generated_by': row['generated_by']
            })
        
        conn.close()
        print(f"✅ 从数据库成功加载 {len(summaries)} 条分析")
        return summaries
        
    except Exception as e:
        print(f"❌ 从数据库加载分析失败: {e}")
        return []


def get_real_posts_from_db():
    """从数据库获取真实的帖子数据"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT post_id, content, timestamp_et, likes_count, reposts_count, comments_count
            FROM trump_posts 
            ORDER BY timestamp_et DESC
            LIMIT 50
        ''')
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'post_id': row['post_id'],
                'content': row['content'],
                'created_at': row['timestamp_et'],
                'engagement_score': row['likes_count']
            })
        
        conn.close()
        print(f"✅ 从数据库成功加载 {len(posts)} 条帖子")
        return posts
        
    except Exception as e:
        print(f"❌ 从数据库加载帖子失败: {e}")
        return []


def get_real_stats_from_db():
    """从数据库获取真实的统计数据"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # 获取总帖子数
        cursor.execute('SELECT COUNT(*) FROM trump_posts')
        total_posts = cursor.fetchone()[0]
        
        # 获取总分析数
        cursor.execute('SELECT COUNT(*) FROM daily_summaries')
        total_summaries = cursor.fetchone()[0]
        
        # 获取最新帖子时间
        cursor.execute('SELECT MAX(timestamp_et) FROM trump_posts')
        latest_post = cursor.fetchone()[0]
        
        # 获取每日统计
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
        
        conn.close()
        
        return {
            'total_posts': total_posts,
            'total_days': len(daily_stats),
            'latest_post': latest_post,
            'daily_stats': daily_stats
        }
        
    except Exception as e:
        print(f"❌ 从数据库加载统计失败: {e}")
        return None


def get_fallback_data():
    """备用硬编码数据"""
    return {
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
                'analysis_date': '2025-07-06',
                'post_count': 8,
                'summary_text': """## 2025-07-06 Trump Truth Social 动态深度分析

**核心观点**: 特朗普总统首次在Truth Social正式宣布"REMIGRATION"(再移民)作为其政府政策，并庆祝德州洪灾联邦响应的成效，展现其移民强硬立场与灾难领导力的双重形象。

**主要内容**:
- 大力宣传"Operation Apex Hammer"行动成果，该行动在新泽西州逮捕了264名逃犯，包括17名杀人犯、95名帮派成员，其中多人为非法移民
- 首次在Truth Social正式使用"REMIGRATION"一词描述移民政策，该词汇在欧洲被极右翼团体用来描述大规模驱逐非白人移民的种族清洗政策
- 国务院已计划创建"再移民办公室"，将难民援助资源转向驱逐移民，目标是每日逮捕3000名移民
- 宣布为德州克尔县签署重大灾难声明，称海岸警卫队和州应急人员已拯救超过850人生命
- 强调"ONE BIG BEAUTIFUL BILL ACT"将提供ICE所需的全部资金和资源来执行"历史上最大规模的驱逐行动"

**语调特点**: 表现出强烈的民族主义色彩和对移民问题的零容忍态度，同时展现出对灾难响应的领导力和人道主义关怀的平衡

**值得关注**: "REMIGRATION"概念的首次正式提出标志着美国移民政策可能的根本性转向，这一词汇的使用在国际上具有极大争议性""",
                'key_topics': ['REMIGRATION政策', '移民执法', '德州洪灾', 'ICE资金', '边境安全']
            },
            {
                'analysis_date': '2025-07-05',
                'post_count': 14,
                'summary_text': """## 2025-07-05 Trump Truth Social 动态深度分析

**核心观点**: 特朗普总统在7月4日白宫军人家庭野餐会上签署"ONE BIG BEAUTIFUL BILL ACT"成为法律，并在德州发生史上最严重洪灾后迅速做出联邦灾难响应。

**主要内容**:
- 在白宫南草坪举行的军人家庭野餐会上正式签署"ONE BIG BEAUTIFUL BILL ACT"，仪式包括B-2隐形轰炸机和F-35、F-22战斗机飞越表演，这些正是参与6月对伊朗核设施空袭的同型战机
- 法案将债务上限提高5万亿美元，永久延续2017年减税政策，削减医疗补助等社会保障项目，增加移民执法和国防支出
- 德州中部发生灾难性洪水，至少82人死亡(其中28名儿童)，27名女童夏令营营员仍失踪，瓜达卢佩河45分钟内上涨26英尺
- 特朗普表示国土安全部长克里斯蒂·诺姆将赴现场，并可能于周五亲自访问灾区
- 在7月4日发布"HAPPY 4TH OF JULY!"庆祝独立日

**语调特点**: 充满胜利感和爱国主义激情，将政治成就与国家庆典巧妙结合，展现出统一国家和庆祝传统的领导形象

**值得关注**: 独立日当天签署如此重大法案的时机选择具有深刻的象征意义，UFC比赛进入白宫体现了特朗普独特的文化政治策略""",
                'key_topics': ['独立日庆祝', '立法胜利', '建国250周年', 'UFC白宫', '德州洪灾']
            }
        ],
        'recent_posts': [
            {
                'post_id': 'real_003',
                'content': 'This July 4th weekend I want to give a big "THANK YOU!" to the Heroic ICE Officers fighting every day to reclaim our Sovereignty and Freedom. It\'s called "REMIGRATION" and, it will, MAKE AMERICA GREAT AGAIN!',
                'created_at': '2025-07-06 00:50:00',
                'engagement_score': 51000
            }
        ],
        'status': 'fallback_data'
    }


def get_data():
    """获取数据 - 优先数据库，然后JSON文件，最后备用数据"""
    print("🔍 正在加载数据...")
    
    # 尝试从数据库加载（本地开发环境）
    summaries = get_real_summaries_from_db()
    posts = get_real_posts_from_db() 
    stats = get_real_stats_from_db()
    
    if summaries and stats:
        print("✅ 使用数据库数据")
        return {
            'statistics': stats,
            'summaries': summaries,
            'recent_posts': posts,
            'status': 'database_data'
        }
    
    # 尝试从JSON文件加载（Vercel部署环境）
    try:
        if os.path.exists('latest_data.json'):
            with open('latest_data.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print("✅ 使用JSON文件数据")
            return json_data
    except Exception as e:
        print(f"❌ JSON文件加载失败: {e}")
    
    # 最后使用备用数据
    print("⚠️ 数据库和JSON文件都不可用，使用备用数据")
    return get_fallback_data()


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
        data = get_data()
        
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
                    'key_topics': json.dumps(summary.get('key_topics', []), ensure_ascii=False)
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
        data = get_data()
        
        # 查找指定日期的摘要
        summary = None
        post_count = 0
        
        for s in data['summaries']:
            if s['analysis_date'] == date:
                summary = {
                    'summary_text': s['summary_text'],
                    'key_topics': json.dumps(s.get('key_topics', []), ensure_ascii=False)
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


@app.route('/api/stats')
def api_stats():
    """API接口 - 获取总体统计数据"""
    try:
        data = get_data()
        
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
        data = get_data()
        
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