#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os

def create_sample_database():
    """创建包含示例数据的数据库"""
    
    # 创建数据库连接
    conn = sqlite3.connect('trump_posts.db')
    cursor = conn.cursor()
    
    # 创建posts表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        display_name TEXT NOT NULL,
        content TEXT NOT NULL,
        engagement_text TEXT,
        timestamp_text TEXT,
        formatted_time TEXT,
        profile_image_url TEXT,
        verified BOOLEAN DEFAULT 0,
        post_url TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scraped_date TEXT NOT NULL,
        data_id TEXT
    )
    ''')
    
    # 创建daily_summaries表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL,
        summary TEXT NOT NULL,
        post_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 插入示例帖子数据
    cursor.execute('''
    INSERT OR REPLACE INTO posts (
        post_id, username, display_name, content, engagement_text, 
        timestamp_text, formatted_time, profile_image_url, verified, 
        post_url, scraped_date, data_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'example_1', 'realDonaldTrump', 'Donald J. Trump', 
        'HAPPY INDEPENDENCE DAY! Today we celebrate the signing of the Declaration of Independence and the birth of our great Nation!', 
        '12.5K Likes, 3.2K Reposts', 'Jul 04, 2025, 12:00 PM', '2025-07-04 12:00', 
        'https://example.com/profile.jpg', 1, 
        'https://truthsocial.com/@realDonaldTrump/posts/example_1', '2025-07-04', 'example_1'
    ))
    
    cursor.execute('''
    INSERT OR REPLACE INTO posts (
        post_id, username, display_name, content, engagement_text, 
        timestamp_text, formatted_time, profile_image_url, verified, 
        post_url, scraped_date, data_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'example_2', 'realDonaldTrump', 'Donald J. Trump', 
        'The ONE BIG BEAUTIFUL BILL ACT has passed! This will streamline our government and make America more efficient than ever before!', 
        '15.8K Likes, 4.1K Reposts', 'Jul 04, 2025, 2:30 PM', '2025-07-04 14:30', 
        'https://example.com/profile.jpg', 1, 
        'https://truthsocial.com/@realDonaldTrump/posts/example_2', '2025-07-04', 'example_2'
    ))
    
    # 插入示例分析
    summary_text = """## 🎆 2025年7月4日 Trump Truth Social活动分析

### 📊 核心数据
- **帖子总数**: 33条
- **主要主题**: 独立日庆祝、政策成就宣布  
- **情绪基调**: 庆祝与自豪并重

### 🎯 重点内容分析

#### 1. 独立日庆祝主题
Trump在独立日发布了多条庆祝美国独立的帖子，强调爱国主义和美国价值观。这些帖子获得了极高的互动率。

#### 2. "ONE BIG BEAUTIFUL BILL ACT"政策宣布  
Trump宣布了一项重要的政府效率法案通过，声称这将使政府更加精简高效。这是当日的重磅政治新闻。

#### 3. 传统价值观强调
在独立日这个特殊日子，Trump多次强调传统美国价值观，包括自由、民主和爱国精神。

### 📈 传播效果
从互动数据看，独立日相关内容获得了显著更高的参与度，体现了节日话题的传播优势。

### 🔗 原文链接
- [独立日庆祝帖](https://truthsocial.com/@realDonaldTrump/posts/example_1)  
- [政策法案宣布](https://truthsocial.com/@realDonaldTrump/posts/example_2)"""
    
    cursor.execute('''
    INSERT OR REPLACE INTO daily_summaries (date, summary, post_count) VALUES (?, ?, ?)
    ''', ('2025-07-04', summary_text, 33))
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("✅ 示例数据库创建成功！")
    print("📊 包含2条示例帖子和1个分析报告")

if __name__ == '__main__':
    create_sample_database() 