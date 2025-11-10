"""Compatibility helpers for the ``novel_generator`` namespace.

This package bridges the repository's source layout (where modules such as
``core`` and ``ui`` live at the project root) with frozen distributions that
expect imports like ``novel_generator.ui.app``. It installs a lightweight import
aliaser so both styles work consistently.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Optional, Set

# Ensure the project root is importable even when running from a frozen bundle.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Modules/packages that should be reachable via the ``novel_generator`` prefix.
_ALIAS_ROOTS: Set[str] = {
    "core",
    "ui",
    "utils",
    "templates",
    "main",
    "main_wrapper",
}


class _AliasLoader(Loader):
    """Loader that proxies ``novel_generator.*`` imports to top-level modules."""

    def __init__(self, fullname: str, target: str) -> None:
        self.fullname = fullname
        self.target = target

    def create_module(self, spec: ModuleSpec):  # type: ignore[override]
        # Defer to the default module creation machinery. We replace the module
        # reference during ``exec_module``.
        return None

    def exec_module(self, module) -> None:  # type: ignore[override]
        target_module = importlib.import_module(self.target)
        sys.modules[self.fullname] = target_module

        parent_name, _, attr = self.fullname.rpartition(".")
        if parent_name == __name__:
            setattr(sys.modules[parent_name], attr, target_module)


class _AliasFinder(MetaPathFinder):
    """Meta path finder that exposes top-level modules under a namespace."""

    def find_spec(  # type: ignore[override]
        self, fullname: str, path, target=None
    ) -> Optional[ModuleSpec]:
        if not fullname.startswith(__name__ + "."):
            return None

        tail = fullname[len(__name__) + 1 :]
        root = tail.split(".", 1)[0]
        if root not in _ALIAS_ROOTS:
            return None

        target_spec = importlib.util.find_spec(tail)
        if target_spec is None:
            return None

        loader = _AliasLoader(fullname, tail)
        is_package = target_spec.submodule_search_locations is not None
        spec = ModuleSpec(fullname, loader, is_package=is_package)

        if is_package:
            spec.submodule_search_locations = target_spec.submodule_search_locations
        spec.origin = target_spec.origin
        return spec


if not any(isinstance(finder, _AliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())

__all__ = tuple(sorted(_ALIAS_ROOTS))


def __getattr__(name: str):
    if name in _ALIAS_ROOTS:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
