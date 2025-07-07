#!/usr/bin/env python3
"""
Claude小结导入工具
用于将Claude的分析结果保存到数据库
"""

import sys
import argparse
import pytz

from database import TrumpPostsDB
from config import TIMEZONE


class SummaryImporter:
    """小结导入器"""
    
    def __init__(self):
        self.db = TrumpPostsDB()
        self.et_tz = pytz.timezone(TIMEZONE)
    
    def import_summary(self, date: str, summary_content: str) -> bool:
        """导入Claude分析的小结"""
        
        try:
            # 检查日期是否有帖子数据
            posts = self.db.get_posts_by_date(date)
            if not posts:
                print(f"❌ 错误：{date} 没有帖子数据")
                return False
            
            # 检查是否已存在小结
            existing_summary = self.db.get_summary_by_date(date)
            if existing_summary:
                confirm = input(f"⚠️  {date} 已存在小结，是否覆盖？(y/N): ")
                if confirm.lower() != 'y':
                    print("取消导入")
                    return False
            
            # 计算统计数据
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_reposts = sum(post.get('reposts_count', 0) 
                              for post in posts)
            total_comments = sum(post.get('comments_count', 0) 
                               for post in posts)
            
            # 保存小结
            summary_data = {
                'summary_date': date,
                'summary_content': summary_content,
                'post_count': len(posts),
                'total_likes': total_likes,
                'total_reposts': total_reposts,
                'total_comments': total_comments,
                'generated_by': 'Claude'
            }
            
            success = self.db.insert_daily_summary(summary_data)
            
            if success:
                print(f"✅ 成功保存 {date} 的Claude分析小结")
                print(f"📊 包含 {len(posts)} 条帖子的分析")
                return True
            else:
                print("❌ 保存失败")
                return False
                
        except Exception as e:
            print(f"❌ 导入失败：{e}")
            return False
    
    def import_from_file(self, date: str, file_path: str) -> bool:
        """从文件导入小结"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"❌ 文件 {file_path} 为空")
                return False
            
            return self.import_summary(date, content)
            
        except FileNotFoundError:
            print(f"❌ 文件不存在：{file_path}")
            return False
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
            return False


def main():
    """主函数 - 命令行界面"""
    parser = argparse.ArgumentParser(description='导入Claude分析的小结')
    parser.add_argument('date', help='日期 (YYYY-MM-DD格式)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='直接输入小结内容')
    group.add_argument('--file', help='从文件读取小结内容')
    
    args = parser.parse_args()
    
    print("📥 Claude小结导入工具")
    print("=" * 40)
    
    importer = SummaryImporter()
    
    if args.text:
        # 直接输入文本
        success = importer.import_summary(args.date, args.text)
    else:
        # 从文件导入
        success = importer.import_from_file(args.date, args.file)
    
    if success:
        print("\n🎉 导入完成！")
        print("📝 可以使用 'python main.py --status' 查看所有小结")
    else:
        print("\n❌ 导入失败")
        sys.exit(1)


if __name__ == "__main__":
    # 如果没有参数，提供交互式界面
    if len(sys.argv) == 1:
        print("📥 Claude小结导入工具 (交互模式)")
        print("=" * 40)
        
        date = input("请输入日期 (YYYY-MM-DD): ").strip()
        if not date:
            print("❌ 日期不能为空")
            sys.exit(1)
        
        print("\n请输入Claude的分析小结 (输入END结束):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines).strip()
        if not content:
            print("❌ 小结内容不能为空")
            sys.exit(1)
        
        importer = SummaryImporter()
        success = importer.import_summary(date, content)
        
        if success:
            print("\n🎉 导入完成！")
        else:
            print("\n❌ 导入失败")
            sys.exit(1)
    else:
        main() 