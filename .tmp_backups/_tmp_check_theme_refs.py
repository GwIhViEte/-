p = 'novel_generator/ui/modern_theme.py'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    s = f.read()
for key in ['from ui', 'import ui', 'from .app', 'ui.app']:
    print(key + ':', (key in s))
