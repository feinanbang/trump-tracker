#!/usr/bin/env python3
"""
本地AI小结生成器
不依赖外部API，使用本地算法生成智能小结
"""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz

from database import TrumpPostsDB
from config import TIMEZONE

logger = logging.getLogger(__name__)


class LocalTrumpSummarizer:
    """本地Trump帖子智能小结生成器"""
    
    def __init__(self):
        self.db = TrumpPostsDB()
        self.et_tz = pytz.timezone(TIMEZONE)
        
        # 政治关键词词典
        self.political_keywords = {
            'election': ['election', 'vote', 'voting', 'ballot', 'poll', '民调', '选举', '投票'],
            'economy': ['economy', 'economic', 'jobs', 'employment', 'business', '经济', '就业', '商业'],
            'border': ['border', 'immigration', 'wall', 'security', '边境', '移民', '安全'],
            'media': ['media', 'fake news', 'press', 'journalist', '媒体', '新闻', '记者'],
            'political': ['democrat', 'republican', 'congress', 'senate', '民主党', '共和党', '国会'],
            'legal': ['court', 'judge', 'trial', 'case', 'legal', '法院', '法官', '审判'],
            'campaign': ['campaign', 'rally', 'support', 'donate', '竞选', '集会', '支持']
        }
        
        # 情感词典
        self.sentiment_words = {
            'positive': ['great', 'excellent', 'wonderful', 'amazing', 'fantastic', 'best', 'winning'],
            'negative': ['terrible', 'horrible', 'worst', 'bad', 'failing', 'disaster', 'corrupt'],
            'neutral': ['said', 'reported', 'announced', 'stated', 'mentioned']
        }
        
    def extract_keywords(self, posts: List[Dict]) -> Dict[str, int]:
        """提取关键词和频率"""
        all_text = ' '.join([post.get('content', '') for post in posts]).lower()
        
        keyword_counts = {}
        for category, keywords in self.political_keywords.items():
            count = 0
            for keyword in keywords:
                count += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', all_text))
            if count > 0:
                keyword_counts[category] = count
        
        return keyword_counts
    
    def analyze_sentiment(self, posts: List[Dict]) -> str:
        """分析情感倾向"""
        all_text = ' '.join([post.get('content', '') for post in posts]).lower()
        
        sentiment_scores = {}
        for sentiment, words in self.sentiment_words.items():
            score = 0
            for word in words:
                score += len(re.findall(r'\b' + re.escape(word) + r'\b', all_text))
            sentiment_scores[sentiment] = score
        
        if sentiment_scores['positive'] > sentiment_scores['negative']:
            return "积极乐观"
        elif sentiment_scores['negative'] > sentiment_scores['positive']:
            return "批评质疑"
        else:
            return "中性陈述"
    
    def extract_mentions(self, posts: List[Dict]) -> List[str]:
        """提取@提及和重要人物"""
        mentions = set()
        all_text = ' '.join([post.get('content', '') for post in posts])
        
        # 提取@mentions
        at_mentions = re.findall(r'@(\w+)', all_text)
        mentions.update(at_mentions)
        
        # 重要人物关键词
        important_people = ['Biden', 'Harris', 'Pelosi', 'McCarthy', 'DeSantis', '拜登', '哈里斯']
        for person in important_people:
            if person.lower() in all_text.lower():
                mentions.add(person)
        
        return list(mentions)[:5]  # 最多返回5个
    
    def categorize_content(self, posts: List[Dict]) -> Dict[str, List[str]]:
        """对内容进行分类"""
        categories = {
            '政治观点': [],
            '媒体批评': [],
            '政策主张': [],
            '个人生活': [],
            '其他': []
        }
        
        for post in posts:
            content = post.get('content', '').lower()
            post_time = post.get('post_time', '')
            short_content = content[:50] + "..." if len(content) > 50 else content
            
            if any(word in content for word in ['fake news', 'media', 'press', '媒体', '新闻']):
                categories['媒体批评'].append(f"[{post_time}] {short_content}")
            elif any(word in content for word in ['policy', 'border', 'economy', '政策', '边境', '经济']):
                categories['政策主张'].append(f"[{post_time}] {short_content}")
            elif any(word in content for word in ['election', 'vote', 'campaign', '选举', '竞选']):
                categories['政治观点'].append(f"[{post_time}] {short_content}")
            elif any(word in content for word in ['family', 'personal', 'golf', '家庭', '个人']):
                categories['个人生活'].append(f"[{post_time}] {short_content}")
            else:
                categories['其他'].append(f"[{post_time}] {short_content}")
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    def generate_time_analysis(self, posts: List[Dict]) -> str:
        """分析发帖时间模式"""
        times = []
        for post in posts:
            time_str = post.get('post_time', '')
            if time_str:
                try:
                    hour = int(time_str.split(':')[0])
                    times.append(hour)
                except:
                    continue
        
        if not times:
            return "时间分布：无法分析"
        
        if max(times) - min(times) <= 2:
            return f"时间分布：集中在{min(times)}:00-{max(times)}:00"
        elif all(t < 12 for t in times):
            return "时间分布：主要在上午发布"
        elif all(t >= 12 for t in times):
            return "时间分布：主要在下午/晚上发布"
        else:
            return f"时间分布：从{min(times)}:00到{max(times)}:00，分布较广"
    
    def create_intelligent_summary(self, posts: List[Dict], date: str) -> str:
        """生成智能小结"""
        
        # 基础统计
        post_count = len(posts)
        total_likes = sum(post.get('likes_count', 0) for post in posts)
        total_reposts = sum(post.get('reposts_count', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        
        # 分析组件
        keywords = self.extract_keywords(posts)
        sentiment = self.analyze_sentiment(posts)
        mentions = self.extract_mentions(posts)
        categories = self.categorize_content(posts)
        time_pattern = self.generate_time_analysis(posts)
        
        # 构建小结
        summary_parts = [
            f"## {date} Trump Truth Social 动态小结",
            "",
            f"**📊 数据概览**：{date}共发布{post_count}条帖子，获得{total_likes:,}个赞、{total_reposts:,}次转发、{total_comments:,}条评论。",
            "",
            f"**⏰ {time_pattern}**",
            "",
            f"**🎯 内容情感**：{sentiment}",
            ""
        ]
        
        # 主要话题
        if keywords:
            topic_list = []
            topic_map = {
                'election': '选举政治',
                'economy': '经济议题', 
                'border': '边境安全',
                'media': '媒体批评',
                'political': '政治立场',
                'legal': '法律事务',
                'campaign': '竞选活动'
            }
            
            for topic, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:3]:
                chinese_topic = topic_map.get(topic, topic)
                topic_list.append(f"{chinese_topic}({count}次)")
            
            summary_parts.extend([
                f"**🔥 主要话题**：{' | '.join(topic_list)}",
                ""
            ])
        
        # 内容分类
        if categories:
            summary_parts.append("**📝 内容分类**：")
            for category, items in categories.items():
                if items:
                    summary_parts.append(f"• **{category}** ({len(items)}条)")
                    for item in items[:2]:  # 最多显示2条
                        summary_parts.append(f"  - {item}")
            summary_parts.append("")
        
        # 重要提及
        if mentions:
            summary_parts.extend([
                f"**👥 重要提及**：{' | '.join(mentions)}",
                ""
            ])
        
        # 原文链接
        summary_parts.extend([
            "### 📎 原文链接：",
            *[f"• [{post.get('post_time', '时间未知')}] {post.get('post_url', '')}" 
              for post in sorted(posts, key=lambda x: x.get('post_time', ''))],
            "",
            "*本小结由本地智能算法生成，基于关键词分析、情感识别和内容分类技术。*"
        ])
        
        return "\n".join(summary_parts)
    
    def generate_daily_summary(self, date: str) -> Optional[str]:
        """生成指定日期的智能小结"""
        try:
            logger.info(f"开始生成 {date} 的本地智能小结")
            
            # 获取指定日期的所有帖子
            posts = self.db.get_posts_by_date(date)
            
            if not posts:
                logger.info(f"{date} 没有帖子数据")
                return None
            
            logger.info(f"找到 {len(posts)} 条帖子，开始生成智能小结")
            
            # 生成智能小结
            summary = self.create_intelligent_summary(posts, date)
            
            # 保存到数据库
            post_count = len(posts)
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_reposts = sum(post.get('reposts_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) for post in posts)
            
            summary_data = {
                'summary_date': date,
                'summary_content': summary,
                'post_count': post_count,
                'total_likes': total_likes,
                'total_reposts': total_reposts,
                'total_comments': total_comments,
                'generated_by': 'Local_AI'
            }
            
            if self.db.insert_daily_summary(summary_data):
                logger.info(f"{date} 本地智能小结保存成功")
            
            return summary
            
        except Exception as e:
            logger.error(f"生成本地智能小结失败: {e}")
            return None


def main():
    """测试本地智能小结功能"""
    print("🤖 本地智能小结系统测试")
    print("=" * 50)
    
    try:
        summarizer = LocalTrumpSummarizer()
        
        # 生成昨天的小结
        yesterday = (datetime.now(pytz.timezone(TIMEZONE)) - 
                    timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"📝 正在生成 {yesterday} 的本地智能小结...")
        summary = summarizer.generate_daily_summary(yesterday)
        
        if summary:
            print(f"\n✅ 本地智能小结生成成功!")
            print(f"\n{summary}")
        else:
            print(f"\n❌ 没有找到 {yesterday} 的数据")
            
    except Exception as e:
        print(f"❌ 系统错误: {e}")


if __name__ == "__main__":
    main() 