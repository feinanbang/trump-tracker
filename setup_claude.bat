@echo off
echo Trump Truth Social 爬虫 - Claude API配置
echo =============================================
echo.
echo 此脚本将帮助您配置Claude API
echo.
echo 步骤1: 获取Claude API Key
echo ------------------------
echo 1. 访问: https://console.anthropic.com/
echo 2. 注册Anthropic账号
echo 3. 进入API Keys页面
echo 4. 创建新的API Key
echo 5. 复制API Key（以sk-ant-开头）
echo.
echo 💰 费用说明：
echo   - Claude-3-Sonnet: $3/1M tokens
echo   - 每日小结成本: 约0.02-0.07元人民币
echo   - 首次注册通常有免费额度
echo.
echo 步骤2: 配置环境变量
echo ------------------
set /p token="请粘贴您的Claude API Key: "

if "%token%"=="" (
    echo 错误：API Key不能为空
    pause
    exit /b 1
)

echo.
echo 正在配置环境变量...
setx CLAUDE_API_KEY "%token%"

if %errorlevel%==0 (
    echo.
    echo ✅ 配置成功！
    echo.
    echo 环境变量已设置：CLAUDE_API_KEY
    echo.
    echo 💡 重要提示：
    echo 1. 请重新启动命令行窗口让环境变量生效
    echo 2. 然后可以使用以下命令测试Claude小结功能：
    echo    python claude_summarizer.py
    echo    python main.py --summary 2025-07-07
    echo.
    echo 📊 使用方法：
    echo    python main.py --summary YYYY-MM-DD
    echo.
) else (
    echo.
    echo ❌ 配置失败！
    echo 请以管理员身份运行此脚本
    echo.
)

echo.
pause 