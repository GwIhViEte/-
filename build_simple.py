#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI_Novel_Generator - 简化打包脚本 v4.1.2
使用基本PyInstaller命令进行打包
"""

import os
import sys
import shutil
import subprocess
import time


def main():
    print("AI_Novel_Generator v4.1.2 - 简化打包脚本")
    print("=" * 50)

    # 清理旧的构建文件
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            shutil.rmtree(dir_name)

    # 检查PyInstaller
    try:
        import PyInstaller

        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=AI_Novel_Generator",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
    ]

    # 添加数据文件
    if os.path.exists("resources"):
        cmd.append("--add-data=resources;resources")
    if os.path.exists("templates"):
        cmd.append("--add-data=templates;templates")
    if os.path.exists("example_prompts"):
        cmd.append("--add-data=example_prompts;example_prompts")

    # 添加图标
    if os.path.exists("resources/icon.ico"):
        cmd.append("--icon=resources/icon.ico")

    # 隐藏导入
    hidden_imports = [
        "aiohttp",
        "aiohttp.client",
        "http.client",
        "tkinter",
        "tkinter.ttk",
        "configparser",
        "json",
        "asyncio",
        "threading",
    ]

    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")

    # 排除模块
    excludes = ["matplotlib", "numpy", "scipy", "pandas", "pytest"]
    for exc in excludes:
        cmd.append(f"--exclude-module={exc}")

    # 主文件
    cmd.append("main.py")

    print("\n开始打包...")
    print("命令:", " ".join(cmd))

    start_time = time.time()

    try:
        # 执行打包
        subprocess.run(cmd, check=True)

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n打包完成！耗时: {minutes}分{seconds}秒")

        if os.path.exists("dist"):
            print("可执行文件位于 dist 目录")

            # 复制文档
            docs = [
                ("README.md", "使用说明.md"),
                ("UPDATE_NOTES_v4.1.2.md", "更新说明.md"),
                ("USER_GUIDE.md", "用户指南.md"),
            ]

            for src, dst in docs:
                if os.path.exists(src):
                    try:
                        shutil.copy(src, os.path.join("dist", dst))
                        print(f"已复制: {dst}")
                    except Exception as e:
                        print(f"复制失败 {src}: {e}")

            # 创建配置文件
            import json

            config = {
                "api_key": "",
                "model": "gemini-2.0-flash",
                "language": "中文",
                "novel_type": "奇幻冒险",
                "target_length": 20000,
                "generate_cover": False,
                "generate_music": False,
                "num_cover_images": 1,
            }

            try:
                with open(
                    os.path.join("dist", "novel_generator_config.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print("已创建配置文件")
            except Exception as e:
                print(f"创建配置文件失败: {e}")

            # 打开目录
            try:
                if sys.platform == "win32":
                    os.startfile(os.path.abspath("dist"))
                else:
                    print(f"输出目录: {os.path.abspath('dist')}")
            except Exception:
                print(f"输出目录: {os.path.abspath('dist')}")
        else:
            print("打包失败: 未找到输出目录")

    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
    except Exception as e:
        print(f"错误: {e}")

    print("\n打包过程结束")


if __name__ == "__main__":
    main()
