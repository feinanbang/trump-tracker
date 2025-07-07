import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pytz
from config import DATABASE_PATH, TIMEZONE

logger = logging.getLogger(__name__)


class TrumpPostsDB:
    """Trump帖子数据库管理类"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建帖子表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trump_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id TEXT UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        post_date TEXT NOT NULL,
                        post_time TEXT NOT NULL,
                        timestamp_utc TEXT NOT NULL,
                        timestamp_et TEXT NOT NULL,
                        likes_count INTEGER DEFAULT 0,
                        reposts_count INTEGER DEFAULT 0,
                        comments_count INTEGER DEFAULT 0,
                        media_urls TEXT,
                        post_url TEXT,
                        scraped_at TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建每日小结表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        summary_date TEXT UNIQUE NOT NULL,
                        summary_content TEXT NOT NULL,
                        post_count INTEGER DEFAULT 0,
                        total_likes INTEGER DEFAULT 0,
                        total_reposts INTEGER DEFAULT 0,
                        total_comments INTEGER DEFAULT 0,
                        generated_by TEXT DEFAULT 'AI',
                        generated_at TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建帖子表索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_post_date 
                    ON trump_posts(post_date)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_post_id 
                    ON trump_posts(post_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_scraped_at 
                    ON trump_posts(scraped_at)
                ''')
                
                # 创建小结表索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_summary_date 
                    ON daily_summaries(summary_date)
                ''')
                
                conn.commit()
                logger.info("数据库初始化成功")
                
        except sqlite3.Error as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def insert_post(self, post_data: Dict) -> bool:
        """插入新帖子数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 转换时间戳
                et_tz = pytz.timezone(TIMEZONE)
                scraped_at = datetime.now(et_tz).isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO trump_posts 
                    (post_id, content, post_date, post_time, timestamp_utc, 
                     timestamp_et, likes_count, reposts_count, comments_count, 
                     media_urls, post_url, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data.get('post_id'),
                    post_data.get('content'),
                    post_data.get('post_date'),
                    post_data.get('post_time'),
                    post_data.get('timestamp_utc'),
                    post_data.get('timestamp_et'),
                    post_data.get('likes_count', 0),
                    post_data.get('reposts_count', 0),
                    post_data.get('comments_count', 0),
                    post_data.get('media_urls'),
                    post_data.get('post_url'),
                    scraped_at
                ))
                
                conn.commit()
                logger.info(f"成功插入帖子: {post_data.get('post_id')}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"插入帖子失败: {e}")
            return False
    
    def insert_daily_summary(self, summary_data: Dict) -> bool:
        """插入每日小结数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                et_tz = pytz.timezone(TIMEZONE)
                generated_at = datetime.now(et_tz).isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_summaries 
                    (summary_date, summary_content, post_count, total_likes,
                     total_reposts, total_comments, generated_by, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    summary_data.get('summary_date'),
                    summary_data.get('summary_content'),
                    summary_data.get('post_count', 0),
                    summary_data.get('total_likes', 0),
                    summary_data.get('total_reposts', 0),
                    summary_data.get('total_comments', 0),
                    summary_data.get('generated_by', 'AI'),
                    generated_at
                ))
                
                conn.commit()
                logger.info(f"成功插入小结: {summary_data.get('summary_date')}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"插入小结失败: {e}")
            return False
    
    def get_posts_by_date(self, date: str) -> List[Dict]:
        """按日期获取帖子"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM trump_posts 
                    WHERE post_date = ? 
                    ORDER BY timestamp_et DESC
                ''', (date,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"查询帖子失败: {e}")
            return []
    
    def get_summary_by_date(self, date: str) -> Optional[Dict]:
        """按日期获取小结"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM daily_summaries 
                    WHERE summary_date = ?
                ''', (date,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except sqlite3.Error as e:
            logger.error(f"查询小结失败: {e}")
            return None
    
    def get_recent_summaries(self, days: int = 7) -> List[Dict]:
        """获取最近几天的小结"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM daily_summaries 
                    ORDER BY summary_date DESC 
                    LIMIT ?
                ''', (days,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"查询最近小结失败: {e}")
            return []
    
    def summary_exists(self, date: str) -> bool:
        """检查小结是否已存在"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 1 FROM daily_summaries WHERE summary_date = ?
                ''', (date,))
                
                return cursor.fetchone() is not None
                
        except sqlite3.Error as e:
            logger.error(f"检查小结存在性失败: {e}")
            return False
    
    def get_latest_post_id(self) -> Optional[str]:
        """获取最新帖子ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT post_id FROM trump_posts 
                    ORDER BY timestamp_et DESC 
                    LIMIT 1
                ''')
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except sqlite3.Error as e:
            logger.error(f"获取最新帖子ID失败: {e}")
            return None
    
    def get_posts_count(self) -> int:
        """获取帖子总数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM trump_posts')
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except sqlite3.Error as e:
            logger.error(f"获取帖子数量失败: {e}")
            return 0
    
    def get_summaries_count(self) -> int:
        """获取小结总数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM daily_summaries')
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except sqlite3.Error as e:
            logger.error(f"获取小结数量失败: {e}")
            return 0
    
    def post_exists(self, post_id: str) -> bool:
        """检查帖子是否已存在"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 1 FROM trump_posts WHERE post_id = ?
                ''', (post_id,))
                
                return cursor.fetchone() is not None
                
        except sqlite3.Error as e:
            logger.error(f"检查帖子存在性失败: {e}")
            return False 