@echo off
echo ========================================
echo     Trump Truth Social 分析网站
echo ========================================
echo.
echo 正在启动网站服务器...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.

cd /d "%~dp0"
python web_app.py

pause 