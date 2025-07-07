#!/usr/bin/env python3
"""
调试导入问题
"""

import sys

print("Python 版本:", sys.version)
print("当前工作目录:", sys.path[0])
print()

# 测试基础导入
try:
    import logging
    print("✅ logging 导入成功")
except Exception as e:
    print("❌ logging 导入失败:", e)

try:
    import datetime
    print("✅ datetime 导入成功")
except Exception as e:
    print("❌ datetime 导入失败:", e)

try:
    import pytz
    print("✅ pytz 导入成功")
except Exception as e:
    print("❌ pytz 导入失败:", e)

try:
    from selenium import webdriver
    print("✅ selenium 导入成功")
except Exception as e:
    print("❌ selenium 导入失败:", e)

try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup 导入成功")
except Exception as e:
    print("❌ BeautifulSoup 导入失败:", e)

print()

# 测试项目模块导入
try:
    import config
    print("✅ config 模块导入成功")
except Exception as e:
    print("❌ config 模块导入失败:", e)

try:
    import utils
    print("✅ utils 模块导入成功")
except Exception as e:
    print("❌ utils 模块导入失败:", e)

try:
    import database
    print("✅ database 模块导入成功")
except Exception as e:
    print("❌ database 模块导入失败:", e)

try:
    import scraper
    print("✅ scraper 模块导入成功")
except Exception as e:
    print("❌ scraper 模块导入失败:", e)

try:
    import main
    print("✅ main 模块导入成功")
except Exception as e:
    print("❌ main 模块导入失败:", e)

print()
print("如果所有模块都导入成功，那么问题可能是:")
print("1. PowerShell 输出缓冲问题")
print("2. 程序在等待用户输入")
print("3. 程序在后台执行但没有立即输出")

print()
print("测试完成！") 