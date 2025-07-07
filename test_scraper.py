#!/usr/bin/env python3
"""
Truth Social 访问测试脚本
用于调试网站访问和内容提取问题
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_truth_social_access():
    """测试Truth Social网站访问"""
    
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
        
        logger.info("访问Truth Social主页...")
        driver.get("https://truthsocial.com/")
        
        # 等待页面加载
        time.sleep(5)
        
        logger.info("获取页面标题...")
        title = driver.title
        logger.info(f"页面标题: {title}")
        
        logger.info("获取页面源码长度...")
        page_source_length = len(driver.page_source)
        logger.info(f"页面源码长度: {page_source_length} 字符")
        
        # 尝试访问Trump的页面
        logger.info("访问Trump的Truth Social页面...")
        driver.get("https://truthsocial.com/@realDonaldTrump")
        
        # 等待页面加载
        time.sleep(10)
        
        logger.info("获取Trump页面标题...")
        trump_title = driver.title
        logger.info(f"Trump页面标题: {trump_title}")
        
        logger.info("获取Trump页面源码长度...")
        trump_page_length = len(driver.page_source)
        logger.info(f"Trump页面源码长度: {trump_page_length} 字符")
        
        # 尝试查找帖子元素
        logger.info("查找帖子元素...")
        try:
            # 等待帖子元素出现
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .post, [data-testid='post'], .status"))
            )
            
            # 查找各种可能的帖子选择器
            selectors = [
                "article",
                ".post",
                "[data-testid='post']",
                ".status",
                ".timeline-item",
                ".feed-item"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"找到 {len(elements)} 个元素使用选择器: {selector}")
                    
                    # 显示前几个元素的文本内容
                    for i, element in enumerate(elements[:3]):
                        try:
                            text = element.text.strip()[:200]  # 只显示前200个字符
                            logger.info(f"元素 {i+1} 文本: {text}")
                        except Exception as e:
                            logger.warning(f"无法获取元素 {i+1} 的文本: {e}")
                    break
            else:
                logger.warning("未找到任何帖子元素")
                
        except TimeoutException:
            logger.error("等待帖子元素超时")
            
        # 保存页面源码用于调试
        with open("trump_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("页面源码已保存到 trump_page_source.html")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            logger.info("浏览器已关闭")

if __name__ == "__main__":
    logger.info("开始Truth Social访问测试...")
    success = test_truth_social_access()
    
    if success:
        logger.info("测试完成")
    else:
        logger.error("测试失败") 