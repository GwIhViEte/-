import importlib
try:
    import main  # will run import path setup and try to import NovelGeneratorApp
    print('Imported main OK')
except Exception as e:
    print('Import main failed:', e)
