#!/usr/bin/env python3
"""
Trump Truth Social 爬虫主程序

功能：
1. 每小时自动爬取Trump在Truth Social上的最新帖子
2. 按天存储数据（美国东部时区）
3. 支持批量爬取历史数据
4. 无头浏览器运行，不占用屏幕
5. 完整的日志记录和错误处理

使用方法：
    python main.py                    # 启动定时爬虫
    python main.py --historical 30   # 爬取过去30天的历史数据
    python main.py --test            # 测试运行一次
    python main.py --status          # 查看数据库状态
"""

import argparse
import sys
import logging
from datetime import datetime, timedelta

from utils import setup_logging, create_summary_report, check_system_requirements
from scraper import TruthSocialScraper
from scheduler import TrumpScraperScheduler
from database import TrumpPostsDB
from summarizer import TrumpPostSummarizer
from claude_summarizer import ClaudeSummarizer
from daily_export import DailyExporter
from config import TIMEZONE
import pytz

# logger will be initialized after setup_logging() is called
logger = None


def test_scrape():
    """测试爬取功能"""
    print(f"\n🧪 启动测试模式")
    print(f"🎯 将爬取最新的帖子进行测试")
    print(f"⏰ 预计耗时：1-3分钟")
    print("=" * 40)
    
    logger.info("开始测试爬取...")
    
    print("🔧 正在初始化爬虫...")
    scraper = TruthSocialScraper()
    
    print("🌐 正在启动无头浏览器...")
    results = scraper.run_with_retry()
    
    if results:
        print(f"\n✅ 测试成功！爬取到 {len(results)} 个帖子")
        logger.info(f"测试成功！爬取到 {len(results)} 个帖子")
        print(create_summary_report(results))
    else:
        print(f"\n📝 测试完成，没有发现新帖子")
        logger.info("测试完成，没有新帖子")
    
    return len(results)


def historical_scrape(days_back: int):
    """批量爬取历史数据"""
    print(f"\n🚀 启动Trump Truth Social历史数据爬虫")
    print(f"📅 目标：爬取过去 {days_back} 天的历史数据")
    print(f"⏰ 预计耗时：10-30分钟（取决于数据量）")
    print(f"💡 提示：程序正在后台运行，请耐心等待...")
    print("=" * 60)
    
    logger.info(f"开始爬取过去 {days_back} 天的历史数据...")
    
    print("🔧 正在初始化爬虫...")
    scraper = TruthSocialScraper()
    
    print("🌐 正在启动无头浏览器...")
    results = scraper.run_with_retry(days_back=days_back)
    
    if results:
        print(f"\n✅ 历史数据爬取成功！")
        logger.info(f"历史数据爬取成功！共获取 {len(results)} 个帖子")
        print(create_summary_report(results))
    else:
        print(f"\n📝 历史数据爬取完成，没有发现新帖子")
        logger.info("历史数据爬取完成，没有新帖子")
    
    return len(results)


def generate_summary(date: str):
    """生成指定日期的小结"""
    try:
        print(f"\n📝 正在生成 {date} 的小结...")
        print("🤖 优先尝试Claude API，失败时使用Hugging Face...")
        print("=" * 50)
        
        # 首先尝试Claude API
        try:
            claude_summarizer = ClaudeSummarizer()
            summary = claude_summarizer.generate_daily_summary(date)
            
            if summary:
                print(f"\n✅ Claude AI小结生成成功！")
                print(f"\n{summary}")
                logger.info(f"成功生成 {date} 的Claude小结")
                return
        except ValueError as claude_error:
            logger.warning(f"Claude API配置问题: {claude_error}")
            print("⚠️ Claude API未配置，切换到Hugging Face...")
        except Exception as claude_error:
            logger.warning(f"Claude API失败: {claude_error}")
            print("⚠️ Claude API不可用，切换到Hugging Face...")
        
        # 使用Hugging Face备用
        try:
            hf_summarizer = TrumpPostSummarizer()
            summary = hf_summarizer.generate_daily_summary(date)
            
            if summary and "由于AI服务暂时不可用" not in summary:
                print(f"\n✅ Hugging Face小结生成成功！")
                print(f"\n{summary}")
                logger.info(f"成功生成 {date} 的Hugging Face小结")
                return
            else:
                print(f"\n⚠️ AI服务暂时不可用，生成了基础统计小结")
                print(f"\n{summary}")
                logger.info(f"生成了 {date} 的基础统计小结")
        except Exception as hf_error:
            logger.warning(f"Hugging Face失败: {hf_error}")
            print(f"\n❌ 没有找到 {date} 的数据")
            
    except Exception as e:
        print(f"❌ 生成小结失败: {e}")
        logger.error(f"生成小结失败: {e}")


def export_for_claude():
    """导出待处理日期的Claude分析文件"""
    try:
        print("\n📤 Trump Truth Social 每日导出工具")
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
            
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        logger.error(f"导出失败: {e}")


def show_status():
    """显示数据库状态"""
    db = TrumpPostsDB()
    
    total_posts = db.get_posts_count()
    latest_post_id = db.get_latest_post_id()
    
    # 获取最近7天的数据统计
    et_tz = pytz.timezone(TIMEZONE)
    today = datetime.now(et_tz)
    
    print("=" * 60)
    print("Trump Truth Social 爬虫状态报告")
    print("=" * 60)
    print(f"数据库总帖子数: {total_posts:,}")
    print(f"最新帖子ID: {latest_post_id or '无'}")
    print(f"报告生成时间: {today.strftime('%Y-%m-%d %H:%M:%S')} (ET)")
    print()
    
    # 最近7天的数据分布
    print("最近7天数据分布:")
    print("-" * 30)
    
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        posts = db.get_posts_by_date(date)
        
        if posts:
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_reposts = sum(post.get('reposts_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) for post in posts)
            
            print(f"{date}: {len(posts):2d} 帖子 | "
                  f"赞 {total_likes:,} | "
                  f"转 {total_reposts:,} | "
                  f"评 {total_comments:,}")
        else:
            print(f"{date}: 无数据")
    
    print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Trump Truth Social 爬虫程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试运行一次爬取'
    )
    
    parser.add_argument(
        '--historical',
        type=int,
        metavar='DAYS',
        help='爬取过去N天的历史数据'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='显示数据库状态'
    )
    
    parser.add_argument(
        '--no-historical',
        action='store_true',
        help='启动定时爬虫时不执行历史数据爬取'
    )
    
    parser.add_argument(
        '--summary',
        type=str,
        metavar='DATE',
        help='生成指定日期的小结 (格式: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='导出待处理日期的Claude分析文件'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 初始化logger
    global logger
    logger = logging.getLogger(__name__)
    
    try:
        # 检查系统要求
        check_system_requirements()
        
        # 根据参数执行不同功能
        if args.status:
            show_status()
            
        elif args.test:
            test_scrape()
            
        elif args.historical:
            if args.historical <= 0:
                logger.error("历史数据天数必须大于0")
                sys.exit(1)
            historical_scrape(args.historical)
            
        elif args.summary:
            generate_summary(args.summary)
            
        elif args.export:
            export_for_claude()
            
        else:
            # 默认启动定时爬虫
            logger.info("启动Trump Truth Social定时爬虫...")
            
            scheduler = TrumpScraperScheduler()
            run_historical = not args.no_historical
            
            scheduler.start(run_historical=run_historical, days_back=30)
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 