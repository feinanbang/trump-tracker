print("程序开始运行...")

try:
    print("测试 1: 基础Python功能")
    print("1 + 1 =", 1 + 1)
    
    print("测试 2: 导入系统模块")
    import sys
    print("Python版本:", sys.version_info.major, ".", sys.version_info.minor)
    
    print("测试 3: 导入第三方包")
    try:
        import pytz
        print("pytz导入成功")
    except:
        print("pytz导入失败")
    
    try:
        import selenium
        print("selenium导入成功")
    except:
        print("selenium导入失败")
    
    print("测试 4: 导入项目模块")
    try:
        from config import TRUTH_SOCIAL_URL
        print("config导入成功, URL:", TRUTH_SOCIAL_URL)
    except Exception as e:
        print("config导入失败:", str(e))
    
    print("所有测试完成！")
    
except Exception as e:
    print("出现错误:", str(e))
    import traceback
    traceback.print_exc()

print("程序结束") 