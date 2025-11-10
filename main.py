import os
import sys
import logging
import traceback
import importlib
import importlib.util
from typing import Iterable, Optional

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
    os.path.join(base_dir, 'lib'),
    os.path.join(base_dir, 'library.zip'),
    os.path.dirname(sys.executable) if hasattr(sys, 'executable') else '',
    current_dir,
    os.getcwd(),
]
for path in paths_to_add:
    if not path:
        continue
    normalized_path = os.path.abspath(path)
    if os.path.exists(normalized_path) and normalized_path not in sys.path:
        sys.path.insert(0, normalized_path)
        logger.info(f"注入路径到 sys.path: {normalized_path}")


def _iter_unique_paths(paths: Iterable[str]) -> Iterable[str]:
    """Yield unique, existing absolute paths while preserving order."""

    seen = set()
    for path in paths:
        if not path:
            continue
        normalized = os.path.abspath(path)
        if not os.path.exists(normalized):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        yield normalized


def _locate_module_root(module_name: str, search_roots: Iterable[str]) -> Optional[str]:
    """Try to find a sys.path entry that contains the requested module."""

    parts = module_name.split('.')
    relative_dir = os.path.join(*parts[:-1]) if len(parts) > 1 else ''
    module_file_stem = parts[-1]
    filenames = [module_file_stem + ext for ext in ('.py', '.pyc', '.pyo')]

    for root in search_roots:
        if not root:
            continue
        candidate_dir = os.path.join(root, relative_dir)
        if os.path.isdir(candidate_dir):
            for name in filenames:
                if os.path.isfile(os.path.join(candidate_dir, name)):
                    return os.path.abspath(root)
        for name in filenames:
            candidate_file = os.path.join(root, relative_dir, name)
            if os.path.isfile(candidate_file):
                return os.path.abspath(root)
    return None


def _import_ui_module() -> type:
    module_candidates = ('ui.app', 'novel_generator.ui.app')
    search_roots = list(
        _iter_unique_paths(
            [
                base_dir,
                current_dir,
                os.getcwd(),
                os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else '',
                os.path.dirname(sys.executable) if hasattr(sys, 'executable') else '',
            ]
        )
    )

    last_error: Optional[BaseException] = None
    importlib.invalidate_caches()

    for module_name in module_candidates:
        try:
            module = importlib.import_module(module_name)
            logger.info(f"成功导入UI模块: {module_name}")
            return module.NovelGeneratorApp
        except ModuleNotFoundError as exc:
            logger.warning(f"直接导入 {module_name} 失败: {exc}")
            module_root = _locate_module_root(module_name, search_roots)
            if module_root:
                normalized_root = os.path.abspath(module_root)
            else:
                normalized_root = None
            if normalized_root and normalized_root not in sys.path:
                sys.path.insert(0, normalized_root)
                logger.info(f"动态注入路径到 sys.path: {normalized_root}")
            if normalized_root:
                importlib.invalidate_caches()
                try:
                    module = importlib.import_module(module_name)
                    logger.info(f"通过文件系统导入UI模块: {module_name}")
                    return module.NovelGeneratorApp
                except ModuleNotFoundError as retry_exc:
                    last_error = retry_exc
                    logger.debug(
                        "模块在文件系统中找到，但导入仍失败: %s", retry_exc
                    )
                    continue
            last_error = exc
        except Exception as exc:  # pragma: no cover - propagate unexpected import errors
            logger.error(f"导入 {module_name} 时出现异常: {traceback.format_exc()}")
            raise

    if last_error is None:
        last_error = ModuleNotFoundError('未能定位到 UI 模块')
    raise last_error

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
    except ModuleNotFoundError:
        logger.info(f"不可见模块: {module_name}")
        return False
    except Exception as e:
        logger.error(f"探测模块 {module_name} 出错: {e}")
        return False

check_module('ui.app')
check_module('novel_generator.ui.app')

# 导入 UI（优先 ui.app，其次 novel_generator.ui.app）
try:
    NovelGeneratorApp = _import_ui_module()
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

