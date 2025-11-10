import os
import sys
import shutil
import subprocess
import random
import string
import time
import json
import argparse
from typing import Any


def generate_random_name(length=8):
    """生成随机名称，用于混淆"""
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def clean_sensitive_info():
    """在打包前清理敏感信息和临时文件"""
    print("\n正在清理敏感信息和临时文件...")

    try:
        # 清理配置文件中的API密钥
        config_files = [
            "novel_generator_config.json",
            "novel_generator_config.ini",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"清理 {config_file} 中的API密钥...")

                if config_file.endswith(".json"):
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        # 清除API密钥
                        if "api_key" in config:
                            config["api_key"] = ""

                        with open(config_file, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)

                        print(f"已清理 {config_file} 中的API密钥")
                    except Exception as e:
                        print(f"清理 {config_file} 失败: {e}")

                elif config_file.endswith(".ini"):
                    try:
                        import configparser

                        config = configparser.ConfigParser()

                        if os.path.exists(config_file):
                            config.read(config_file)

                            default_section = config.get("DEFAULT", {})
                            if "api_key" in default_section:
                                default_section["api_key"] = ""
                                config["DEFAULT"] = default_section

                            with open(config_file, "w", encoding="utf-8") as f:
                                config.write(f)

                            print(f"已清理 {config_file} 中的API密钥")
                    except Exception as e:
                        print(f"清理 {config_file} 失败: {e}")

        # 清理测试生成的小说目录
        novel_dirs = [d for d in os.listdir() if d.startswith("novel_output_")]

        if novel_dirs:
            print(f"发现 {len(novel_dirs)} 个小说输出目录")
            remove_all = (
                input("是否删除所有小说输出目录? (y/n): ").lower().strip() == "y"
            )

            if remove_all:
                for novel_dir in novel_dirs:
                    try:
                        shutil.rmtree(novel_dir)
                        print(f"已删除目录: {novel_dir}")
                    except Exception as e:
                        print(f"删除目录 {novel_dir} 失败: {e}")
            else:
                print("保留小说输出目录")

        # 清理__pycache__目录
        for root, dirs, files in os.walk("."):
            for dir in dirs:
                if dir == "__pycache__":
                    try:
                        pycache_path = os.path.join(root, dir)
                        shutil.rmtree(pycache_path)
                        print(f"已删除目录: {pycache_path}")
                    except Exception as e:
                        print(f"删除 {pycache_path} 失败: {e}")

        # 清理.pyc文件
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".pyc"):
                    try:
                        pyc_path = os.path.join(root, file)
                        os.remove(pyc_path)
                        print(f"已删除文件: {pyc_path}")
                    except Exception as e:
                        print(f"删除 {pyc_path} 失败: {e}")

        print("敏感信息和临时文件清理完成")
    except Exception as e:
        print(f"清理过程中出现错误: {e}")


def main():
    """
    项目打包脚本，使用 PyInstaller 将项目打包成可执行文件，并增加反编译防护
    """
    print("=" * 60)
    print("  AI_Novel_Generator - 增强型打包工具 v1.1")
    print("  版本 4.1.2 - 修复内容清理bug + 媒体生成功能")
    print("=" * 60)
    print("\n正在初始化打包环境...")

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

    # 尝试安装混淆工具
    try:
        import pyarmor  # type: ignore[import-not-found]
    except ImportError:
        print("正在安装 PyArmor（代码保护工具）...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "pyarmor",
                ]
            )
            print("PyArmor 安装完成")
            import pyarmor  # type: ignore[import-not-found]
        except Exception as e:
            print(f"警告: PyArmor 安装失败: {e}")
            print("将继续使用基本保护措施...")

    # 清理之前的打包文件
    for dir_to_clean in ["build", "dist"]:
        if os.path.exists(dir_to_clean):
            print(f"正在清理 {dir_to_clean} 目录...")
            shutil.rmtree(dir_to_clean)

    if os.path.exists("AI_Novel_Generator.spec"):
        os.remove("AI_Novel_Generator.spec")

    # 检查资源目录
    resources_dir = "resources"
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)

    # 创建一个默认图标如果不存在
    icon_path = os.path.join(resources_dir, "icon.ico")
    if not os.path.exists(icon_path):
        print("未找到图标文件，创建一个简单的默认图标...")
        try:
            from PIL import Image

            img = Image.new("RGB", (256, 256), color="darkblue")
            img.save(os.path.join(resources_dir, "icon.png"))
            print("已创建默认图标，请注意此默认图标不是 .ico 格式")
            print("使用 .png 格式继续打包...")
            icon_path = os.path.join(resources_dir, "icon.png")
        except ImportError:
            print("无法创建默认图标，将不使用图标进行打包")
            icon_path = None

    # 询问一些打包选项
    print("\n" + "=" * 40)
    print("打包选项设置")
    print("=" * 40)

    # 打包模式选择
    is_onefile = input("\n是否打包为单个文件？ (y/n, 推荐n): ").lower() == "y"

    # 是否应用混淆保护
    use_obfuscation = input("是否应用代码混淆保护？ (y/n, 推荐y): ").lower() == "y"

    # 是否启用控制台
    use_console = input("是否保留控制台窗口？ (y/n, 推荐n): ").lower() == "y"

    # 应用程序名称
    app_name = input(
        "\n请输入应用程序名称 (直接回车使用默认名称'AI小说生成器_v4.1.2'): "
    )
    if not app_name:
        app_name = "AI小说生成器"

    print("\n正在准备打包...")

    # 应用代码保护措施
    if use_obfuscation:
        try:
            # 生成随机的混淆名称
            # obf_names = [generate_random_name() for _ in range(10)]

            print("正在应用代码保护措施...")

            # 尝试使用PyArmor进行代码加密
            if "pyarmor" in sys.modules:
                print("使用PyArmor进行代码加密...")
                obf_dir = "obfuscated"
                if os.path.exists(obf_dir):
                    shutil.rmtree(obf_dir)

                try:
                    # 检查PyArmor版本并使用对应的命令
                    pyarmor_mod: Any = pyarmor  # type: ignore[name-defined]
                    pyarmor_version = pyarmor_mod.__version__
                    print(f"PyArmor版本: {pyarmor_version}")

                    # PyArmor 8.x 使用新的命令语法
                    if pyarmor_version.startswith("8"):
                        print("使用PyArmor 8.x语法...")
                        pyarmor_cmd = [
                            sys.executable,
                            "-m",
                            "pyarmor",
                            "gen",
                            "--output",
                            obf_dir,
                            "--pack",
                            "main.py",
                            "--enable",
                            "jit",
                            "--private",
                        ]
                    else:
                        # PyArmor 7.x 使用旧语法
                        print("使用PyArmor 7.x语法...")
                        pyarmor_cmd = [
                            sys.executable,
                            "-m",
                            "pyarmor",
                            "obfuscate",
                            "--output",
                            obf_dir,
                            "--restrict",
                            "0",
                            "--advanced",
                            "2",
                            "main.py",
                        ]

                    print("执行PyArmor命令:", " ".join(pyarmor_cmd))
                    result = subprocess.run(  # noqa: E501
                        pyarmor_cmd, capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        print("代码加密成功！将使用加密后的代码打包")
                        # 检查生成的文件
                        possible_main_paths = [
                            os.path.join(obf_dir, "main.py"),
                            os.path.join(obf_dir, "dist", "main.py"),
                            "main.py",  # 对于pack模式，可能直接替换原文件
                        ]

                        main_script = None
                        for path in possible_main_paths:
                            if os.path.exists(path):
                                main_script = path
                                print(f"找到混淆后的main.py: {path}")
                                break

                        if not main_script:
                            print("警告：未找到混淆后的main.py文件，使用原始文件")
                            main_script = "main.py"
                    else:
                        print(f"PyArmor加密失败，返回码: {result.returncode}")
                        print(f"错误输出: {result.stderr}")
                        print("将使用基本保护措施继续...")
                        main_script = "main.py"

                except Exception as e:
                    print(f"PyArmor加密过程中出错: {e}")
                    print("将使用基本保护措施继续...")
                    main_script = "main.py"
            else:
                print("未安装PyArmor，使用基本保护措施...")
                main_script = "main.py"
        except Exception as e:
            print(f"应用代码保护措施时出错: {e}")
            print("将继续使用无保护的代码...")
            main_script = "main.py"
    else:
        main_script = "main.py"

    # 构建 PyInstaller 命令
    pyinstaller_args = [
        "pyinstaller",
        "--onefile" if is_onefile else "--onedir",
        "--console" if use_console else "--windowed",
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问确认
        f"--name={app_name}",
        "--log-level=INFO",
        "--paths=.",
    ]

    # 添加图标
    if icon_path:
        pyinstaller_args.append(f"--icon={icon_path}")

    # 添加数据文件
    data_args = [
        f"{resources_dir}:{resources_dir}",
        "templates:templates",
    ]
    for data_arg in data_args:
        pyinstaller_args.append(f"--add-data={data_arg}")

    # 防止嵌入调试信息
    pyinstaller_args.append("--strip")

    # 添加反调试措施
    # pyinstaller_args.append(
    #     "--key="
    #     + ''.join(random.choice(string.hexdigits) for _ in range(16))
    # )

    # 添加隐藏导入
    hidden_imports = [
        "tkinter",
        "PIL.Image",
        "PIL.ImageTk",
        "asyncio",
        "aiohttp",
        "configparser",
        "json",
        "threading",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.filedialog",
        "tkinter.messagebox",
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
    pyinstaller_args.append(main_script)

    # 执行 PyInstaller 命令
    print("\n开始打包...")
    print("执行打包命令: " + " ".join(pyinstaller_args))

    start_time = time.time()

    try:
        subprocess.call(pyinstaller_args)

        # 计算打包耗时
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        # 打包完成后的处理
        if os.path.exists("dist"):
            print(f"\n打包完成！耗时: {minutes}分{seconds}秒")
            print("可执行文件位于 dist 目录")

            # 复制README和使用说明
            print("正在复制说明文档...")
            if os.path.exists("README.md"):
                shutil.copy("README.md", os.path.join("dist", "使用说明.md"))

            if os.path.exists("UPDATE_NOTES_v4.0.md"):
                shutil.copy(
                    "UPDATE_NOTES_v4.0.md",
                    os.path.join("dist", "更新说明.md"),
                )

            if os.path.exists("USER_GUIDE.md"):
                shutil.copy("USER_GUIDE.md", os.path.join("dist", "用户指南.md"))

            # 创建一个默认配置文件（不含API密钥）
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
                with open(
                    os.path.join("dist", "novel_generator_config.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(clean_config, f, ensure_ascii=False, indent=2)
                print("已创建干净的配置文件（不含API密钥）")
            except Exception as e:
                print(f"创建配置文件时出错: {str(e)}")

            # 打开输出目录
            try:
                os.startfile(os.path.abspath("dist"))
            except AttributeError:
                print(f"打包结果位于: {os.path.abspath('dist')}")
        else:
            print("\n打包失败！请检查错误信息。")
    except Exception as e:
        print(f"\n打包过程中发生错误: {e}")
        import traceback

        print(traceback.format_exc())

    # 清理混淆临时文件
    if use_obfuscation and os.path.exists("obfuscated"):
        try:
            shutil.rmtree("obfuscated")
        except Exception:
            print("注意: 无法清理混淆临时目录")

    print("\n打包过程结束")


if __name__ == "__main__":
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="小说生成器打包脚本")
    parser.add_argument(
        "--skip-clean", action="store_true", help="跳过清理敏感信息步骤"
    )
    parser.add_argument("--onedir", action="store_true", help="使用文件夹模式打包")
    parser.add_argument("--onefile", action="store_true", help="使用单文件模式打包")
    args = parser.parse_args()

    # 除非明确跳过，否则清理敏感信息
    if not args.skip_clean:
        clean_sensitive_info()

    # 继续执行打包流程...
    main()
