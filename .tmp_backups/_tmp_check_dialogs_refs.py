import re
p = 'novel_generator/ui/dialogs.py'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    s = f.read()
print('references to ui.app:', 'ui.app' in s)
print('references to from ui import:', bool(re.search(r'from\s+ui\.', s)))
print('references to from .app import:', bool(re.search(r'from\s+\.app\s+import', s)))
print('references to import ui:', bool(re.search(r'\bimport\s+ui\b', s)))
