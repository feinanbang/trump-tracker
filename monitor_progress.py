#!/usr/bin/env python3
"""
实时监控Trump爬虫进度
"""
import time
import os
import sys
from datetime import datetime

def monitor_log_file(log_file="trump_scraper.log"):
    """监控日志文件，显示实时进度"""
    print("🔍 Trump爬虫进度监控器")
    print("=" * 50)
    print("💡 此工具将实时显示爬虫运行状态")
    print("💡 请在另一个终端运行爬虫程序")
    print("💡 按 Ctrl+C 退出监控")
    print("=" * 50)
    
    if not os.path.exists(log_file):
        print(f"❌ 日志文件不存在: {log_file}")
        print("💡 请先运行爬虫程序")
        return
    
    # 获取文件初始大小
    last_size = os.path.getsize(log_file)
    
    print(f"📁 监控日志文件: {log_file}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print("\n🔄 等待爬虫活动...")
    
    try:
        while True:
            current_size = os.path.getsize(log_file)
            
            if current_size > last_size:
                # 文件有新内容
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                
                for line in new_lines:
                    line = line.strip()
                    if line:
                        # 解析关键信息
                        if "滚动轮次" in line:
                            print(f"🔄 {line.split(' - ')[-1]}")
                        elif "成功处理帖子" in line:
                            print(f"✨ {line.split(' - ')[-1]}")
                        elif "爬取完成" in line:
                            print(f"🎉 {line.split(' - ')[-1]}")
                        elif "ERROR" in line:
                            print(f"❌ {line.split(' - ')[-1]}")
                        elif "访问" in line and "truthsocial" in line:
                            print(f"🌐 {line.split(' - ')[-1]}")
                        elif "Chrome浏览器驱动设置成功" in line:
                            print("✅ 浏览器启动成功")
                        elif "开始深度滚动爬取" in line:
                            print("🚀 开始深度爬取...")
                
                last_size = current_size
            
            time.sleep(1)  # 每秒检查一次
            
    except KeyboardInterrupt:
        print(f"\n⏹️ 监控已停止")
        print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")

def show_latest_progress():
    """显示最近的进度信息"""
    log_file = "trump_scraper.log"
    
    if not os.path.exists(log_file):
        print("❌ 日志文件不存在，爬虫可能还未运行")
        return
    
    print("📊 最近的爬虫活动:")
    print("=" * 40)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 显示最后20行的关键信息
        recent_lines = lines[-20:] if len(lines) > 20 else lines
        
        for line in recent_lines:
            line = line.strip()
            if any(keyword in line for keyword in 
                   ["滚动轮次", "成功处理帖子", "爬取完成", "访问", "Chrome"]):
                timestamp = line.split(' - ')[0] if ' - ' in line else ""
                message = line.split(' - ')[-1] if ' - ' in line else line
                print(f"{timestamp}: {message}")
                
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--latest":
        show_latest_progress()
    else:
        monitor_log_file() 