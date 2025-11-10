import re
p = 'novel_generator/ui/app.py'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    s = f.read()
print('__all__ present:', bool(re.search(r'^__all__\s*=\s*\[', s, re.M)))
print('NovelGeneratorApp defined:', bool(re.search(r'class\s+NovelGeneratorApp\b', s)))
