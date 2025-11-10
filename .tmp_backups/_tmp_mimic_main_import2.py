import os, sys
base_dir = os.path.dirname(os.path.abspath('main.py'))
paths_to_add = [
    os.path.dirname(os.path.abspath('main.py')),
    os.path.dirname(base_dir),
    os.path.join(base_dir, 'ui'),
    os.path.join(base_dir, 'core'),
    os.path.join(base_dir, 'utils'),
    os.path.join(base_dir, 'templates'),
]
for p in paths_to_add:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)
try:
    from novel_generator.ui.app import NovelGeneratorApp
    print('OK novel_generator.ui.app')
except Exception as e:
    print('FAIL novel_generator.ui.app:', e)
try:
    from ui.app import NovelGeneratorApp as NG
    print('OK ui.app (wrapper)')
except Exception as e:
    print('FAIL ui.app wrapper:', e)
