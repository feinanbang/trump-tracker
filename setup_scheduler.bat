@echo off
echo 正在设置Trump Truth Social爬虫定时任务...
echo.

REM 获取当前目录
set "CURRENT_DIR=%~dp0"
set "PYTHON_SCRIPT=%CURRENT_DIR%main.py"

echo 脚本路径: %PYTHON_SCRIPT%
echo.

REM 创建定时任务 - 每小时运行一次
schtasks /create /tn "Trump Truth Social 爬虫" /tr "python \"%PYTHON_SCRIPT%\"" /sc hourly /st 00:00 /f

if %errorlevel% equ 0 (
    echo ✅ 定时任务创建成功！
    echo.
    echo 📋 任务详情:
    echo    任务名称: Trump Truth Social 爬虫
    echo    运行频率: 每小时一次
    echo    开始时间: 每小时的00分
    echo    脚本路径: %PYTHON_SCRIPT%
    echo.
    echo 🎯 任务已激活，将在下一个整点开始运行
    echo.
    
    REM 显示当前任务状态
    echo 📊 当前任务状态:
    schtasks /query /tn "Trump Truth Social 爬虫"
) else (
    echo ❌ 定时任务创建失败
    echo 请确保以管理员权限运行此脚本
)

echo.
echo 💡 管理提示:
echo    查看任务: schtasks /query /tn "Trump Truth Social 爬虫"
echo    删除任务: schtasks /delete /tn "Trump Truth Social 爬虫" /f
echo    立即运行: schtasks /run /tn "Trump Truth Social 爬虫"
echo.
pause 