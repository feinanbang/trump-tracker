@echo off
chcp 65001 > nul
echo Trump Truth Social 爬虫程序
echo ==========================

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

:: 检查是否需要安装依赖
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 安装依赖包...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 显示菜单
:menu
echo.
echo 请选择操作:
echo 1. 启动定时爬虫 (每小时运行)
echo 2. 测试运行一次
echo 3. 爬取历史数据 (过去30天)
echo 4. 查看数据库状态
echo 5. 退出
echo.
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" (
    echo 启动定时爬虫...
    python main.py
    goto menu
)

if "%choice%"=="2" (
    echo 测试运行...
    python main.py --test
    pause
    goto menu
)

if "%choice%"=="3" (
    echo 爬取历史数据...
    python main.py --historical 30
    pause
    goto menu
)

if "%choice%"=="4" (
    echo 查看数据库状态...
    python main.py --status
    pause
    goto menu
)

if "%choice%"=="5" (
    echo 退出程序
    exit /b 0
)

echo 无效选项，请重新选择
goto menu 