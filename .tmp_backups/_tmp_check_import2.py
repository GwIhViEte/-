import importlib
m = importlib.import_module("ui.app")
print('Has NovelGeneratorApp:', hasattr(m, 'NovelGeneratorApp'))
print('Has run_asyncio_event_loop:', hasattr(m, 'run_asyncio_event_loop'))
from ui.app import NovelGeneratorApp
print('Direct import NovelGeneratorApp works:', bool(NovelGeneratorApp))
