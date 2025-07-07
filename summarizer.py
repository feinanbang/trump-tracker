#!/usr/bin/env python3
"""
Trump Truth Social 帖子自动小结系统
使用Hugging Face API生成每日小结
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz

from database import TrumpPostsDB
from config import TIMEZONE
from utils import setup_logging
import logging

# 设置日志系统并获取logger
try:
    setup_logging()  # 初始化日志系统
    logger = logging.getLogger(__name__)
except Exception:
    logger = logging.getLogger(__name__)


class TrumpPostSummarizer:
    """Trump帖子自动小结生成器"""
    
    def __init__(self, hf_api_token: Optional[str] = None):
        self.db = TrumpPostsDB()
        self.et_tz = pytz.timezone(TIMEZONE)
        
        # 从环境变量获取Hugging Face API token
        self.hf_token = hf_api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        if not self.hf_token:
            raise ValueError("需要设置HUGGINGFACE_API_TOKEN环境变量")
        
        # Hugging Face API配置
        self.api_base = "https://api-inference.huggingface.co/models"
        
        # 推荐的免费模型（按优先级排序）
        self.models = [
            "microsoft/DialoGPT-large",  # 对话型，适合总结
            "facebook/blenderbot-400M-distill",  # 轻量级对话模型
            "google/flan-t5-large",  # 指令跟随模型
            "microsoft/DialoGPT-medium"  # 中等规模备用
        ]
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
    
    def create_summary_prompt(self, posts: List[Dict], date: str) -> str:
        """创建小结提示词"""
        
        # 按时间排序帖子
        sorted_posts = sorted(posts, key=lambda x: x.get('post_time', ''))
        
        # 构建帖子内容
        posts_text = ""
        for i, post in enumerate(sorted_posts, 1):
            post_time = post.get('post_time', '未知时间')
            content = post.get('content', '').strip()
            post_url = post.get('post_url', '')
            
            posts_text += (f"{i}. [{post_time}] {content}\n"
                           f"   链接: {post_url}\n\n")
        
        # 小结提示词（中英文混合，确保模型理解）
        prompt = f"""
请为以下Trump在Truth Social上{date}发布的帖子生成一份简洁的中文小结：

=== {date} Trump Truth Social 帖子 ===
{posts_text}

请按以下要求生成小结：
1. 用中文总结这一天的主要内容和观点
2. 突出重点话题和关键信息
3. 保持客观和事实性的描述
4. 控制在200字以内
5. 在小结后列出所有帖子的原文链接以供查证

小结格式：
## {date} Trump Truth Social 动态小结

[在这里写小结内容]

### 原文链接：
{chr(10).join([f"• {post.get('post_url', '')}" for post in sorted_posts])}
"""
        return prompt
    
    def call_huggingface_api(self, prompt: str, model_name: str) -> Optional[str]:
        """调用Hugging Face API生成小结"""
        try:
            api_url = f"{self.api_base}/{model_name}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "min_length": 100,
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "no_repeat_ngram_size": 3
                }
            }
            
            logger.info(f"调用Hugging Face API: {model_name}")
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                except Exception as e:
                    logger.error(f"JSON解析失败: {e}")
                    return None
                
                if result is None:
                    logger.error("API返回空结果")
                    return None
                
                # 检查API错误
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"API返回错误: {result['error']}")
                    return None
                
                # 处理不同的响应格式
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text:
                        return generated_text.strip()
                elif isinstance(result, dict) and 'generated_text' in result:
                    return result['generated_text'].strip()
                else:
                    logger.warning(f"意外的API响应格式: {result}")
                    return None
                    
            elif response.status_code == 503:
                logger.warning(f"模型 {model_name} 正在加载中，请稍后重试")
                return None
            else:
                logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("API调用超时")
            return None
        except Exception as e:
            logger.error(f"调用Hugging Face API失败: {e}")
            return None
    
    def generate_summary_with_fallback(self, prompt: str) -> Optional[str]:
        """使用多个模型生成小结（备用机制）"""
        for model_name in self.models:
            logger.info(f"尝试使用模型: {model_name}")
            
            summary = self.call_huggingface_api(prompt, model_name)
            if summary:
                logger.info(f"成功使用模型 {model_name} 生成小结")
                return summary
            else:
                logger.warning(f"模型 {model_name} 生成失败，尝试下一个...")
        
        logger.error("所有模型都生成失败")
        return None
    
    def create_fallback_summary(self, posts: List[Dict], date: str) -> str:
        """创建备用小结（当API失败时）"""
        post_count = len(posts)
        
        # 计算互动数据
        total_likes = sum(post.get('likes_count', 0) for post in posts)
        total_reposts = sum(post.get('reposts_count', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        
        # 提取关键词（简单实现）
        all_content = ' '.join([post.get('content', '') for post in posts])
        
        # 生成简单小结
        summary = f"""## {date} Trump Truth Social 动态小结

**数据概览**: {date}共发布{post_count}条帖子，获得{total_likes:,}个赞、{total_reposts:,}次转发、{total_comments:,}条评论。

**内容摘要**: 由于AI服务暂时不可用，此为系统自动生成的基础统计信息。如需详细内容分析，请查看下方原文链接。

### 原文链接：
{chr(10).join([f"• {post.get('post_url', '')}" for post in posts])}

*注：此小结由系统自动生成，如需AI智能小结请稍后重试。*
"""
        return summary
    
    def save_summary_to_database(self, date: str, summary_content: str, 
                                posts: List[Dict]) -> bool:
        """将小结保存到数据库"""
        try:
            # 计算统计数据
            post_count = len(posts)
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_reposts = sum(post.get('reposts_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) 
                               for post in posts)
            
            summary_data = {
                'summary_date': date,
                'summary_content': summary_content,
                'post_count': post_count,
                'total_likes': total_likes,
                'total_reposts': total_reposts,
                'total_comments': total_comments,
                'generated_by': 'AI'
            }
            
            return self.db.insert_daily_summary(summary_data)
            
        except Exception as e:
            logger.error(f"保存小结到数据库失败: {e}")
            return False
    
    def generate_daily_summary(self, date: str) -> Optional[str]:
        """生成指定日期的小结"""
        try:
            logger.info(f"开始生成 {date} 的小结")
            
            # 获取指定日期的所有帖子
            posts = self.db.get_posts_by_date(date)
            
            if not posts:
                logger.info(f"{date} 没有帖子数据")
                return None
            
            logger.info(f"找到 {len(posts)} 条帖子，开始生成小结")
            
            # 创建提示词
            prompt = self.create_summary_prompt(posts, date)
            
            # 尝试使用AI生成小结
            ai_summary = self.generate_summary_with_fallback(prompt)
            
            if ai_summary:
                summary = ai_summary
                logger.info("AI小结生成成功")
            else:
                # 使用备用小结
                summary = self.create_fallback_summary(posts, date)
                logger.warning("使用备用小结")
            
            # 保存到数据库
            if self.save_summary_to_database(date, summary, posts):
                logger.info(f"{date} 小结保存成功")
            
            return summary
            
        except Exception as e:
            logger.error(f"生成日期小结失败: {e}")
            return None
    
    def generate_recent_summaries(self, days: int = 7) -> Dict[str, str]:
        """生成最近几天的小结"""
        summaries = {}
        
        for i in range(days):
            date = (datetime.now(self.et_tz) - timedelta(days=i)).strftime('%Y-%m-%d')
            summary = self.generate_daily_summary(date)
            
            if summary:
                summaries[date] = summary
        
        return summaries


def main():
    """测试小结功能"""
    print("🤖 Trump Truth Social 自动小结系统测试")
    print("=" * 50)
    
    try:
        # 初始化小结器
        summarizer = TrumpPostSummarizer()
        
        # 生成昨天的小结
        yesterday = (datetime.now(pytz.timezone(TIMEZONE)) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"📝 正在生成 {yesterday} 的小结...")
        summary = summarizer.generate_daily_summary(yesterday)
        
        if summary:
            print(f"\n✅ 小结生成成功!")
            print(f"\n{summary}")
        else:
            print(f"\n❌ 没有找到 {yesterday} 的数据")
            
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("💡 请设置环境变量: HUGGINGFACE_API_TOKEN")
    except Exception as e:
        print(f"❌ 系统错误: {e}")


if __name__ == "__main__":
    main() 