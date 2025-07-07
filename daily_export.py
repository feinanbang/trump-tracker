#!/usr/bin/env python3
"""
每日Trump帖子自动导出工具
自动生成格式化文件供Claude分析
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
import pytz

from database import TrumpPostsDB
from config import TIMEZONE


class DailyExporter:
    """每日帖子导出器"""
    
    def __init__(self, export_dir: str = "daily_exports"):
        self.db = TrumpPostsDB()
        self.et_tz = pytz.timezone(TIMEZONE)
        self.export_dir = export_dir
        
        # 创建导出目录
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
    
    def export_for_claude(self, date: str) -> str:
        """导出适合Claude分析的格式"""
        
        posts = self.db.get_posts_by_date(date)
        if not posts:
            return None
        
        # 按时间排序
        sorted_posts = sorted(posts, key=lambda x: x.get('post_time', ''))
        
        # 创建Claude分析用的Markdown文件
        current_time = datetime.now(self.et_tz).strftime('%Y-%m-%d %H:%M:%S')
        content = [
            "# Trump Truth Social 帖子分析请求",
            f"**日期**: {date}",
            f"**帖子数量**: {len(posts)}条",
            f"**导出时间**: {current_time} (ET)",
            "",
            "## 📋 角色设定",
            "",
            "你是一个非常资深的新闻总结专家。你非常了解美国的政治历史和政治传统、惯例。你非常了解美国文化。现在，你会每天收到一份markdown格式的文件，里面记录了过去一天内特朗普总统的所有推特内容和原文网址。你被要求每天总结特朗普总统的推特，并输出一份日度的小结。",
            "",
            "## 📋 分析要求",
            "",
            "1. **简明扼要**：用5句话讲清楚发生了什么，就像最严格的新闻要求一样",
            "2. **美国常识解释**：如果推文涉及一些美国常识，对特朗普的观点做必要的解释，但不要太长",
            "3. **不跳过步骤**：分析每个重要内容",
            "4. **访问链接**：这里面的链接全部是原文链接，请一个一个访问并总结",
            "5. **使用工具**：必要时，请使用浏览器工具",
            "6. **深度理解**：深度理解每条帖子的真实含义和背景",
            "7. **政策分析**：识别主要话题、政策立场和情绪表达",
            "8. **客观中立**：保持客观中立的新闻分析角度",
            "",
            "**小结格式**：",
            "```",
            f"## {date} Trump Truth Social 动态深度分析",
            "",
            "**核心观点**: [总结当日最重要的1-2个观点]",
            "",
            "**主要内容**: ",
            "- [按重要性排列的3-5个要点]",
            "",
            "**语调特点**: [分析整体语调和情绪]",
            "",
            "**值得关注**: [指出特别重要或争议性的内容]",
            "```",
            "",
            "---",
            "",
            f"## 📝 {date} 帖子内容",
            ""
        ]
        
        # 添加每条帖子
        for i, post in enumerate(sorted_posts, 1):
            post_time = post.get('post_time', '未知时间')
            post_content = post.get('content', '').strip()
            post_url = post.get('post_url', '')
            likes = post.get('likes_count', 0)
            reposts = post.get('reposts_count', 0)
            comments = post.get('comments_count', 0)
            
            content.extend([
                f"### 帖子 {i} [{post_time}]",
                "",
                "**内容**：",
                f"{post_content}",
                "",
                f"**互动数据**：👍 {likes} | 🔄 {reposts} | 💬 {comments}",
                f"**原文链接**：{post_url}",
                "",
                "---",
                ""
            ])
        
        # 添加导出说明
        content.extend([
            "## 💡 分析完成后",
            "",
            "请将分析结果复制，然后运行以下命令保存到数据库：",
            "```bash",
            f'python import_summary.py "{date}" "您的分析结果"',
            "```",
            "",
            "谢谢！🙏"
        ])
        
        return "\n".join(content)
    
    def export_json(self, date: str) -> Dict:
        """导出JSON格式数据"""
        
        posts = self.db.get_posts_by_date(date)
        if not posts:
            return None
        
        export_data = {
            "date": date,
            "post_count": len(posts),
            "export_time": datetime.now(self.et_tz).isoformat(),
            "posts": []
        }
        
        for post in sorted(posts, key=lambda x: x.get('post_time', '')):
            export_data["posts"].append({
                "time": post.get('post_time'),
                "content": post.get('content'),
                "url": post.get('post_url'),
                "likes": post.get('likes_count', 0),
                "reposts": post.get('reposts_count', 0),
                "comments": post.get('comments_count', 0)
            })
        
        return export_data
    
    def save_daily_export(self, date: str, 
                         formats: List[str] = ['md']) -> List[str]:
        """保存每日导出文件"""
        
        saved_files = []
        
        if 'md' in formats:
            # 导出Markdown格式
            md_content = self.export_for_claude(date)
            if md_content:
                filename = f"trump_{date}_for_claude.md"
                md_file = os.path.join(self.export_dir, filename)
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                saved_files.append(md_file)
        
        if 'json' in formats:
            # 导出JSON格式
            json_data = self.export_json(date)
            if json_data:
                filename = f"trump_{date}_data.json"
                json_file = os.path.join(self.export_dir, filename)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                saved_files.append(json_file)
        
        return saved_files
    
    def auto_export_yesterday(self) -> List[str]:
        """自动导出昨天的数据"""
        yesterday = (datetime.now(self.et_tz) - 
                    timedelta(days=1)).strftime('%Y-%m-%d')
        return self.save_daily_export(yesterday, ['md', 'json'])
    
    def check_pending_dates(self) -> List[str]:
        """检查哪些日期有数据但没有小结"""
        
        pending_dates = []
        
        # 检查最近7天
        for i in range(7):
            current_date = (datetime.now(self.et_tz) - 
                           timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 检查是否有帖子数据
            posts = self.db.get_posts_by_date(current_date)
            if not posts:
                continue
            
            # 检查是否已有小结
            summary = self.db.get_summary_by_date(current_date)
            if not summary:
                pending_dates.append(current_date)
        
        return pending_dates


def main():
    """主函数 - 自动导出功能"""
    print("📤 Trump Truth Social 每日导出工具")
    print("=" * 50)
    
    exporter = DailyExporter()
    
    # 检查待处理的日期
    pending_dates = exporter.check_pending_dates()
    
    if pending_dates:
        print(f"📋 发现 {len(pending_dates)} 个日期需要生成小结：")
        for date in pending_dates:
            posts = exporter.db.get_posts_by_date(date)
            print(f"  • {date} ({len(posts)}条帖子)")
        
        print("\n🚀 开始导出...")
        
        for date in pending_dates:
            files = exporter.save_daily_export(date, ['md'])
            if files:
                print(f"✅ {date} 导出完成: {files[0]}")
            else:
                print(f"❌ {date} 导出失败（无数据）")
        
        print("\n💡 导出完成！请查看 daily_exports/ 文件夹")
        print("📁 将 .md 文件发送给Claude，获得分析后使用：")
        print("   python import_summary.py [日期] [Claude的分析结果]")
        
    else:
        print("✅ 所有日期都已有小结，无需导出")


if __name__ == "__main__":
    main() 