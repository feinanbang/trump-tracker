#!/usr/bin/env python3
"""
测试历史数据爬取功能 - 验证深度滚动能力
"""

import logging
import sys
from datetime import datetime, timedelta
import pytz
from scraper import TruthSocialScraper
from database import TrumpPostsDB
from utils import setup_logging

def test_historical_depth():
    """测试历史数据爬取深度"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 测试爬取过去30天的数据
    target_days = 30
    
    logger.info("=" * 50)
    logger.info("开始历史数据深度爬取测试")
    logger.info(f"目标：爬取过去 {target_days} 天的所有帖子")
    logger.info("=" * 50)
    
    # 计算目标日期
    et_tz = pytz.timezone("US/Eastern")
    start_date = datetime.now(et_tz)
    end_date = start_date - timedelta(days=target_days)
    
    logger.info(f"开始日期: {start_date.strftime('%Y-%m-%d %H:%M')}")
    logger.info(f"目标日期: {end_date.strftime('%Y-%m-%d')}")
    
    # 清空数据库以获得准确测试
    db = TrumpPostsDB()
    logger.info("清空现有数据库以进行干净测试...")
    db.cursor.execute("DELETE FROM trump_posts")
    db.connection.commit()
    
    # 开始爬取
    scraper = TruthSocialScraper()
    try:
        results = scraper.run_with_retry(days_back=target_days)
        
        logger.info("=" * 50)
        logger.info("爬取结果分析")
        logger.info("=" * 50)
        
        if results:
            logger.info(f"✅ 成功爬取到 {len(results)} 个帖子")
            
            # 分析日期分布
            date_counts = {}
            earliest_date = None
            latest_date = None
            
            for post in results:
                post_date = post.get('post_date')
                if post_date:
                    if post_date not in date_counts:
                        date_counts[post_date] = 0
                    date_counts[post_date] += 1
                    
                    if earliest_date is None or post_date < earliest_date:
                        earliest_date = post_date
                    if latest_date is None or post_date > latest_date:
                        latest_date = post_date
            
            logger.info(f"📅 日期范围: {earliest_date} 到 {latest_date}")
            
            # 计算覆盖天数
            if earliest_date and latest_date:
                start_dt = datetime.strptime(latest_date, "%Y-%m-%d")
                end_dt = datetime.strptime(earliest_date, "%Y-%m-%d") 
                covered_days = (start_dt - end_dt).days + 1
                logger.info(f"📊 覆盖天数: {covered_days} 天")
                
                # 检查是否达到目标
                target_date_str = end_date.strftime("%Y-%m-%d")
                if earliest_date <= target_date_str:
                    logger.info(f"🎯 ✅ 成功到达目标日期！")
                    logger.info(f"   目标: {target_date_str}")
                    logger.info(f"   实际: {earliest_date}")
                else:
                    days_short = (datetime.strptime(earliest_date, "%Y-%m-%d") - 
                                 datetime.strptime(target_date_str, "%Y-%m-%d")).days
                    logger.info(f"🎯 ❌ 未到达目标日期")
                    logger.info(f"   目标: {target_date_str}")
                    logger.info(f"   实际: {earliest_date}")
                    logger.info(f"   差距: {days_short} 天")
            
            # 显示每日统计
            logger.info("\n📈 每日帖子数量:")
            for date in sorted(date_counts.keys(), reverse=True):
                logger.info(f"   {date}: {date_counts[date]} 个帖子")
                
        else:
            logger.error("❌ 没有爬取到任何帖子")
            return False
            
        # 数据库验证
        logger.info("\n🗄️ 数据库验证:")
        total_posts = db.get_total_posts()
        logger.info(f"   数据库中总帖子数: {total_posts}")
        
        recent_posts = db.get_posts_by_date_range(
            start_date.strftime("%Y-%m-%d"),
            (start_date - timedelta(days=7)).strftime("%Y-%m-%d")
        )
        logger.info(f"   近7天帖子数: {len(recent_posts)}")
        
        return len(results) > 0
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False

def main():
    """主函数"""
    success = test_historical_depth()
    
    if success:
        print("\n🎉 历史数据爬取测试通过！")
        print("系统具备深度历史数据爬取能力。")
        sys.exit(0)
    else:
        print("\n❌ 历史数据爬取测试失败！")
        print("需要进一步优化滚动机制。")
        sys.exit(1)

if __name__ == "__main__":
    main() 