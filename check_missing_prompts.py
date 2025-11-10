# -*- coding: utf-8 -*-
from templates.prompts import NOVEL_TYPES, GENRE_SPECIFIC_PROMPTS

chinese_types = NOVEL_TYPES['中文']
existing_prompts = set(GENRE_SPECIFIC_PROMPTS.keys())
missing_types = [t for t in chinese_types if t not in existing_prompts]

print(f'已有提示词的类型数量: {len(existing_prompts)}')
print(f'总类型数量: {len(chinese_types)}')
print(f'缺失提示词的类型数量: {len(missing_types)}')
print()
print('缺失提示词的类型:')
for i, t in enumerate(missing_types, 1):
    print(f'{i:2d}. {t}')
    
print()
print('已有提示词的类型:')
for i, t in enumerate(sorted(existing_prompts), 1):
    print(f'{i:2d}. {t}')