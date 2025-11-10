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
print('sys.path order (first 5):', sys.path[:5])
try:
    import importlib
    m = importlib.import_module('ui.app')
    print('Imported ui.app as', m.__file__)
    # After import, inspect what novel_generator resolves to
    for name in ['novel_generator', 'novel_generator.ui', 'novel_generator.ui.app']:
        mod = sys.modules.get(name)
        print(name, '->', getattr(mod, '__file__', None))
except Exception as e:
    print('Error during import:', e)
    import traceback; traceback.print_exc()
