#!/usr/bin/env python3
"""
网络连接测试
"""
import sys
import time
import socket

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

flush_print("=== 网络连接诊断 ===")

# 1. 测试基本网络连接
flush_print("\n1. 测试基本网络连接...")
try:
    import requests
    flush_print("   requests库导入成功")
    
    # 测试访问百度（国内网络测试）
    flush_print("   测试访问百度...")
    response = requests.get("https://www.baidu.com", timeout=10)
    flush_print(f"   百度响应状态: {response.status_code}")
    
    # 测试访问Google（国际网络测试）
    flush_print("   测试访问Google...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        flush_print(f"   Google响应状态: {response.status_code}")
    except Exception as e:
        flush_print(f"   Google访问失败: {e}")
        flush_print("   可能存在网络限制或墙的问题")
        
except Exception as e:
    flush_print(f"   网络测试失败: {e}")

# 2. 测试Truth Social连接
flush_print("\n2. 测试Truth Social连接...")
try:
    truth_social_url = "https://truthsocial.com"
    flush_print(f"   尝试访问: {truth_social_url}")
    
    response = requests.get(truth_social_url, timeout=30)
    flush_print(f"   Truth Social响应状态: {response.status_code}")
    flush_print(f"   响应大小: {len(response.content)} 字节")
    
    if response.status_code == 200:
        flush_print("   ✅ Truth Social可以正常访问")
    else:
        flush_print(f"   ⚠️ Truth Social返回异常状态码: {response.status_code}")
        
except requests.exceptions.Timeout:
    flush_print("   ❌ Truth Social访问超时")
    flush_print("   可能原因: 网络延迟过高或服务器响应慢")
    
except requests.exceptions.ConnectionError:
    flush_print("   ❌ Truth Social连接失败")
    flush_print("   可能原因: DNS解析失败或网络被阻断")
    
except Exception as e:
    flush_print(f"   ❌ Truth Social访问出错: {e}")

# 3. 测试DNS解析
flush_print("\n3. 测试DNS解析...")
try:
    import socket
    ip = socket.gethostbyname("truthsocial.com")
    flush_print(f"   truthsocial.com解析到: {ip}")
except Exception as e:
    flush_print(f"   DNS解析失败: {e}")

# 4. 测试ChromeDriver下载
flush_print("\n4. 测试ChromeDriver下载...")
try:
    from webdriver_manager.chrome import ChromeDriverManager
    flush_print("   webdriver_manager导入成功")
    
    flush_print("   尝试获取ChromeDriver...")
    # 设置较短的超时时间来测试
    driver_path = ChromeDriverManager().install()
    flush_print(f"   ChromeDriver路径: {driver_path}")
    flush_print("   ✅ ChromeDriver下载成功")
    
except Exception as e:
    flush_print(f"   ❌ ChromeDriver下载失败: {e}")
    flush_print("   这可能是导致程序无响应的主要原因！")

# 5. 给出诊断结果
flush_print("\n=== 诊断结果 ===")
flush_print("如果上面的测试显示:")
flush_print("- Truth Social访问超时/失败 → 网络连接问题")
flush_print("- ChromeDriver下载失败 → 可能需要VPN或代理")
flush_print("- DNS解析失败 → 网络配置问题")
flush_print("\n建议解决方案:")
flush_print("1. 检查网络连接是否稳定")
flush_print("2. 尝试使用VPN或代理")
flush_print("3. 检查防火墙设置")
flush_print("4. 手动下载ChromeDriver")

flush_print("\n=== 测试完成 ===") 