# Repository Guidelines

## Project Structure & Module Organization
- `core/`: generation engine, models, media tools (logic only).
- `ui/`: desktop Tkinter app (`ui/app.py`), dialogs, `ui/assets/`.
- `novel_generator_app/`: Kivy variant (`novel_generator_app/main.py`, its `requirements.txt`).
- `utils/`, `templates/`, shared helpers; app icons in `resources/`.
- Examples: `example_prompts/`, `simple_demo.py`, `demo_media_generation.py`.
- Tests live at repo root as `test_*.py` (e.g., `test_media_generation.py`). Entrypoints: `main.py`, `ui/app.py`, `novel_generator_app/main.py`.

## Build, Test, and Development Commands
- Create venv (Windows): `python -m venv .venv && .\.venv\Scripts\activate`
- Install deps: `pip install -r requirements.txt`
- Run desktop UI: `python main.py` (or `python ui/app.py`)
- Run Kivy app: `pip install -r novel_generator_app/requirements.txt && python novel_generator_app/main.py`
- Tests: `pytest -q`
- Format: `black .`
- Package (PyInstaller): use provided `*.spec` ensuring `core/`, `utils/`, `templates/`, `ui/`, `resources/` are included.

## Coding Style & Naming Conventions
- Python 3, PEP 8, 4-space indent, prefer type hints where helpful.
- Naming: modules/functions `snake_case`; classes `PascalCase`; constants `UPPER_CASE`.
- Keep modules focused and side-effect free; small, testable functions in `core/` and `utils/`.
- Sort imports logically; run `black .` before PRs.

## Testing Guidelines
- Framework: `pytest` with files named `test_*.py` at repo root or next to code.
- Prefer deterministic tests; mock external APIs/models and filesystem where needed.
- Add/adjust tests for any feature or bug fix touching behavior.

## Commit & Pull Request Guidelines
- Commits: concise imperative subject (≤72 chars) + brief context. Link issues (e.g., `Fixes #123`).
- PRs: purpose, repro steps, screenshots for UI, test notes, and scope-limited changes. Update docs/config when behavior changes.

## Versioning & Release
- Bump `templates/prompts.py::__version__` with any code change; UI titles reference `v{__version__}`.
- Keep spec/doc versions aligned (e.g., `AI…_v5.0.2.spec`, `PACKAGING_GUIDE_v5.0.2.md`).
- If frozen build misses imports, add `hiddenimports` for `core.*`, `utils.*`, `templates.*`, `ui.*` in the spec.

## Security & Configuration
- Never commit secrets; use env vars or a locally ignored JSON.
- Centralize runtime settings in `utils/config.py`; validate paths/model IDs in `core/` before long tasks.

