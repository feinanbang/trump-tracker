#!/usr/bin/env python3
"""
调试Truth Social滚动和帖子加载行为
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_truth_social_loading():
    """调试Truth Social的加载行为"""
    
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 禁用图片加载以提高速度
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = None
    try:
        logger.info("启动Chrome浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 设置超时
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(15)
        
        logger.info("访问Trump的Truth Social页面...")
        driver.get("https://truthsocial.com/@realDonaldTrump")
        
        # 等待页面初始加载
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".status"))
        )
        
        logger.info("页面初始加载完成，开始详细分析...")
        
        # 详细滚动调试
        for scroll_round in range(15):  # 增加滚动次数
            logger.info(f"\n=== 滚动轮次 {scroll_round + 1} ===")
            
            # 获取当前所有帖子
            posts = driver.find_elements(By.CSS_SELECTOR, ".status")
            logger.info(f"当前帖子数量: {len(posts)}")
            
            # 显示前几个帖子的时间信息
            for i, post in enumerate(posts[:5]):
                try:
                    time_element = post.find_element(By.CSS_SELECTOR, "time")
                    title_time = time_element.get_attribute("title")
                    relative_time = time_element.text
                    logger.info(f"  帖子 {i+1}: {relative_time} ({title_time})")
                except Exception as e:
                    logger.info(f"  帖子 {i+1}: 无法获取时间信息")
            
            # 检查页面位置
            current_scroll = driver.execute_script("return window.pageYOffset")
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            logger.info(f"滚动位置: {current_scroll}, 页面高度: {page_height}, 视口高度: {viewport_height}")
            
            # 渐进式滚动
            scroll_distance = viewport_height * 0.5  # 每次滚动50%视口高度
            new_position = current_scroll + scroll_distance
            
            logger.info(f"滚动到位置: {new_position}")
            driver.execute_script(f"window.scrollTo(0, {new_position});")
            
            # 等待更长时间让内容加载
            logger.info("等待内容加载...")
            time.sleep(4)  # 增加等待时间
            
            # 检查是否有新帖子加载
            new_posts = driver.find_elements(By.CSS_SELECTOR, ".status")
            if len(new_posts) > len(posts):
                logger.info(f"✅ 新加载了 {len(new_posts) - len(posts)} 个帖子")
            else:
                logger.info("❌ 没有新帖子加载")
            
            # 检查是否到达底部
            current_scroll_after = driver.execute_script("return window.pageYOffset")
            page_height_after = driver.execute_script("return document.body.scrollHeight")
            
            if current_scroll_after + viewport_height >= page_height_after - 50:
                logger.info("⚠️ 可能已到达页面底部")
                # 等待更长时间看是否有延迟加载
                time.sleep(6)
                final_posts = driver.find_elements(By.CSS_SELECTOR, ".status")
                if len(final_posts) == len(new_posts):
                    logger.info("🛑 确认已到达底部，停止滚动")
                    break
                else:
                    logger.info(f"🔄 延迟加载了 {len(final_posts) - len(new_posts)} 个帖子")
        
        # 最终统计
        final_posts = driver.find_elements(By.CSS_SELECTOR, ".status")
        logger.info(f"\n=== 最终结果 ===")
        logger.info(f"总共找到 {len(final_posts)} 个帖子")
        
        # 显示所有帖子的时间
        logger.info("\n所有帖子时间列表:")
        for i, post in enumerate(final_posts):
            try:
                time_element = post.find_element(By.CSS_SELECTOR, "time")
                title_time = time_element.get_attribute("title")
                relative_time = time_element.text
                logger.info(f"  {i+1}. {relative_time} ({title_time})")
            except Exception:
                logger.info(f"  {i+1}. 无法获取时间信息")
        
        return True
        
    except Exception as e:
        logger.error(f"调试失败: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            logger.info("浏览器已关闭")

if __name__ == "__main__":
    logger.info("开始Truth Social滚动调试...")
    debug_truth_social_loading() 