import os
import sys
import logging
import traceback
import importlib.util

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('novel_generator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("novel_generator")

# 记录启动信息
logger.info(f"当前工作目录: {os.getcwd()}")

# 检测是否在 PyInstaller 冻结环境
is_frozen = getattr(sys, 'frozen', False)
if is_frozen:
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    logger.info(f"运行于打包环境，基准目录: {base_dir}")
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"运行于开发环境，基准目录: {base_dir}")

# 注入常见路径（尽量不依赖于磁盘目录以便 PyInstaller 的 PyiImporter 工作）
current_dir = os.path.dirname(os.path.abspath(__file__))
paths_to_add = [
    base_dir,
    os.path.join(base_dir, 'novel_generator'),
    current_dir,
]
for path in paths_to_add:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        logger.info(f"注入路径到 sys.path: {path}")

# 尝试加载 ctypes 设置 Windows AppID（可选）
try:
    import ctypes
    if sys.platform.startswith('win'):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('novel_generator.app')
            logger.info("已设置 Windows 应用 ID")
        except Exception as e:
            logger.warning(f"设置 Windows 应用 ID 失败: {e}")
except ImportError:
    logger.warning("无法导入 ctypes 模块")

# 探测模块可见性（日志用）
def check_module(module_name: str) -> bool:
    try:
        spec = importlib.util.find_spec(module_name)
        ok = spec is not None
        logger.info(("可见" if ok else "不可见") + f"模块: {module_name}")
        return ok
    except Exception as e:
        logger.error(f"探测模块 {module_name} 出错: {e}")
        return False

check_module('ui.app')
check_module('novel_generator.ui.app')

# 导入 UI（优先 ui.app，其次 novel_generator.ui.app）
try:
    try:
        from ui.app import NovelGeneratorApp
        logger.info("成功导入UI模块: ui.app")
    except Exception:
        from novel_generator.ui.app import NovelGeneratorApp
        logger.info("成功导入UI模块: novel_generator.ui.app")
except Exception as e:
    logger.error(f"无法导入UI模块: {traceback.format_exc()}")
    print("抱歉，无法导入UI模块")
    print(f"错误详情: {e}")
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("启动失败", f"无法导入UI模块:\n{e}")
    except Exception:
        pass
    try:
        if sys.stdin and sys.stdin.isatty():
            input("按Enter键退出...")
    except Exception:
        pass
    sys.exit(1)

def main():
    """应用入口，启动 GUI 应用"""
    import tkinter as tk
    from tkinter import messagebox

    logger.info("AI小说生成器启动中…")
    try:
        root = tk.Tk()
        # 默认窗口尺寸
        root.geometry("1280x860")
        root.minsize(1200, 800)

        # 设置窗口图标（可选）
        try:
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "resources", "icon.ico"),
                os.path.join(base_dir, "resources", "icon.ico"),
                "resources/icon.ico",
            ]
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    root.iconbitmap(icon_path)
                    logger.info(f"使用应用图标: {icon_path}")
                    break
        except Exception as e:
            logger.warning(f"设置应用图标失败: {e}")

        app = NovelGeneratorApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        logger.info("应用UI初始化完成")

        root.mainloop()
        logger.info("应用已关闭")
    except Exception as e:
        error_msg = f"应用运行异常: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        try:
            messagebox.showerror("错误", error_msg)
        except Exception:
            print(error_msg)
        try:
            if sys.stdin and sys.stdin.isatty():
                input("按Enter键退出...")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()

