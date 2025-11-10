import os
import sys
import logging
import traceback
import importlib
import importlib.machinery
import importlib.util
from typing import Iterable, Optional, Sequence

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

current_dir = os.path.dirname(os.path.abspath(__file__))


def _expand_with_parents(path: str, depth: int = 2) -> Iterable[str]:
    """Generate ``path`` and up to ``depth`` parent directories."""

    current = os.path.abspath(path)
    for _ in range(depth + 1):
        if current:
            yield current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent


def _collect_bootstrap_paths() -> Iterable[str]:
    """Collect directories/archives that may host project modules."""

    roots = [
        base_dir,
        current_dir,
        os.getcwd(),
        os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else '',
        os.path.dirname(sys.executable) if hasattr(sys, 'executable') else '',
    ]

    for root in roots:
        if not root:
            continue
        for candidate in _expand_with_parents(root, depth=3):
            yield candidate
            for sub in ("novel_generator", "ui", "core", "utils", "templates", "lib"):
                yield os.path.join(candidate, sub)
            if os.path.isdir(candidate):
                library_zip = os.path.join(candidate, "library.zip")
                if os.path.isfile(library_zip):
                    yield library_zip
                try:
                    entries = os.listdir(candidate)
                except OSError:
                    entries = []
                for entry in entries:
                    if entry.lower().endswith((".zip", ".pkg")):
                        yield os.path.join(candidate, entry)


for bootstrap_path in _iter_unique_paths(_collect_bootstrap_paths()):
    if bootstrap_path not in sys.path:
        sys.path.insert(0, bootstrap_path)
        logger.info(f"注入路径到 sys.path: {bootstrap_path}")


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


def _locate_module_spec(
    module_name: str, search_roots: Sequence[str]
) -> Optional[importlib.machinery.ModuleSpec]:
    """Find a module spec using PathFinder against explicit search roots."""

    for root in search_roots:
        if not root:
            continue
        try:
            spec = importlib.machinery.PathFinder.find_spec(module_name, [root])
        except ImportError:
            continue
        if spec is not None:
            return spec
    return None


def _import_ui_module() -> type:
    module_candidates = ('ui.app', 'novel_generator.ui.app')
    search_roots = list(
        _iter_unique_paths(
            list(_collect_bootstrap_paths())
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
            spec = _locate_module_spec(module_name, search_roots)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                loader = spec.loader
                assert loader is not None
                try:
                    sys.modules[module_name] = module
                    loader.exec_module(module)
                    logger.info(f"通过路径发现导入UI模块: {module_name}")
                    return module.NovelGeneratorApp
                except Exception as retry_exc:  # pragma: no cover - propagate runtime issues
                    last_error = retry_exc
                    logger.debug("模块通过 spec 加载失败: %s", retry_exc)
                    continue
                finally:
                    if module_name in sys.modules and not hasattr(
                        sys.modules[module_name], "NovelGeneratorApp"
                    ):
                        sys.modules.pop(module_name, None)
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

