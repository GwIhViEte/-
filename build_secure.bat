@echo off
chcp 65001 > nul
title AI_Novel_Generator - 安全打包工具
color 0B

echo ==========================================
echo     AI_Novel_Generator - 安全打包工具 v1.0
echo     防反编译增强版
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.7或更高版本
    echo 可以从 https://www.python.org/downloads/ 下载Python
    pause
    exit /b
)

echo [信息] 检测到Python已安装

REM 检查核心文件
if not exist main.py (
    echo [错误] 在当前目录下找不到main.py
    echo 请确保此脚本与main.py在同一目录下
    pause
    exit /b
)

REM 更新必要的库
echo [信息] 正在安装/更新必要的库...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --upgrade pyinstaller pyarmor

REM 创建安全打包环境
echo [信息] 准备打包环境...

REM 设置PyInstaller特定环境变量以增强安全性
set PYTHONOPTIMIZE=2
set PYTHONDONTWRITEBYTECODE=1

echo.
echo [信息] 启动增强型打包工具...
echo.
echo 提示：
echo - 推荐使用目录模式（非单文件）打包，启动速度更快
echo - 启用代码混淆保护可以有效防止反编译
echo - 关闭控制台窗口可以提升用户体验
echo.

REM 运行优化的Python打包脚本
python build.py

REM 清理临时文件
if exist "__pycache__" (
    echo [清理] 正在删除__pycache__目录...
    rd /s /q "__pycache__"
)

if exist "obfuscated" (
    echo [清理] 正在删除临时混淆目录...
    rd /s /q "obfuscated"
)

echo.
echo [完成] 打包过程已完成！
echo 如果打包成功，可执行文件位于dist目录中

pause 