@echo off
chcp 65001 >nul
title AI_Novel_Generator - 快速打包工具 v4.1.2

echo ====================================
echo   AI_Novel_Generator - 快速打包工具
echo   版本 4.1.2 - 修复bug + 媒体生成
echo ====================================
echo.

echo 正在启动Python打包脚本...
echo.

python build_quick.py

echo.
echo 打包完成！按任意键退出...
pause >nul 