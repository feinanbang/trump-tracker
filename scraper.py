import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException
)
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import random

from config import (
    TRUTH_SOCIAL_URL, BROWSER_OPTIONS, SCROLL_PAUSE_TIME,
    MAX_SCROLL_ATTEMPTS, MAX_NO_NEW_POSTS, TIMEZONE, MAX_RETRIES, RETRY_DELAY, USER_AGENT
)
from database import TrumpPostsDB
from utils import setup_logging

logger = setup_logging()


class TruthSocialScraper:
    """Truth Social Trump帖子爬虫"""
    
    def __init__(self):
        self.db = TrumpPostsDB()
        self.driver = None
        self.et_tz = pytz.timezone(TIMEZONE)
    
    def human_like_scroll(self, pause_range=(3, 6)):
        """模拟人类滚动行为 - 匿名访问优化版"""
        # 随机滚动距离（较小，模拟真实阅读）
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_distance = random.randint(
            int(viewport_height * 0.2), 
            int(viewport_height * 0.5)
        )
        
        # 获取当前位置
        current_pos = self.driver.execute_script("return window.pageYOffset")
        
        # 分步滚动，模拟人类行为
        steps = random.randint(2, 4)
        for i in range(steps):
            intermediate_pos = current_pos + (scroll_distance * (i + 1) / steps)
            self.driver.execute_script(f"window.scrollTo(0, {intermediate_pos});")
            time.sleep(random.uniform(0.2, 0.5))  # 短暂停顿
        
        # 随机停顿，模拟阅读
        pause_time = random.uniform(pause_range[0], pause_range[1])
        time.sleep(pause_time)
        
        return current_pos + scroll_distance
    
    def setup_driver(self):
        """设置浏览器驱动 - 增强反检测版本"""
        try:
            chrome_options = Options()
            
            # 基础无头设置
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 反检测增强选项
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 模拟真实用户代理
            chrome_options.add_argument(f"--user-agent={USER_AGENT}")
            
            # 禁用一些可能暴露自动化的功能
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # 加速加载
            
            try:
                # 尝试自动下载ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("自动下载ChromeDriver成功")
            except Exception as e:
                logger.warning(f"自动下载ChromeDriver失败: {e}")
                logger.info("尝试使用系统Chrome...")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # 设置超时
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(15)
            
            # 反检测脚本
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("Chrome浏览器驱动设置成功（匿名访问 + 反检测）")
            
        except Exception as e:
            logger.error(f"设置浏览器驱动失败: {e}")
            raise
    
    def close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器驱动失败: {e}")
    
    def scroll_and_scrape_posts(
            self, target_date: Optional[str] = None
    ) -> List[Dict]:
        """边滚动边处理帖子，人性化匿名访问版本"""
        scraped_posts = []
        processed_post_ids = set()
        scroll_attempts = 0
        no_new_posts_count = 0
        earliest_date_found = None
        target_reached = False
        
        logger.info(f"开始人性化匿名爬取，目标日期: {target_date}")
        
        # 添加实时进度显示
        print(f"\n🚀 开始人性化匿名爬取 Truth Social 帖子...")
        if target_date:
            print(f"📅 目标日期: {target_date}")
            print(f"🎯 停止条件: 找到 {target_date} 或更早的帖子")
        print(f"🐌 使用慢速人性化滚动（匿名访问）")
        print(f"🔄 最大滚动轮次: {MAX_SCROLL_ATTEMPTS} 次")
        print("=" * 60)
        
        try:
            while scroll_attempts < MAX_SCROLL_ATTEMPTS:
                # 获取当前页面上的所有帖子
                current_posts = self.driver.find_elements(
                    By.CSS_SELECTOR, ".status"
                )
                current_post_count = len(current_posts)
                
                # 实时显示进度
                progress_percent = (scroll_attempts + 1) / MAX_SCROLL_ATTEMPTS * 100
                earliest_info = f"最早: {earliest_date_found}" if earliest_date_found else "最早: 未知"
                print(f"\r📊 进度: [{scroll_attempts+1:2d}/{MAX_SCROLL_ATTEMPTS}] "
                      f"({progress_percent:5.1f}%) | "
                      f"页面帖子: {current_post_count:2d} | "
                      f"已处理: {len(processed_post_ids):2d} | "
                      f"新增: {len(scraped_posts):2d} | {earliest_info}", end="", flush=True)
                
                logger.info(
                    f"人性化滚动轮次 {scroll_attempts + 1}: "
                    f"当前页面帖子数量: {current_post_count}"
                )
                
                # 处理当前页面上的每个帖子
                new_posts_found = 0
                oldest_post_date_this_round = None
                
                for post_element in current_posts:
                    try:
                        # 先尝试获取帖子ID来避免重复处理
                        try:
                            wrapper = post_element.find_element(
                                By.CSS_SELECTOR, ".status__wrapper"
                            )
                            post_id = wrapper.get_attribute("data-id")
                        except NoSuchElementException:
                            # 如果无法获取ID，跳过这个帖子
                            continue
                        
                        # 如果已经处理过这个帖子，跳过
                        if post_id in processed_post_ids:
                            continue
                        
                        # 检查数据库中是否已存在
                        if self.db.post_exists(post_id):
                            processed_post_ids.add(post_id)
                            logger.info(f"帖子已存在，跳过: {post_id}")
                            continue
                        
                        # 提取帖子数据
                        post_data = self.extract_post_data(post_element)
                        
                        if post_data and post_data.get('post_date'):
                            post_date = post_data['post_date']
                            
                            # 更新最早发现的日期
                            if (oldest_post_date_this_round is None or 
                                    post_date < oldest_post_date_this_round):
                                oldest_post_date_this_round = post_date
                            
                            if (earliest_date_found is None or 
                                    post_date < earliest_date_found):
                                earliest_date_found = post_date
                            
                            # 检查是否到达目标日期
                            if target_date and post_date <= target_date:
                                target_reached = True
                                print(f"\n🎯 找到目标日期帖子！日期: {post_date}")
                                logger.info(f"找到目标日期帖子: {post_date} <= {target_date}")
                            
                            # 保存到数据库
                            if self.db.insert_post(post_data):
                                scraped_posts.append(post_data)
                                processed_post_ids.add(post_id)
                                new_posts_found += 1
                                logger.info(
                                    f"成功处理帖子: {post_id} (日期: {post_date})"
                                )
                                
                                # 实时显示新帖子
                                earliest_info = f"最早: {earliest_date_found}" if earliest_date_found else "最早: 未知"
                                print(f"\r📊 进度: [{scroll_attempts+1:2d}/{MAX_SCROLL_ATTEMPTS}] "
                                      f"({progress_percent:5.1f}%) | "
                                      f"页面帖子: {current_post_count:2d} | "
                                      f"已处理: {len(processed_post_ids):2d} | "
                                      f"新增: {len(scraped_posts):2d} ✨ | {earliest_info}", end="", flush=True)
                            else:
                                logger.error(f"保存帖子失败: {post_id}")
                        
                    except Exception as e:
                        logger.error(f"处理帖子时出错: {e}")
                        continue
                
                logger.info(
                    f"本轮处理了 {new_posts_found} 个新帖子，"
                    f"最老帖子日期: {oldest_post_date_this_round}, "
                    f"全局最早日期: {earliest_date_found}"
                )
                
                # 优化的停止条件：基于日期目标
                if target_date and target_reached:
                    # 已经找到目标日期的帖子，但再滚动几轮确保完整性
                    print(f"\n✅ 已找到目标日期 {target_date} 的帖子，再滚动几轮确保完整性...")
                    
                    # 检查是否还有更早的帖子
                    additional_rounds = 3  # 减少额外滚动轮次
                    if scroll_attempts >= MAX_SCROLL_ATTEMPTS - additional_rounds:
                        print(f"🎯 目标已达成，停止爬取")
                        logger.info(f"已到达目标日期: {target_date} (当前最早: {earliest_date_found})")
                        break
                
                # 执行人性化滚动
                current_height = self.human_like_scroll(pause_range=(4, 8))
                
                # 检查页面变化和停止条件
                updated_posts = self.driver.find_elements(By.CSS_SELECTOR, ".status")
                updated_post_count = len(updated_posts)
                
                # 基于新帖子数量的停止检查
                if not target_reached:
                    if (new_posts_found == 0 and updated_post_count == current_post_count):
                        no_new_posts_count += 1
                        logger.info(f"没有新帖子，连续 {no_new_posts_count} 次")
                    else:
                        no_new_posts_count = 0
                    
                    # 匿名访问的温和停止策略
                    if no_new_posts_count >= MAX_NO_NEW_POSTS:
                        if not target_date:
                            print(f"\n⚠️ 连续 {MAX_NO_NEW_POSTS} 次没有新帖子，停止爬取")
                            logger.info("连续多次没有新帖子，停止滚动")
                            break
                        else:
                            print(f"\n⚠️ 连续 {MAX_NO_NEW_POSTS} 次没有新帖子，但未达到目标日期 {target_date}")
                            print(f"🔍 当前最早日期: {earliest_date_found}")
                            
                            # 执行最后尝试，但更温和
                            logger.info("执行最后的温和滚动尝试...")
                            self.human_like_scroll(pause_range=(6, 12))
                            
                            final_posts = self.driver.find_elements(By.CSS_SELECTOR, ".status")
                            if len(final_posts) == updated_post_count:
                                print("❌ 确认已到达匿名访问的数据边界")
                                logger.info("已到达匿名访问的数据边界")
                                break
                            else:
                                new_count = len(final_posts) - updated_post_count
                                print(f"🎉 温和滚动后发现 {new_count} 个新帖子，继续爬取")
                                no_new_posts_count = 0
                
                scroll_attempts += 1
                logger.info(f"人性化滚动进度: {scroll_attempts}/{MAX_SCROLL_ATTEMPTS}")
                
                # 每5轮输出一次统计信息（减少频率）
                if scroll_attempts % 5 == 0:
                    status = "🎯 已达成" if target_reached else "🔍 搜索中"
                    print(f"\n📈 阶段总结 - 第 {scroll_attempts} 轮:")
                    print(f"   🎯 已处理帖子: {len(processed_post_ids)} 个")
                    print(f"   ✨ 新增帖子: {len(scraped_posts)} 个")
                    print(f"   📅 最早帖子日期: {earliest_date_found or '未知'}")
                    if target_date:
                        print(f"   🎯 目标日期: {target_date} ({status})")
                    print("=" * 60)
                    
                    # 模拟用户休息
                    if scroll_attempts % 10 == 0:
                        print("💭 模拟用户休息时间...")
                        time.sleep(random.uniform(8, 15))
            
            # 最终结果显示
            print(f"\n🎉 人性化匿名爬取完成！")
            print(f"📊 最终统计:")
            print(f"   🎯 共处理 {len(processed_post_ids)} 个帖子")
            print(f"   ✨ 新增 {len(scraped_posts)} 个帖子")
            print(f"   📅 最早帖子日期: {earliest_date_found or '未知'}")
            if target_date:
                if target_reached:
                    print(f"   🎯 目标日期 {target_date}: ✅ 已达成")
                else:
                    print(f"   🎯 目标日期 {target_date}: ❌ 未达成")
                    print(f"   💡 建议: 匿名访问的数据深度限制约为4天")
            print("=" * 60)
            
            logger.info(
                f"人性化匿名爬取完成，共处理 {len(processed_post_ids)} 个帖子，"
                f"新增 {len(scraped_posts)} 个，最早日期: {earliest_date_found}，"
                f"目标达成: {target_reached}"
            )
            return scraped_posts
            
        except Exception as e:
            print(f"\n❌ 爬取过程出错: {e}")
            logger.error(f"滚动和爬取过程失败: {e}")
            return scraped_posts
    
    def _reached_target_date(self, target_date: str) -> bool:
        """检查是否已经滚动到目标日期 - 修复版本"""
        try:
            # 使用正确的选择器获取帖子
            post_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".status"
            )
            
            if not post_elements:
                return False
            
            # 检查最后几个帖子的时间
            for post in post_elements[-5:]:
                try:
                    # Truth Social的时间在time元素中
                    time_element = post.find_element(By.CSS_SELECTOR, "time")
                    title_time = time_element.get_attribute("title")
                    
                    if title_time:
                        # 解析时间格式 "Jul 07, 2025, 10:24 AM"
                        try:
                            parsed_time = datetime.strptime(
                                title_time, "%b %d, %Y, %I:%M %p"
                            )
                            post_date_et = self.et_tz.localize(parsed_time)
                            post_date_str = post_date_et.strftime("%Y-%m-%d")
                            
                            if post_date_str <= target_date:
                                logger.info(
                                    f"找到目标日期帖子: {post_date_str} <= {target_date}"
                                )
                                return True
                                
                        except ValueError as e:
                            logger.debug(f"时间解析失败: {title_time}, {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"获取帖子时间失败: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"检查目标日期失败: {e}")
            return False
    
    def extract_post_data(self, post_element) -> Optional[Dict]:
        """从帖子元素提取数据"""
        try:
            post_data = {}
            
            # 获取帖子HTML
            post_html = post_element.get_attribute("outerHTML")
            soup = BeautifulSoup(post_html, 'html.parser')
            
            # 提取帖子ID
            try:
                # Truth Social在.status__wrapper中有data-id属性
                wrapper = post_element.find_element(By.CSS_SELECTOR, ".status__wrapper")
                post_id = wrapper.get_attribute("data-id")
            except NoSuchElementException:
                # 如果找不到wrapper，尝试从链接中提取ID
                try:
                    link_element = post_element.find_element(By.CSS_SELECTOR, "a[href*='/posts/']")
                    href = link_element.get_attribute("href")
                    post_id = href.split('/posts/')[-1].split('?')[0]
                except NoSuchElementException:
                    post_id = None
            
            if not post_id:
                logger.warning("无法提取帖子ID")
                return None
            
            post_data['post_id'] = post_id
            
            # 提取帖子内容
            try:
                # Truth Social使用.status-content类来包含帖子内容
                content_element = post_element.find_element(By.CSS_SELECTOR, ".status-content, .status__content")
                content = content_element.text.strip()
                post_data['content'] = content
            except NoSuchElementException:
                # 如果找不到标准内容元素，尝试获取整个帖子的文本
                try:
                    content = post_element.text.strip()
                    # 移除用户名和时间戳部分
                    lines = content.split('\n')
                    if len(lines) > 3:
                        content = '\n'.join(lines[3:])  # 跳过用户名、@handle和时间
                    post_data['content'] = content
                except Exception:
                    logger.warning(f"帖子 {post_id} 无法提取内容")
                    return None
            
            # 提取时间信息
            try:
                time_element = post_element.find_element(By.CSS_SELECTOR, "time")
                # Truth Social在title属性中有完整的时间信息
                title_time = time_element.get_attribute("title")
                datetime_str = time_element.get_attribute("datetime")
                
                if title_time:
                    # 解析title中的时间 (格式: "Jul 07, 2025, 10:24 AM")
                    try:
                        # 转换为标准格式
                        parsed_time = datetime.strptime(title_time, "%b %d, %Y, %I:%M %p")
                        # 假设时间是东部时间
                        post_datetime_et = self.et_tz.localize(parsed_time)
                        post_data['timestamp_et'] = post_datetime_et.isoformat()
                        post_data['post_date'] = post_datetime_et.strftime("%Y-%m-%d")
                        post_data['post_time'] = post_datetime_et.strftime("%H:%M:%S")
                        
                        # 转换为UTC
                        post_datetime_utc = post_datetime_et.astimezone(pytz.UTC)
                        post_data['timestamp_utc'] = post_datetime_utc.isoformat()
                        
                    except ValueError:
                        logger.warning(f"帖子 {post_id} 时间格式解析失败: {title_time}")
                        return None
                        
                elif datetime_str:
                    # 备用：使用datetime属性
                    post_datetime_utc = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    post_data['timestamp_utc'] = post_datetime_utc.isoformat()
                    
                    post_datetime_et = post_datetime_utc.astimezone(self.et_tz)
                    post_data['timestamp_et'] = post_datetime_et.isoformat()
                    post_data['post_date'] = post_datetime_et.strftime("%Y-%m-%d")
                    post_data['post_time'] = post_datetime_et.strftime("%H:%M:%S")
                    
                else:
                    logger.warning(f"帖子 {post_id} 无法提取时间")
                    return None
                    
            except NoSuchElementException:
                logger.warning(f"帖子 {post_id} 无法找到时间元素")
                return None
            
            # 提取互动数据
            try:
                likes_element = post_element.find_element(By.CSS_SELECTOR, "[data-testid='like-count']")
                post_data['likes_count'] = int(likes_element.text.replace(',', '')) if likes_element.text else 0
            except (NoSuchElementException, ValueError):
                post_data['likes_count'] = 0
            
            try:
                reposts_element = post_element.find_element(By.CSS_SELECTOR, "[data-testid='repost-count']")
                post_data['reposts_count'] = int(reposts_element.text.replace(',', '')) if reposts_element.text else 0
            except (NoSuchElementException, ValueError):
                post_data['reposts_count'] = 0
            
            try:
                comments_element = post_element.find_element(By.CSS_SELECTOR, "[data-testid='comment-count']")
                post_data['comments_count'] = int(comments_element.text.replace(',', '')) if comments_element.text else 0
            except (NoSuchElementException, ValueError):
                post_data['comments_count'] = 0
            
            # 提取媒体URL
            media_urls = []
            try:
                media_elements = post_element.find_elements(By.CSS_SELECTOR, "img, video")
                for media in media_elements:
                    src = media.get_attribute("src")
                    if src and src.startswith("http"):
                        media_urls.append(src)
            except Exception:
                pass
            
            post_data['media_urls'] = json.dumps(media_urls) if media_urls else None
            
            # 构建帖子URL
            post_data['post_url'] = f"https://truthsocial.com/@realDonaldTrump/posts/{post_id}"
            
            return post_data
            
        except Exception as e:
            logger.error(f"提取帖子数据失败: {e}")
            return None
    
    def scrape_posts(self, days_back: int = 0) -> List[Dict]:
        """爬取帖子数据"""
        scraped_posts = []
        
        try:
            self.setup_driver()
            
            # 访问Truth Social页面
            logger.info(f"访问 {TRUTH_SOCIAL_URL}")
            self.driver.get(TRUTH_SOCIAL_URL)
            
            # 等待页面加载
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".status"))
            )
            
            # 如果需要爬取历史数据，计算目标日期
            target_date = None
            if days_back > 0:
                target_date = (datetime.now(self.et_tz) - timedelta(days=days_back)).strftime("%Y-%m-%d")
                logger.info(f"目标爬取日期: {target_date}")
            
            # 边滚动边处理帖子
            scraped_posts = self.scroll_and_scrape_posts(target_date)
            
            logger.info(f"爬取完成，共获取 {len(scraped_posts)} 个新帖子")
            return scraped_posts
            
        except TimeoutException:
            logger.error("页面加载超时")
            return scraped_posts
        except Exception as e:
            logger.error(f"爬取过程失败: {e}")
            return scraped_posts
        finally:
            self.close_driver()
    
    def run_with_retry(self, days_back: int = 0) -> List[Dict]:
        """带重试机制的爬取"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"开始第 {attempt + 1} 次爬取尝试")
                result = self.scrape_posts(days_back)
                
                if result or attempt == MAX_RETRIES - 1:
                    return result
                
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次爬取失败: {e}")
                
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
        
        return [] 