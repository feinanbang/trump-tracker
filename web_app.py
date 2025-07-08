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
    """真实的Claude分析数据 - 硬编码版本"""
    return {
        'statistics': {
            'total_posts': 62,
            'total_days': 4,
            'latest_post': '2025-07-07 18:30:00',
            'daily_stats': [
                {'date': '2025-07-06', 'post_count': 8},
                {'date': '2025-07-05', 'post_count': 14},
                {'date': '2025-07-04', 'post_count': 33},
                {'date': '2025-07-03', 'post_count': 2}
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

**语调特点**: 呈现强烈的胜利主义和民族主义语调，大量使用军事化和对抗性语言如"reclaim our Sovereignty"、"violent assault"、"strongest on Earth"等。在移民议题上采用极端化修辞，将移民描述为"入侵"威胁，同时在灾难应对上展现总统关怀形象。语调中透露出种族主义暗示，暗指要防止美国成为"第三世界国家"。

**值得关注**: "REMIGRATION"一词的使用极其危险，该术语在欧洲被奥地利极右翼活动家马丁·塞尔纳等人推广，与2019年新西兰基督城清真寺枪击案凶手有过联系，被批评为种族清洗的委婉说法。主流媒体基本忽视了这一危险术语的使用，未能充分报道其与白人民族主义的关联。特朗普将ICE官员描述为"日常遭受暴力攻击"，为加强执法行动制造理由。政府目标是将逮捕人数提升至每日3000人，是今年早期的三倍，这标志着美国移民政策向极端主义方向的历史性转变。""",
                'key_topics': ['REMIGRATION政策', '移民执法', '德州洪灾', 'Operation Apex Hammer', '种族清洗']
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

**语调特点**: 呈现出鲜明的双重情绪模式：前半段延续胜利庆祝的兴奋语调，大量分享庆祝活动的视频和图片；后期转为庄重的灾难应对模式，使用"GOD BLESS"等宗教用语表达哀悼和支持。这种情绪转换体现了其作为总统在国家危机时刻的角色转变能力。

**值得关注**: 法案签署仪式选择在7月4日并配合军机飞越，营造了强烈的爱国主义和军事力量展示氛围，暗示其将立法成就与军事威慑力结合的战略意图。德州洪灾的突发性和严重性(河流45分钟上涨26英尺)引发了对国家气象局预警系统和夏令营疏散程序的质疑。有专家质疑特朗普政府对国家海洋和大气管理局的人员削减是否影响了天气预报准确性。特朗普在庆祝立法胜利与应对国家灾难之间的快速切换，展现了现代总统职位的复杂性和挑战。""",
                'key_topics': ['ONE BIG BEAUTIFUL BILL ACT', '德州洪灾', '独立日庆祝', '军机飞越', '联邦响应']
            },
            {
                'analysis_date': '2025-07-04',
                'post_count': 33,
                'summary_text': """## 2025-07-04 Trump Truth Social 动态深度分析

**核心观点**: 特朗普总统在"ONE BIG BEAUTIFUL BILL ACT"通过后进行了全方位的政治胜利庆祝，并正式启动美国建国250周年纪念活动，展现了其将立法成就与爱国主义叙事完美结合的政治策略。

**主要内容**:
- 众议院以218-214的票数通过"ONE BIG BEAUTIFUL BILL ACT"，该法案预计将在10年内增加约3万亿美元的国债，但永久延续了特朗普2017年的减税政策
- 法案包含数百项条款，涉及税收减免、移民执法、国防支出增加1500亿美元，以及削减医疗补助、食品券等社会保障项目
- 在爱荷华州启动"美国250周年"庆典，提出"伟大美国州博览会"概念，将在全国各地举办活动，最终在2026年7月4日于国家广场举办盛大庆典
- 宣布将在白宫举办UFC冠军赛作为250周年庆典的一部分，由UFC首席执行官达纳·怀特监督
- 逐一感谢共和党领袖，包括众议院议长约翰逊、参议院多数党领袖图恩等关键人物
- 在椭圆形办公室会见被哈马斯扣押584天的人质伊丹·亚历山大
- 推广纽特·金里奇新书《特朗普的胜利：美国最伟大的复出》

**语调特点**: 极度兴奋和胜利的狂欢模式，33条帖子中大量使用全大写字母、感叹号和极端修饰词。采用"感谢马拉松"策略，体现其重视个人关系和公开认可的政治风格。将立法胜利、爱国庆典、媒体宣传完美整合为统一的胜利叙事。

**值得关注**: 218-214的投票结果虽然显示党派团结，但仅有4票的微弱优势反映了共和党内部分歧。众议院少数党领袖杰弗里斯发表了超过8小时32分钟的演讲来拖延投票，打破了众议院历史记录。该法案使用预算和解程序绕过参议院60票门槛，副总统万斯投出关键的决定性一票。特朗普将反共宣言、UFC赛事、爱国庆典等多元素整合，展现了其独特的政治表演艺术风格。法案中还隐藏了限制各州AI法律执行的条款，引发了对选举诚信的担忧。""",
                'key_topics': ['立法胜利', '建国250周年', 'UFC白宫赛事', '感谢马拉松', '预算和解']
            },
            {
                'analysis_date': '2025-07-03',
                'post_count': 2,
                'summary_text': """## 2025-07-03 Trump Truth Social 动态深度分析

**核心观点**: 特朗普总统宣称其政府成功控制了鸡蛋价格，将此作为执政成果进行宣传。

**主要内容**:
- 声称在其1月20日就职后，成功让鸡蛋价格回归合理水平
- 批评媒体此前关于鸡蛋价格"涨了四倍"、"价格飞涨"的报道为"假新闻"
- 强调现在鸡蛋供应充足且价格便宜
- 引用公众感谢话语为自己的政策成果背书
- 第一条帖子内容不明确，可能是转发或技术显示问题

**语调特点**: 典型的特朗普式表达风格，带有自我肯定的胜利宣告语调，同时对媒体表达不满。使用引号营造民众感谢的效果，体现其擅长的叙事技巧。

**值得关注**: 鸡蛋价格确实是美国民生关注焦点。2022-2023年美国鸡蛋价格因禽流感疫情大幅上涨，成为通胀压力的象征。特朗普将价格回落归功于自己的政策，这是典型的政治归因策略。不过价格变化通常受多重因素影响，包括供应链恢复、疫情缓解等市场因素。""",
                'key_topics': ['鸡蛋价格', '通胀控制', '媒体批评', '执政成果', '民生政策']
            }
        ],
        'recent_posts': [],  # 不需要帖子数据
        'status': 'real_analysis_data'
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