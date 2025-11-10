# -*- mode: python ; coding: utf-8 -*-
# fmt: off
# flake8: noqa
# mypy: ignore-errors
"""
PyInstaller spec file for AI Novel Generator
Ensures all modules (ui, core, utils, templates) are properly included.
"""

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all submodules and data for core packages
ui_datas, ui_binaries, ui_hiddenimports = collect_all("ui")
core_datas, core_binaries, core_hiddenimports = collect_all("core")
utils_datas, utils_binaries, utils_hiddenimports = collect_all("utils")
templates_datas, templates_binaries, templates_hiddenimports = (
    collect_all("templates")
)
ng_datas, ng_binaries, ng_hiddenimports = collect_all("novel_generator")

# Explicitly list all submodules to ensure they're included
explicit_hiddenimports = [
    # Standard library and dependencies
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
    # Top-level imports (direct)
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
    # novel_generator namespace aliases
    "novel_generator",
    "novel_generator.ui",
    "novel_generator.ui.app",
    "novel_generator.ui.dialogs",
    "novel_generator.core",
    "novel_generator.core.generator",
    "novel_generator.core.media_generator",
    "novel_generator.core.media_task_manager",
    "novel_generator.core.model_manager",
    "novel_generator.core.sanqianliu_generator",
    "novel_generator.core.sanqianliu_interface",
    "novel_generator.utils",
    "novel_generator.utils.common",
    "novel_generator.utils.config",
    "novel_generator.utils.quality",
    "novel_generator.templates",
    "novel_generator.templates.prompts",
]

# Combine all hidden imports
all_hiddenimports = sorted(
    set(
        explicit_hiddenimports
        + ui_hiddenimports
        + core_hiddenimports
        + utils_hiddenimports
        + templates_hiddenimports
        + ng_hiddenimports
    )
)

# Data files to include
datas = [
    ("resources", "resources"),
    ("templates", "templates"),
    ("ui/assets", "ui/assets") if os.path.exists("ui/assets") else None,
]
# Filter out None entries
datas = [d for d in datas if d is not None]

# Combine with collected data
datas.extend(ui_datas)
datas.extend(core_datas)
datas.extend(utils_datas)
datas.extend(templates_datas)
datas.extend(ng_datas)

# Binary files
binaries = []
binaries.extend(ui_binaries)
binaries.extend(core_binaries)
binaries.extend(utils_binaries)
binaries.extend(templates_binaries)
binaries.extend(ng_binaries)

# Analysis step
a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AI_Novel_Generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="resources/icon.ico" if os.path.exists("resources/icon.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name="AI_Novel_Generator",
)
