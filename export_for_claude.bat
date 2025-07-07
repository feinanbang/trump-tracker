@echo off
cd /d "%~dp0"

echo =====================================
echo    Trump Truth Social 导出工具
echo =====================================
echo.

python main.py --export

echo.
echo 按任意键退出...
pause > nul 