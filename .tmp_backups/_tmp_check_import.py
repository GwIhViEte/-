import importlib
m = importlib.import_module("ui.app")
print('Imported ui.app OK; has run_asyncio_event_loop:', hasattr(m, 'run_asyncio_event_loop'))
print('Has NovelGeneratorApp:', hasattr(m, 'NovelGeneratorApp'))
md = importlib.import_module("ui.dialogs")
print('Imported ui.dialogs OK')
