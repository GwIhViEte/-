import os, sys
base_dir = os.path.dirname(os.path.abspath('main.py'))
paths_to_add = [
    os.path.dirname(base_dir),  # parent_dir
    os.path.join(base_dir, 'ui'),
    os.path.join(base_dir, 'core'),
    os.path.join(base_dir, 'utils'),
    os.path.join(base_dir, 'templates'),
    os.path.dirname(os.path.abspath('main.py')),  # current_dir
]
for p in paths_to_add:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)
print('sys.path head:', sys.path[:6])
import importlib
print('pre sys.modules has novel_generator:', 'novel_generator' in sys.modules)
print('pre sys.modules has novel_generator.ui:', 'novel_generator.ui' in sys.modules)
try:
    m = importlib.import_module('novel_generator.ui.app')
    print('module file:', m.__file__)
except Exception as e:
    print('import error:', e)
    import traceback; traceback.print_exc()
