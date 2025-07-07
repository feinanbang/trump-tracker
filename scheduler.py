import logging
import signal
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from config import TIMEZONE, SCHEDULE_MINUTE
from scraper import TruthSocialScraper
from daily_export import DailyExporter
from utils import setup_logging

logger = logging.getLogger(__name__)


class TrumpScraperScheduler:
    """Trump帖子爬虫调度器"""
    
    def __init__(self):
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(TIMEZONE))
        self.scraper = TruthSocialScraper()
        self.exporter = DailyExporter()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """设置信号处理器，用于优雅关闭"""
        def signal_handler(signum, frame):
            logger.info("接收到关闭信号，正在停止调度器...")
            self.scheduler.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def scrape_job(self):
        """定时爬取任务"""
        try:
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            logger.info(f"开始执行定时爬取任务 - {current_time}")
            
            # 执行爬取
            results = self.scraper.run_with_retry()
            
            if results:
                logger.info(f"定时爬取完成，获取 {len(results)} 个新帖子")
            else:
                logger.info("定时爬取完成，没有新帖子")
            
            # 如果有新数据，检查是否需要导出
            self.check_and_export_daily()
            
        except Exception as e:
            logger.error(f"定时爬取任务失败: {e}")
    
    def check_and_export_daily(self):
        """检查并导出需要生成小结的日期"""
        try:
            pending_dates = self.exporter.check_pending_dates()
            if pending_dates:
                logger.info(f"发现 {len(pending_dates)} 个日期需要导出Claude分析文件")
                for date in pending_dates:
                    files = self.exporter.save_daily_export(date, ['md'])
                    if files:
                        logger.info(f"已导出 {date}: {files[0]}")
        except Exception as e:
            logger.error(f"导出检查失败: {e}")
    
    def historical_scrape_job(self, days_back: int = 30):
        """历史数据爬取任务"""
        try:
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            logger.info(f"开始执行历史数据爬取任务 - {current_time}")
            logger.info(f"爬取过去 {days_back} 天的数据")
            
            # 执行历史数据爬取
            results = self.scraper.run_with_retry(days_back=days_back)
            
            if results:
                logger.info(f"历史数据爬取完成，获取 {len(results)} 个帖子")
            else:
                logger.info("历史数据爬取完成，没有新帖子")
            
        except Exception as e:
            logger.error(f"历史数据爬取任务失败: {e}")
    
    def add_hourly_job(self):
        """添加每小时执行的爬取任务"""
        self.scheduler.add_job(
            func=self.scrape_job,
            trigger=CronTrigger(minute=SCHEDULE_MINUTE),
            id='hourly_scrape',
            name='每小时爬取Trump帖子',
            replace_existing=True
        )
        logger.info(f"已添加每小时爬取任务，将在每小时的第 {SCHEDULE_MINUTE} 分钟执行")
    
    def add_historical_job(self, days_back: int = 30):
        """添加一次性历史数据爬取任务"""
        self.scheduler.add_job(
            func=lambda: self.historical_scrape_job(days_back),
            trigger='date',
            run_date=datetime.now(pytz.timezone(TIMEZONE)),
            id='historical_scrape',
            name=f'爬取过去{days_back}天的历史数据',
            replace_existing=True
        )
        logger.info(f"已添加历史数据爬取任务，将立即执行")
    
    def start(self, run_historical: bool = True, days_back: int = 30):
        """启动调度器"""
        try:
            logger.info("启动Trump帖子爬虫调度器")
            
            # 添加定时任务
            self.add_hourly_job()
            
            # 如果需要，添加历史数据爬取任务
            if run_historical:
                self.add_historical_job(days_back)
            
            # 显示已添加的任务
            jobs = self.scheduler.get_jobs()
            logger.info(f"已添加 {len(jobs)} 个任务:")
            for job in jobs:
                logger.info(f"  - {job.name} (ID: {job.id})")
            
            # 启动调度器
            logger.info("调度器已启动，按 Ctrl+C 停止")
            self.scheduler.start()
            
        except KeyboardInterrupt:
            logger.info("用户中断，停止调度器")
        except Exception as e:
            logger.error(f"调度器启动失败: {e}")
            raise
    
    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"停止调度器失败: {e}")


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建并启动调度器
    scheduler = TrumpScraperScheduler()
    
    try:
        # 启动调度器，包含历史数据爬取
        scheduler.start(run_historical=True, days_back=30)
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 