#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI_Novel_Generator - 快速打包脚本 v4.1.2
自动使用最佳设置进行打包，无需用户交互
"""

import os
import sys
import shutil
import subprocess
import time
import json


def clean_build_dirs():
    """清理构建目录"""
    print("正在清理构建目录...")
    for dir_name in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"已清理 {dir_name}")
            except Exception as e:
                print(f"清理 {dir_name} 失败: {e}")


def ensure_pyinstaller():
    """确保PyInstaller已安装"""
    try:
        import PyInstaller

        print(f"PyInstaller 版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("正在安装 PyInstaller...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "pyinstaller>=6.0.0",
                ]
            )
            print("PyInstaller 安装完成")
            return True
        except Exception as e:
            print(f"PyInstaller 安装失败: {e}")
            return False


def create_version_file():
    """创建版本信息文件"""
    version_info = """
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(4,1,2,0),
prodvers=(4,1,2,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'080404B0',
    [StringStruct(u'CompanyName', u'147229'),
    StringStruct(u'FileDescription', u'AI小说生成器 - 智能小说创作工具'),
    StringStruct(u'FileVersion', u'4.1.2'),
    StringStruct(u'InternalName', u'AI小说生成器'),
    StringStruct(u'LegalCopyright', u'Copyright (C) 2024 147229'),
    StringStruct(u'OriginalFilename', u'AI小说生成器_v4.1.2.exe'),
    StringStruct(u'ProductName', u'AI小说生成器'),
    StringStruct(u'ProductVersion', u'4.1.2')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
    ]
    )
"""

    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    print("已创建版本信息文件")


def main():
    """主打包函数"""
    print("=" * 60)
    print("  AI小说生成器 - 快速打包脚本 v4.1.2")
    print("  修复内容清理bug + 媒体生成功能")
    print("=" * 60)

    start_time = time.time()

    # 检查主文件是否存在
    if not os.path.exists("main.py"):
        print("错误: 找不到 main.py 文件")
        print("请确保在项目根目录运行此脚本")
        sys.exit(1)

    # 清理构建目录
    clean_build_dirs()

    # 确保PyInstaller已安装
    if not ensure_pyinstaller():
        print("无法安装PyInstaller，打包终止")
        sys.exit(1)

    # 创建版本信息文件
    create_version_file()

    # 检查资源文件
    if not os.path.exists("resources"):
        os.makedirs("resources")
        print("已创建 resources 目录")

    # 构建PyInstaller命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=AI小说生成器_v4.1.2",
        "--onedir",  # 使用目录模式，更稳定
        "--windowed",  # 隐藏控制台
        "--clean",
        "--noconfirm",
        "--add-data=resources;resources",
        "--add-data=templates;templates",
        "--add-data=example_prompts;example_prompts",
        "--hidden-import=aiohttp",
        "--hidden-import=aiohttp.client",
        "--hidden-import=http.client",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=configparser",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=pytest",
        "--version-file=version_info.txt",
    ]

    # 添加图标（如果存在）
    icon_path = os.path.join("resources", "icon.ico")
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    # 添加主文件
    cmd.append("main.py")

    print("正在执行打包命令:")
    print(" ".join(cmd))
    print("\n开始打包...")

    try:
        # 执行打包
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="gbk",
            errors="ignore",
        )
        print("打包命令执行成功")

        # 计算耗时
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        print(f"\n打包完成！耗时: {minutes}分{seconds}秒")

        # 检查输出目录
        if os.path.exists("dist"):
            print("可执行文件位于 dist 目录")

            # 复制说明文档
            docs_to_copy = [
                ("README.md", "使用说明.md"),
                ("UPDATE_NOTES_v4.0.md", "更新说明.md"),
                ("USER_GUIDE.md", "用户指南.md"),
                ("PACKAGING_GUIDE.md", "打包指南.md"),
            ]

            for src, dst in docs_to_copy:
                if os.path.exists(src):
                    try:
                        shutil.copy(src, os.path.join("dist", dst))
                        print(f"已复制 {src} -> {dst}")
                    except Exception as e:
                        print(f"复制 {src} 失败: {e}")

            # 创建清洁的配置文件
            clean_config = {
                "api_key": "",
                "model": "gemini-2.0-flash",
                "language": "中文",
                "max_workers": 3,
                "context_length": 100000,
                "novel_type": "奇幻冒险",
                "target_length": 20000,
                "num_novels": 1,
                "auto_summary": True,
                "auto_summary_interval": 10000,
                "temperature": 0.7,
                "top_p": 0.9,
                "generate_cover": False,
                "generate_music": False,
                "num_cover_images": 1,
                "midjourney_api_key": "",
                "suno_api_key": "",
            }

            try:
                config_path = os.path.join("dist", "novel_generator_config.json")
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(clean_config, f, ensure_ascii=False, indent=2)
                print("已创建默认配置文件")
            except Exception as e:
                print(f"创建配置文件失败: {e}")

            # 创建更新日志
            changelog = f"""AI_Novel_Generator v4.1.2 更新日志
================================

发布时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

主要更新:
--------
1. 【重要修复】修复了内容清理方法中的严重bug，解决了生成内容被意外清空的问题
2. 【新功能】添加了封面生成功能，支持MidJourney API
3. 【新功能】添加了音乐生成功能，支持Suno API
4. 【优化】改进了"社会现实"类型小说的提示词模板
5. 【优化】增强了API响应解析和错误处理
6. 【优化】提高了内容长度检查阈值，减少"内容过短"错误

技术改进:
--------
- 修复了_clean_content方法中导致内容被跳过的逻辑错误
- 增强了媒体生成的任务管理和状态跟踪
- 优化了API调用的重试机制和错误处理
- 改进了内容安全策略的兼容性

使用说明:
--------
1. 首次使用请配置API密钥
2. 媒体生成功能需要额外的MidJourney和Suno API密钥
3. 建议使用目录模式而非单文件模式以获得更好的性能

注意事项:
--------
- 本版本修复了重要的内容生成bug，强烈建议更新
- 媒体生成功能为可选功能，不影响基本的小说生成
- 请确保网络连接稳定以获得最佳体验
"""

            try:
                changelog_path = os.path.join("dist", "更新日志_v4.1.2.txt")
                with open(changelog_path, "w", encoding="utf-8") as f:
                    f.write(changelog)
                print("已创建更新日志")
            except Exception as e:
                print(f"创建更新日志失败: {e}")

            # 尝试打开输出目录
            try:
                if sys.platform == "win32":
                    os.startfile(os.path.abspath("dist"))
                elif sys.platform == "darwin":
                    subprocess.run(["open", os.path.abspath("dist")])
                else:
                    subprocess.run(["xdg-open", os.path.abspath("dist")])
                print("已打开输出目录")
            except Exception:
                print(f"输出目录位置: {os.path.abspath('dist')}")
        else:
            print("打包失败: 未找到输出目录")

    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
    except Exception as e:
        print(f"打包过程中发生错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # 清理临时文件
        temp_files = ["version_info.txt"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"已清理临时文件: {temp_file}")
                except Exception as e:
                    print(f"清理临时文件 {temp_file} 失败: {e}")

    print("\n打包过程结束")


if __name__ == "__main__":
    main()
