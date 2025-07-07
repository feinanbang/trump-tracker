#!/usr/bin/env python3
"""
测试Trump Truth Social自动小结功能

此脚本用于测试AI小结生成功能，包括：
1. 环境配置检查
2. Hugging Face API连接测试
3. 小结生成测试
4. 数据库存储测试
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TIMEZONE
from database import TrumpPostsDB
from summarizer import TrumpPostSummarizer
from utils import setup_logging

logger = setup_logging()


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查Hugging Face Token
    hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
    if not hf_token:
        print("❌ 未设置HUGGINGFACE_API_TOKEN环境变量")
        print("💡 请运行 config_hf.example.bat 配置API Token")
        return False
    
    print(f"✅ Hugging Face Token已配置 (长度: {len(hf_token)})")
    
    # 检查数据库
    try:
        db = TrumpPostsDB()
        post_count = db.get_posts_count()
        print(f"✅ 数据库连接正常，共有 {post_count} 条帖子")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试Hugging Face API连接...")
    
    try:
        summarizer = TrumpPostSummarizer()
        
        # 测试简单的API调用
        test_prompt = "Test connection to Hugging Face API"
        
        for model_name in summarizer.models[:2]:  # 只测试前两个模型
            print(f"📡 测试模型: {model_name}")
            try:
                response = summarizer.call_huggingface_api(test_prompt, model_name)
                
                if response:
                    print(f"✅ 模型 {model_name} 连接成功")
                    return True
                else:
                    print(f"⚠️ 模型 {model_name} 连接失败，尝试下一个...")
            except Exception as model_error:
                print(f"⚠️ 模型 {model_name} 调用异常: {model_error}")
        
        print("❌ 所有模型连接失败")
        return False
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_generation():
    """测试小结生成"""
    print("\n📝 测试小结生成功能...")
    
    # 获取有数据的最近日期
    db = TrumpPostsDB()
    et_tz = pytz.timezone(TIMEZONE)
    
    test_date = None
    for i in range(7):  # 检查最近7天
        date = (datetime.now(et_tz) - timedelta(days=i)).strftime('%Y-%m-%d')
        posts = db.get_posts_by_date(date)
        
        if posts:
            test_date = date
            print(f"📅 找到测试日期: {date} ({len(posts)} 条帖子)")
            break
    
    if not test_date:
        print("❌ 没有找到测试数据")
        return False
    
    try:
        print(f"🤖 正在生成 {test_date} 的小结...")
        
        summarizer = TrumpPostSummarizer()
        summary = summarizer.generate_daily_summary(test_date)
        
        if summary:
            print(f"✅ 小结生成成功！")
            print(f"\n{'='*60}")
            print(summary)
            print(f"{'='*60}")
            
            # 检查数据库中是否保存了小结
            saved_summary = db.get_summary_by_date(test_date)
            if saved_summary:
                print(f"\n✅ 小结已保存到数据库")
                print(f"生成方式: {saved_summary.get('generated_by')}")
                print(f"生成时间: {saved_summary.get('generated_at')}")
            else:
                print(f"\n⚠️ 小结未保存到数据库")
            
            return True
        else:
            print(f"❌ 小结生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 小结生成测试失败: {e}")
        return False


def test_database_storage():
    """测试数据库存储功能"""
    print("\n💾 测试数据库存储功能...")
    
    try:
        db = TrumpPostsDB()
        
        # 检查小结表是否存在
        summaries_count = db.get_summaries_count()
        print(f"📊 当前小结数量: {summaries_count}")
        
        # 获取最近的小结
        recent_summaries = db.get_recent_summaries(3)
        if recent_summaries:
            print(f"✅ 最近小结:")
            for summary in recent_summaries:
                date = summary.get('summary_date')
                post_count = summary.get('post_count')
                generated_by = summary.get('generated_by')
                print(f"  • {date}: {post_count} 帖子, 生成方式: {generated_by}")
        else:
            print(f"📝 暂无小结数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库存储测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 Trump Truth Social 自动小结功能测试")
    print("=" * 60)
    
    # 测试步骤
    tests = [
        ("环境配置", check_environment),
        ("API连接", test_api_connection),
        ("小结生成", test_summary_generation),
        ("数据库存储", test_database_storage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 测试: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 总结
    print(f"\n{'='*60}")
    print(f"测试完成: {passed}/{total} 项通过")
    
    if passed == total:
        print(f"🎉 所有测试通过！AI小结功能可以正常使用")
        print(f"💡 使用方法: python main.py --summary YYYY-MM-DD")
    else:
        print(f"⚠️ 部分测试失败，请检查配置")
        
        if passed == 0:
            print(f"💡 建议:")
            print(f"1. 运行 config_hf.example.bat 配置API Token")
            print(f"2. 确保已爬取一些帖子数据")
            print(f"3. 检查网络连接")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    main() 