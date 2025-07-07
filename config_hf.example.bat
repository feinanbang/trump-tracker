@echo off
echo Trump Truth Social 爬虫 - Hugging Face API配置
echo ===============================================
echo.
echo 此脚本将帮助您配置Hugging Face API Token
echo.
echo 步骤1: 获取免费API Token
echo ----------------------
echo 1. 访问: https://huggingface.co/
echo 2. 注册账号（完全免费）
echo 3. 进入: https://huggingface.co/settings/tokens
echo 4. 点击 "New token"
echo 5. 创建一个 "Read" 权限的token
echo 6. 复制token（以hf_开头的长字符串）
echo.
echo 步骤2: 配置环境变量
echo ------------------
set /p token="请粘贴您的Hugging Face API Token: "

if "%token%"=="" (
    echo 错误：Token不能为空
    pause
    exit /b 1
)

echo.
echo 正在配置环境变量...
setx HUGGINGFACE_API_TOKEN "%token%"

if %errorlevel%==0 (
    echo.
    echo ✅ 配置成功！
    echo.
    echo 环境变量已设置：HUGGINGFACE_API_TOKEN
    echo.
    echo 💡 重要提示：
    echo 1. 请重新启动命令行窗口让环境变量生效
    echo 2. 然后可以使用以下命令测试AI小结功能：
    echo    python main.py --summary 2025-07-07
    echo.
) else (
    echo.
    echo ❌ 配置失败！
    echo 请以管理员身份运行此脚本
    echo.
)

echo.
pause 