#!/usr/bin/env python3
"""
Claude API 小结生成器
使用Anthropic Claude API生成高质量小结
"""

import os
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pytz

from database import TrumpPostsDB
from config import TIMEZONE

logger = logging.getLogger(__name__)


class ClaudeSummarizer:
    """Claude API 小结生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.db = TrumpPostsDB()
        self.et_tz = pytz.timezone(TIMEZONE)
        
        # 从环境变量获取Claude API key
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置CLAUDE_API_KEY环境变量")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    def create_summary_prompt(self, posts: List[Dict], date: str) -> str:
        """创建小结提示词"""
        
        # 按时间排序帖子
        sorted_posts = sorted(posts, key=lambda x: x.get('post_time', ''))
        
        # 构建帖子内容
        posts_content = []
        for i, post in enumerate(sorted_posts, 1):
            post_time = post.get('post_time', '未知时间')
            content = post.get('content', '').strip()
            post_url = post.get('post_url', '')
            
            posts_content.append(f"帖子{i} [{post_time}]:\n{content}\n链接: {post_url}\n")
        
        prompt = f"""请为以下Trump在Truth Social上{date}发布的帖子生成一份专业的中文小结：

=== {date} Trump Truth Social 帖子内容 ===
{''.join(posts_content)}

请按以下要求生成小结：

1. **深度内容分析**: 理解每条帖子的真实含义，而不是简单的关键词统计
2. **主题归纳**: 识别当日的主要话题和观点
3. **语调分析**: 分析Trump的情绪和态度
4. **重要信息提取**: 突出政策立场、重要声明、争议点等
5. **客观总结**: 保持新闻报道的客观性

小结格式要求：
## {date} Trump Truth Social 动态深度分析

**核心观点**: [总结当日最重要的1-2个观点]

**主要内容**: 
- [按重要性排列的3-5个要点]

**语调特点**: [分析整体语调和情绪]

**值得关注**: [指出特别重要或争议性的内容]

### 原文链接参考：
{chr(10).join([f"• [{post.get('post_time', '时间未知')}] {post.get('post_url', '')}" for post in sorted_posts])}

请生成深度分析性的小结，重点关注内容的实质含义，而非表面统计。"""

        return prompt
    
    def call_claude_api(self, prompt: str) -> Optional[str]:
        """调用Claude API生成小结"""
        try:
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            logger.info("调用Claude API生成小结")
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                logger.info("Claude API调用成功")
                return content.strip()
            else:
                logger.error(f"Claude API调用失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Claude API调用超时")
            return None
        except Exception as e:
            logger.error(f"调用Claude API失败: {e}")
            return None
    
    def generate_daily_summary(self, date: str) -> Optional[str]:
        """生成指定日期的小结"""
        try:
            logger.info(f"开始生成 {date} 的Claude小结")
            
            # 获取指定日期的所有帖子
            posts = self.db.get_posts_by_date(date)
            
            if not posts:
                logger.info(f"{date} 没有帖子数据")
                return None
            
            logger.info(f"找到 {len(posts)} 条帖子，开始生成小结")
            
            # 创建提示词
            prompt = self.create_summary_prompt(posts, date)
            
            # 调用Claude API
            summary = self.call_claude_api(prompt)
            
            if summary:
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
                    'generated_by': 'Claude'
                }
                
                if self.db.insert_daily_summary(summary_data):
                    logger.info(f"{date} Claude小结保存成功")
                
                return summary
            else:
                logger.error("Claude小结生成失败")
                return None
            
        except Exception as e:
            logger.error(f"生成Claude小结失败: {e}")
            return None


def main():
    """测试Claude小结功能"""
    print("🤖 Claude API 小结系统测试")
    print("=" * 50)
    
    try:
        # 初始化Claude小结器
        summarizer = ClaudeSummarizer()
        
        # 生成昨天的小结
        from datetime import timedelta
        yesterday = (datetime.now(pytz.timezone(TIMEZONE)) - 
                    timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"📝 正在生成 {yesterday} 的Claude小结...")
        summary = summarizer.generate_daily_summary(yesterday)
        
        if summary:
            print(f"\n✅ Claude小结生成成功!")
            print(f"\n{summary}")
        else:
            print(f"\n❌ 没有找到 {yesterday} 的数据或API调用失败")
            
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("💡 请设置环境变量: CLAUDE_API_KEY")
    except Exception as e:
        print(f"❌ 系统错误: {e}")


if __name__ == "__main__":
    main() 