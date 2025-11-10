from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
import os

# 导入现有核心功能
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 配置中文字体
def configure_chinese_font():
    # Windows下的字体路径
    if platform == 'win':
        font_paths = [
            "C:/Windows/Fonts",  # 标准Windows字体路径
        ]
        font_files = {
            'SimSun': 'simsun.ttc',  # 宋体
            'Microsoft YaHei': 'msyh.ttc',  # 微软雅黑
            'SimHei': 'simhei.ttf',  # 黑体
        }
        
        # 尝试注册字体
        for font_path in font_paths:
            resource_add_path(font_path)
            for font_name, font_file in font_files.items():
                try:
                    font_file_path = os.path.join(font_path, font_file)
                    if os.path.exists(font_file_path):
                        LabelBase.register(font_name, font_file_path)
                        print(f"字体注册成功: {font_name}")
                except Exception as e:
                    print(f"字体注册失败 {font_name}: {str(e)}")

        # 设置默认字体为宋体
        LabelBase.register(DEFAULT_FONT, os.path.join(font_paths[0], font_files['SimSun']))
    
    # Android平台
    elif platform == 'android':
        from jnius import autoclass
        Environment = autoclass('android.os.Environment')
        # Android上的字体路径
        font_path = Environment.getExternalStorageDirectory().getPath() + '/fonts/'
        if os.path.exists(font_path):
            resource_add_path(font_path)
            # 在Android上可能需要放置自定义字体到此目录

# 导入我们的屏幕
from ui.screens.main_screen import MainScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.generation_screen import GenerationScreen

class NovelGeneratorApp(App):
    version = StringProperty("5.0.5")
    
    def build(self):
        # 配置中文字体
        configure_chinese_font()
        
        # 设置窗口大小（仅在桌面平台有效）
        if platform not in ('android', 'ios'):
            Window.size = (480, 800)
        
        # 创建屏幕管理器
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(GenerationScreen(name='generation'))
        
        return sm

if __name__ == '__main__':
    NovelGeneratorApp().run() 