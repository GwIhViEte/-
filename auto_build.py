#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import time
import json


def auto_build():
    """
    自动化打包脚本 - 无需交互式输入
    """
    print("=" * 60)
    print("  AI_Novel_Generator - 自动化打包工具")
    print("  版本 5.0.5 - 修复代码混淆 + 自动化打包")
    print("=" * 60)

    # 确保 PyInstaller 已安装
    try:
        import PyInstaller  # type: ignore[import-untyped]

        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("正在安装 PyInstaller...")
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

    # 清理之前的打包文件
    for dir_to_clean in ["build", "dist"]:
        if os.path.exists(dir_to_clean):
            print(f"正在清理 {dir_to_clean} 目录...")
            shutil.rmtree(dir_to_clean)

    # 自动配置打包参数（推荐设置）
    is_onefile = True  # 使用文件夹模式，启动更快
    use_console = False  # 隐藏控制台窗口
    app_name = "AI_Novel_Generator"

    print("\n打包配置:")
    print(f"- 模式: {'单文件' if is_onefile else '文件夹'}")
    print(f"- 控制台: {'显示' if use_console else '隐藏'}")
    print(f"- 应用名称: {app_name}")

    # 检查图标文件
    icon_path = None
    possible_icons = [
        "resources/icon.ico",
        "resources/icon.png",
        "icon.ico",
        "icon.png",
    ]

    for icon in possible_icons:
        if os.path.exists(icon):
            icon_path = icon
            print(f"找到图标文件: {icon_path}")
            break

    if not icon_path:
        print("未找到图标文件，将不使用图标")

    # 构建 PyInstaller 命令
    pyinstaller_args = [
        "pyinstaller",
        "--onefile" if is_onefile else "--onedir",
        "--console" if use_console else "--windowed",
        "--clean",
        "--noconfirm",
        f"--name={app_name}",
        "--log-level=INFO",
        "--paths=.",
        "--strip",  # 移除调试信息
    ]

    # 添加图标
    if icon_path:
        pyinstaller_args.append(f"--icon={icon_path}")

    # 添加数据文件
    data_files = [("resources", "resources"), ("templates", "templates")]

    for src, dst in data_files:
        if os.path.exists(src):
            pyinstaller_args.append(f"--add-data={src}{os.pathsep}{dst}")

    # 添加隐藏导入
    hidden_imports = [
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "PIL.Image",
        "PIL.ImageTk",
        "asyncio",
        "aiohttp",
        "configparser",
        "json",
        "threading",
        # 添加项目核心模块
        "ui",
        "ui.app",
        "ui.dialogs",
        "core",
        "core.generator",
        "core.media_generator",
        "core.media_task_manager",
        "core.model_manager",
        "core.sanqianliu_generator",
        "core.sanqianliu_interface",
        "utils",
        "utils.common",
        "utils.config",
        "utils.quality",
        "templates",
        "templates.prompts",
        # 添加 novel_generator 命名空间
        "novel_generator",
        "novel_generator.ui",
        "novel_generator.ui.app",
        "novel_generator.ui.dialogs",
        "novel_generator.core",
        "novel_generator.core.generator",
        "novel_generator.utils",
        "novel_generator.templates",
    ]

    for imp in hidden_imports:
        pyinstaller_args.append(f"--hidden-import={imp}")

    # 收集所有项目模块（强制包含源代码）
    for pkg in ["ui", "core", "utils", "templates", "novel_generator"]:
        pyinstaller_args.append(f"--collect-all={pkg}")

    # 添加主程序
    pyinstaller_args.append("main.py")

    # 执行打包
    print("\n开始打包...")
    print("执行命令:", " ".join(pyinstaller_args))

    start_time = time.time()

    try:
        result = subprocess.run(  # noqa: E501
            pyinstaller_args, capture_output=True, text=True
        )

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        if result.returncode == 0:
            print(f"\n打包成功！耗时: {minutes}分{seconds}秒")

            # 检查输出文件
            if os.path.exists("dist"):
                dist_files = os.listdir("dist")
                print(f"生成的文件: {dist_files}")

                # 创建默认配置文件
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
                }

                config_path = os.path.join(  # noqa: E501
                    "dist", "novel_generator_config.json"
                )
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(clean_config, f, ensure_ascii=False, indent=2)
                print(f"已创建配置文件: {config_path}")

                # 复制说明文档
                docs = ["README.md", "USER_GUIDE.md"]
                for doc in docs:
                    if os.path.exists(doc):
                        shutil.copy2(doc, "dist/")
                        print(f"已复制文档: {doc}")

                print(f"\n打包完成，文件位于: {os.path.abspath('dist')}")

                # 计算文件大小
                total_size = 0
                for root, dirs, files in os.walk("dist"):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))

                size_mb = total_size / (1024 * 1024)
                print(f"总大小: {size_mb:.1f} MB")

            else:
                print("打包失败：未找到dist目录")

        else:
            print(f"打包失败，返回码: {result.returncode}")
            print("错误输出:")
            print(result.stderr)

    except Exception as e:
        print(f"打包过程出错: {e}")
        return False

    return result.returncode == 0


if __name__ == "__main__":
    success = auto_build()
    if success:
        print("\n打包完成！")
    else:
        print("\n打包失败！")
        sys.exit(1)
