import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List, Callable

# 修复导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# 导入路径兼容：相对、包名、目录直导、模块直导
try:
    from ..templates.prompts import GENRE_SPECIFIC_PROMPTS, MODEL_DESCRIPTIONS, __version__, __author__
    from ..utils.config import save_config
except Exception:
    try:
        from novel_generator.templates.prompts import GENRE_SPECIFIC_PROMPTS, MODEL_DESCRIPTIONS, __version__, __author__
        from novel_generator.utils.config import save_config
    except Exception:
        try:
            from templates.prompts import GENRE_SPECIFIC_PROMPTS, MODEL_DESCRIPTIONS, __version__, __author__
            from utils.config import save_config
        except Exception:
            from prompts import GENRE_SPECIFIC_PROMPTS, MODEL_DESCRIPTIONS, __version__, __author__
            from config import save_config
class AdvancedSettingsDialog(tk.Toplevel):
    """高级设置对话框"""
    def __init__(self, parent, temperature=0.7, top_p=0.9, max_tokens=8000, context_length=240000, 
                 autosave_interval=60, auto_summary=True, auto_summary_interval=10000, language="中文",
                 creativity=0.7, formality=0.5, detail_level=0.6, writing_style="平衡",
                 paragraph_length_preference="适中", dialogue_frequency="适中"):
        super().__init__(parent)
        self.parent = parent
        self.title("高级设置")
        self.geometry("800x700")  # 增加窗口高度
        self.resizable(True, True)  # 允许调整大小
        self.transient(parent)
        self.grab_set()
        
        # 设置最小窗口大小
        self.minsize(750, 650)
        
        self.temperature = tk.DoubleVar(value=temperature)
        self.top_p = tk.DoubleVar(value=top_p)
        self.max_tokens = tk.IntVar(value=max_tokens)
        self.context_length = tk.IntVar(value=context_length)
        self.autosave_interval = tk.IntVar(value=autosave_interval)
        self.auto_summary = tk.BooleanVar(value=auto_summary)
        self.auto_summary_interval = tk.IntVar(value=auto_summary_interval)
        self.language = language
        
        # 添加新的设置变量
        self.creativity = tk.DoubleVar(value=creativity)
        self.formality = tk.DoubleVar(value=formality)
        self.detail_level = tk.DoubleVar(value=detail_level)
        self.writing_style = tk.StringVar(value=writing_style)
        
        # 添加排版选项变量
        self.paragraph_length_preference = tk.StringVar(value=paragraph_length_preference)
        self.dialogue_frequency = tk.StringVar(value=dialogue_frequency)
        
        self.result = None
        self.create_widgets()
        
    def create_widgets(self):
        """创建对话框控件"""
        # 创建带滚动条的主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 设置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 创建窗口并配置画布
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 放置画布和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建内容区域
        content = ttk.Frame(scrollable_frame, padding=10)
        content.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(content, text="高级生成参数设置", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Temperature
        ttk.Label(content, text="Temperature（温度）:").grid(row=1, column=0, sticky="w", pady=5)
        temp_scale = ttk.Scale(content, from_=0.1, to=2.0, orient=tk.HORIZONTAL, 
                              variable=self.temperature, length=300,
                              command=lambda x: self.update_value_label('temperature'))
        temp_scale.grid(row=1, column=1, pady=5, sticky="ew")
        self.temp_label = ttk.Label(content, text=f"{self.temperature.get():.2f}")
        self.temp_label.grid(row=1, column=2, padx=5, sticky="w")
        ttk.Label(content, text="控制随机性，较高值产生更有创意但可能离题的内容").grid(row=2, column=1, sticky="w")
        
        # Top P
        ttk.Label(content, text="Top P（核采样）:").grid(row=3, column=0, sticky="w", pady=5)
        top_p_scale = ttk.Scale(content, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                              variable=self.top_p, length=300,
                              command=lambda x: self.update_value_label('top_p'))
        top_p_scale.grid(row=3, column=1, pady=5, sticky="ew")
        self.top_p_label = ttk.Label(content, text=f"{self.top_p.get():.2f}")
        self.top_p_label.grid(row=3, column=2, padx=5, sticky="w")
        ttk.Label(content, text="控制输出随机性，较低值产生更聚焦的内容").grid(row=4, column=1, sticky="w")
        
        # Max Tokens
        ttk.Label(content, text="Max Tokens（生成长度）:").grid(row=5, column=0, sticky="w", pady=5)
        max_tokens_scale = ttk.Scale(content, from_=1000, to=8000, orient=tk.HORIZONTAL, 
                                   variable=self.max_tokens, length=300,
                                   command=lambda x: self.update_value_label('max_tokens'))
        max_tokens_scale.grid(row=5, column=1, pady=5, sticky="ew")
        self.max_tokens_label = ttk.Label(content, text=f"{self.max_tokens.get()}")
        self.max_tokens_label.grid(row=5, column=2, padx=5, sticky="w")
        ttk.Label(content, text="每次调用API生成的最大文本长度").grid(row=6, column=1, sticky="w")
        
        # Context Length
        ttk.Label(content, text="Context Length（上下文长度）:").grid(row=7, column=0, sticky="w", pady=5)
        context_scale = ttk.Scale(content, from_=10000, to=200000, orient=tk.HORIZONTAL, 
                               variable=self.context_length, length=300,
                               command=lambda x: self.update_value_label('context_length'))
        context_scale.grid(row=7, column=1, pady=5, sticky="ew")
        self.context_length_label = ttk.Label(content, text=f"{self.context_length.get()}")
        self.context_length_label.grid(row=7, column=2, padx=5, sticky="w")
        ttk.Label(content, text="发送给API的上下文总长度").grid(row=8, column=1, sticky="w")
        
        # 自动保存间隔
        ttk.Label(content, text="自动保存间隔（秒）:").grid(row=9, column=0, sticky="w", pady=5)
        autosave_scale = ttk.Scale(content, from_=10, to=300, orient=tk.HORIZONTAL, 
                                 variable=self.autosave_interval, length=300,
                                 command=lambda x: self.update_value_label('autosave_interval'))
        autosave_scale.grid(row=9, column=1, pady=5, sticky="ew")
        self.autosave_interval_label = ttk.Label(content, text=f"{self.autosave_interval.get()}")
        self.autosave_interval_label.grid(row=9, column=2, padx=5, sticky="w")
        ttk.Label(content, text="自动保存小说的时间间隔").grid(row=10, column=1, sticky="w")
        
        # 自动摘要设置
        summary_frame = ttk.LabelFrame(content, text="自动摘要设置")
        summary_frame.grid(row=11, column=0, columnspan=3, sticky="ew", pady=10)
        
        auto_summary_check = ttk.Checkbutton(summary_frame, text="启用自动摘要", 
                                          variable=self.auto_summary)
        auto_summary_check.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        ttk.Label(summary_frame, text="摘要间隔（字数）:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        summary_interval_entry = ttk.Spinbox(
            summary_frame,
            from_=2000,
            to=50000,
            increment=1000,
            width=10,
            textvariable=self.auto_summary_interval,
            command=lambda: self.update_value_label('auto_summary_interval')
        )
        summary_interval_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.auto_summary_interval_label = ttk.Label(summary_frame, text=f"{self.auto_summary_interval.get()}")
        self.auto_summary_interval_label.grid(row=1, column=2, padx=5, sticky="w")
        
        # 创意与风格设置
        style_frame = ttk.LabelFrame(content, text="创意与风格设置")
        style_frame.grid(row=12, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 创意度设置
        ttk.Label(style_frame, text="创意度:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        creativity_scale = ttk.Scale(style_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                                   variable=self.creativity, length=300,
                                   command=lambda x: self.update_value_label('creativity'))
        creativity_scale.grid(row=0, column=1, pady=5, sticky="ew")
        self.creativity_label = ttk.Label(style_frame, text=f"{self.creativity.get():.2f}")
        self.creativity_label.grid(row=0, column=2, padx=5, sticky="w")
        ttk.Label(style_frame, text="控制生成内容的创意程度，值越高创意越丰富").grid(row=1, column=1, sticky="w")
        
        # 正式度设置
        ttk.Label(style_frame, text="正式度:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        formality_scale = ttk.Scale(style_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                                  variable=self.formality, length=300,
                                  command=lambda x: self.update_value_label('formality'))
        formality_scale.grid(row=2, column=1, pady=5, sticky="ew")
        self.formality_label = ttk.Label(style_frame, text=f"{self.formality.get():.2f}")
        self.formality_label.grid(row=2, column=2, padx=5, sticky="w")
        ttk.Label(style_frame, text="控制文风的正式程度，值越高越正式").grid(row=3, column=1, sticky="w")
        
        # 细节程度设置
        ttk.Label(style_frame, text="细节程度:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        detail_scale = ttk.Scale(style_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                               variable=self.detail_level, length=300,
                               command=lambda x: self.update_value_label('detail_level'))
        detail_scale.grid(row=4, column=1, pady=5, sticky="ew")
        self.detail_level_label = ttk.Label(style_frame, text=f"{self.detail_level.get():.2f}")
        self.detail_level_label.grid(row=4, column=2, padx=5, sticky="w")
        ttk.Label(style_frame, text="控制生成内容的细节丰富程度").grid(row=5, column=1, sticky="w")
        
        # 写作风格设置
        ttk.Label(style_frame, text="写作风格:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        
        # 创建写作风格选择框
        style_combo = ttk.Combobox(style_frame, textvariable=self.writing_style, width=20)
        writing_styles = ["平衡", "严谨学术", "轻松幽默", "文学性", "简洁直接", "细腻描写", "戏剧性"]
        style_combo['values'] = writing_styles
        style_combo.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(style_frame, text="选择整体写作风格").grid(row=7, column=1, sticky="w")
        
        # 高级排版选项
        layout_frame = ttk.LabelFrame(content, text="排版选项")
        layout_frame.grid(row=13, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 段落长度选项
        ttk.Label(layout_frame, text="段落长度倾向:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.paragraph_style = ttk.Combobox(layout_frame, width=20, textvariable=self.paragraph_length_preference)
        self.paragraph_style['values'] = ["适中", "短小精悍", "较长段落"]
        self.paragraph_style.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 对话频率选项
        ttk.Label(layout_frame, text="对话频率:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.dialogue_style = ttk.Combobox(layout_frame, width=20, textvariable=self.dialogue_frequency)
        self.dialogue_style['values'] = ["适中", "对话较少", "对话较多"]
        self.dialogue_style.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # 创建底部按钮区域（放在主窗口而非滚动区域内）
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10, padx=10)
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="确定", command=self.on_ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.destroy_safely, width=10)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 恢复默认设置按钮
        reset_button = ttk.Button(button_frame, text="恢复默认", command=self.reset_defaults, width=10)
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # 初始更新所有值标签
        self.update_value_label('temperature')
        self.update_value_label('top_p')
        self.update_value_label('max_tokens')
        self.update_value_label('context_length')
        self.update_value_label('autosave_interval')
        self.update_value_label('auto_summary_interval')
        self.update_value_label('creativity')
        self.update_value_label('formality')
        self.update_value_label('detail_level')
        
    def update_value_label(self, var_name):
        """更新数值标签显示"""
        if var_name == 'temperature':
            self.temp_label.config(text=f"{self.temperature.get():.2f}")
        elif var_name == 'top_p':
            self.top_p_label.config(text=f"{self.top_p.get():.2f}")
        elif var_name == 'max_tokens':
            self.max_tokens_label.config(text=f"{self.max_tokens.get()}")
        elif var_name == 'context_length':
            self.context_length_label.config(text=f"{self.context_length.get()}")
        elif var_name == 'autosave_interval':
            self.autosave_interval_label.config(text=f"{self.autosave_interval.get()}")
        elif var_name == 'auto_summary_interval':
            self.auto_summary_interval_label.config(text=f"{self.auto_summary_interval.get()}")
        elif var_name == 'creativity':
            self.creativity_label.config(text=f"{self.creativity.get():.2f}")
        elif var_name == 'formality':
            self.formality_label.config(text=f"{self.formality.get():.2f}")
        elif var_name == 'detail_level':
            self.detail_level_label.config(text=f"{self.detail_level.get():.2f}")
    
    def reset_defaults(self):
        """重置所有设置为默认值"""
        # 重置基本设置
        self.temperature.set(0.8)
        self.top_p.set(0.9)
        self.max_tokens.set(4000)
        self.context_length.set(100000)
        self.autosave_interval.set(60)
        
        # 重置摘要设置
        self.auto_summary.set(True)
        self.auto_summary_interval.set(10000)
        
        # 重置创意与风格设置
        self.creativity.set(0.7)
        self.formality.set(0.5)
        self.detail_level.set(0.6)
        self.writing_style.set("平衡")
        
        # 重置排版选项
        self.paragraph_length_preference.set("适中")
        self.dialogue_frequency.set("适中")
        
        # 更新所有显示
        self.update_value_label('temperature')
        self.update_value_label('top_p')
        self.update_value_label('max_tokens')
        self.update_value_label('context_length')
        self.update_value_label('autosave_interval')
        self.update_value_label('auto_summary_interval')
        self.update_value_label('creativity')
        self.update_value_label('formality')
        self.update_value_label('detail_level')
        
        messagebox.showinfo("重置成功", "已恢复所有设置为默认值")
    
    def on_ok(self):
        """确定按钮点击处理"""
        self.result = {
            "temperature": self.temperature.get(),
            "top_p": self.top_p.get(),
            "max_tokens": self.max_tokens.get(),
            "context_length": self.context_length.get(),
            "autosave_interval": self.autosave_interval.get(),
            "auto_summary": self.auto_summary.get(),
            "auto_summary_interval": self.auto_summary_interval.get(),
            "creativity": self.creativity.get(),
            "formality": self.formality.get(),
            "detail_level": self.detail_level.get(),
            "writing_style": self.writing_style.get(),
            # 添加排版选项
            "paragraph_length_preference": self.paragraph_length_preference.get(),
            "dialogue_frequency": self.dialogue_frequency.get()
        }
        self.destroy_safely()
        
    def show(self):
        """显示对话框并等待结果"""
        self.wait_window()
        return self.result

    def destroy_safely(self):
        """安全地销毁窗口"""
        try:
            self.destroy()
        except:
            # 如果标准destroy失败，尝试强制关闭
            if self.winfo_exists():
                self.quit()
                self.withdraw()

class AboutDialog(tk.Toplevel):
    """关于对话框"""
    def __init__(self, parent, language="中文"):
        super().__init__(parent)
        self.parent = parent
        
        if language == "中文":
            self.title("关于")
        else:
            self.title("About")
            
        self.geometry("400x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.language = language
        self.create_widgets()
        
    def create_widgets(self):
        """创建对话框控件"""
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 版本信息
        if self.language == "中文":
            ttk.Label(frame, text=f"AI小说生成器 v{__version__}", font=("Arial", 16, "bold")).pack(pady=10)
            ttk.Label(frame, text=f"作者: {__author__}", font=("Arial", 10)).pack()
            ttk.Label(frame, text="版权所有 © 2024", font=("Arial", 10)).pack(pady=5)
            
            ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
            
            info_text = "这是一个AI驱动的小说生成器，可以创建各种类型的小说。\n"
            info_text += "使用先进的人工智能技术，生成独特而吸引人的小说内容。\n\n"
            info_text += "特点:\n"
            info_text += "• 多种小说类型选择\n"
            info_text += "• 自定义生成参数\n"
            info_text += "• 批量生成功能\n"
            info_text += "• 续写已有小说"
            
            ttk.Label(frame, text=info_text, wraplength=350, justify=tk.LEFT).pack(pady=10)
        else:
            # 英文版本
            ttk.Label(frame, text=f"AI Novel Generator v{__version__}", font=("Arial", 16, "bold")).pack(pady=10)
            ttk.Label(frame, text=f"Author: {__author__}", font=("Arial", 10)).pack()
            ttk.Label(frame, text="Copyright © 2024", font=("Arial", 10)).pack(pady=5)
            
            ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
            
            info_text = "This is an AI-powered novel generator that can create various types of novels.\n"
            info_text += "Using advanced artificial intelligence technology to generate unique and engaging novel content.\n\n"
            info_text += "Features:\n"
            info_text += "• Multiple novel genre options\n"
            info_text += "• Customizable generation parameters\n"
            info_text += "• Batch generation capability\n"
            info_text += "• Continue writing from existing novels"
            
            ttk.Label(frame, text=info_text, wraplength=350, justify=tk.LEFT).pack(pady=10)
        
        # 添加链接部分
        links_frame = ttk.Frame(frame)
        links_frame.pack(fill=tk.X, pady=(5, 10))
        
        # API充值地址链接
        api_link_label = ttk.Label(links_frame, text="API充值地址: ")
        api_link_label.pack(side=tk.LEFT, padx=(0, 2))
        
        api_link = tk.Label(links_frame, text="api.gwihviete.xyz", fg="blue", cursor="hand2")
        api_link.pack(side=tk.LEFT)
        api_link.bind("<Button-1>", lambda e: self.open_link("https://api.gwihviete.xyz"))
        api_link.bind("<Enter>", lambda e: api_link.config(font=("Arial", 9, "underline")))
        api_link.bind("<Leave>", lambda e: api_link.config(font=("Arial", 9)))
        
        # 空间分隔符
        ttk.Label(links_frame, text="  |  ").pack(side=tk.LEFT)
        
        # 教程地址链接
        tutorial_link_label = ttk.Label(links_frame, text="教程地址: ")
        tutorial_link_label.pack(side=tk.LEFT, padx=(5, 2))
        
        tutorial_link = tk.Label(links_frame, text="@飞书文档", fg="blue", cursor="hand2")
        tutorial_link.pack(side=tk.LEFT)
        tutorial_link.bind("<Button-1>", lambda e: self.open_link("https://ccnql5c7kjke.feishu.cn/wiki/FXp9wHkozi8a3YkH3lRcw5EBn3f"))
        tutorial_link.bind("<Enter>", lambda e: tutorial_link.config(font=("Arial", 9, "underline")))
        tutorial_link.bind("<Leave>", lambda e: tutorial_link.config(font=("Arial", 9)))
        
        # 确定按钮
        ttk.Button(frame, text="确定" if self.language == "中文" else "OK", 
                  command=lambda: self.destroy_safely()).pack(pady=10)

    def destroy_safely(self):
        """安全地销毁窗口"""
        try:
            self.destroy()
        except:
            # 如果标准destroy失败，尝试强制关闭
            if self.winfo_exists():
                self.quit()
                self.withdraw()

    def open_link(self, url):
        import webbrowser
        webbrowser.open(url)

class WelcomeDialog(tk.Toplevel):
    """欢迎对话框"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("欢迎使用")
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.api_key = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建对话框控件"""
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="欢迎使用", font=("Arial", 16, "bold")).pack(pady=10)
        
        ttk.Label(frame, text="请输入您的API密钥继续使用:", font=("Arial", 11)).pack(pady=20)
        
        api_frame = ttk.Frame(frame)
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="API密钥:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*").pack(side=tk.LEFT, padx=5)
        
        info_text = "注意: API密钥将保存在本地配置文件中，\n仅用于与AI服务进行通信。\n\n"
        
        ttk.Label(frame, text=info_text, wraplength=450, justify=tk.LEFT).pack(pady=(10, 0))
        
        # 添加获取API密钥的链接
        link_frame = ttk.Frame(frame)
        link_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(link_frame, text="如果您还没有API密钥，请点击这里获取: ").pack(side=tk.LEFT)
        
        # 创建链接标签
        link_label = tk.Label(link_frame, text="api.gwihviete.xyz", fg="blue", cursor="hand2")
        link_label.pack(side=tk.LEFT)
        
        # 创建鼠标悬停效果
        def on_enter(e):
            link_label.config(font=("Arial", 9, "underline"))
            
        def on_leave(e):
            link_label.config(font=("Arial", 9))
            
        def on_click(e):
            import webbrowser
            webbrowser.open("https://api.gwihviete.xyz")
        
        link_label.bind("<Enter>", on_enter)
        link_label.bind("<Leave>", on_leave)
        link_label.bind("<Button-1>", on_click)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.destroy_safely).pack(side=tk.LEFT, padx=10)
    
    def on_ok(self):
        """确定按钮点击处理"""
        if not self.api_key.get().strip():
            messagebox.showerror("错误", "请输入API密钥")
            return
            
        # 保存API密钥
        save_config(self.api_key.get().strip(), "gemini-2.0-flash", "中文", 3, 100000)
        
        # 确保窗口被销毁
        self.destroy_safely()

    def destroy_safely(self):
        """安全地销毁窗口"""
        try:
            self.destroy()
        except:
            # 如果标准destroy失败，尝试强制关闭
            if self.winfo_exists():
                self.quit()
                self.withdraw()

class MultiTypeDialog(tk.Toplevel):
    """多类型选择对话框"""
    def __init__(self, parent, language="中文"):
        super().__init__(parent)
        self.parent = parent
        
        if language == "中文":
            self.title("选择小说类型")
        else:
            self.title("Select Novel Types")
            
        self.geometry("800x600")  # 增加窗口宽度
        self.resizable(True, True)  # 允许调整大小
        self.transient(parent)
        self.grab_set()
        
        self.language = language
        self.selected_types = []
        
        # 从NOVEL_TYPES获取当前语言的所有类型
        from novel_generator.templates.prompts import NOVEL_TYPES
        
        novel_types_list = []
        if language in NOVEL_TYPES:
            novel_types_list = NOVEL_TYPES[language]
        else:
            # 如果找不到指定语言的类型列表，使用GENRE_SPECIFIC_PROMPTS作为备选
            novel_types_list = list(GENRE_SPECIFIC_PROMPTS.keys())
            
        # 为每个类型创建变量
        self.type_vars = {}
        for novel_type in novel_types_list:
            self.type_vars[novel_type] = tk.BooleanVar(value=False)
            self.type_vars[novel_type].trace_add("write", self.update_selection_count)
            
        self.selection_count = tk.StringVar(value="已选择: 0")
        
        # 添加搜索变量
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_types)
        
        # 存储所有类型和过滤后的类型
        self.all_types = sorted(self.type_vars.keys())
        self.filtered_types = self.all_types.copy()
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建对话框控件"""
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        header_text = "请选择要批量生成的小说类型" if self.language == "中文" else "Select novel types for batch generation"
        ttk.Label(frame, text=header_text, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # 添加搜索框
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        search_label_text = "搜索类型:" if self.language == "中文" else "Search types:"
        ttk.Label(search_frame, text=search_label_text).pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 清除搜索按钮
        clear_text = "清除" if self.language == "中文" else "Clear"
        ttk.Button(search_frame, text=clear_text, command=self.clear_search, width=8).pack(side=tk.LEFT)
        
        # 选择数量
        select_count_frame = ttk.Frame(frame)
        select_count_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(select_count_frame, textvariable=self.selection_count).pack(side=tk.LEFT)
        
        # 全选/取消按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=1, sticky=tk.E)
        
        select_all_text = "全选" if self.language == "中文" else "Select All"
        deselect_all_text = "取消全选" if self.language == "中文" else "Deselect All"
        
        ttk.Button(button_frame, text=select_all_text, command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=deselect_all_text, command=self.deselect_all).pack(side=tk.LEFT)
        
        # 创建滚动框架
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
        scrollbar.grid(row=3, column=2, sticky="ns", pady=10)
        
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # 显示类型复选框
        self.display_types()
        
        # 确定取消按钮
        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ok_text = "确定" if self.language == "中文" else "OK"
        cancel_text = "取消" if self.language == "中文" else "Cancel"
        
        ttk.Button(bottom_frame, text=ok_text, command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text=cancel_text, command=self.destroy_safely).pack(side=tk.LEFT, padx=10)
        
    def display_types(self):
        """显示类型复选框"""
        # 清除现有的复选框
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        columns_per_row = 3  # 每行显示的类型数
        
        for i, novel_type in enumerate(self.filtered_types):
            row = i // columns_per_row
            col = i % columns_per_row
            
            # 创建一个框架来容纳每个复选框，确保它们有足够的空间
            type_frame = ttk.Frame(self.scrollable_frame)
            type_frame.grid(row=row, column=col, sticky=tk.W, pady=5, padx=10)
            
            # 在框架中添加复选框
            ttk.Checkbutton(
                type_frame, 
                text=novel_type, 
                variable=self.type_vars[novel_type],
                width=20  # 设置固定宽度
            ).pack(side=tk.LEFT, anchor=tk.W)
    
    def filter_types(self, *args):
        """根据搜索词过滤类型"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_types = self.all_types.copy()
        else:
            self.filtered_types = [t for t in self.all_types if search_term in t.lower()]
        
        self.display_types()
    
    def clear_search(self):
        """清除搜索"""
        self.search_var.set("")
        
    def update_selection_count(self, *args):
        """更新已选择计数"""
        count = sum(var.get() for var in self.type_vars.values())
        self.selection_count.set(f"已选择: {count}" if self.language == "中文" else f"Selected: {count}")
    
    def select_all(self):
        """全选"""
        # 只全选当前过滤显示的类型
        for novel_type in self.filtered_types:
            self.type_vars[novel_type].set(True)
            
    def deselect_all(self):
        """取消全选"""
        # 只取消全选当前过滤显示的类型
        for novel_type in self.filtered_types:
            self.type_vars[novel_type].set(False)
            
    def on_ok(self):
        """确定按钮点击处理"""
        self.selected_types = [
            novel_type for novel_type, var in self.type_vars.items() if var.get()
        ]
        
        if not self.selected_types:
            error_msg = "请至少选择一种小说类型" if self.language == "中文" else "Please select at least one novel type"
            messagebox.showerror("错误" if self.language == "中文" else "Error", error_msg)
            return
            
        # 确保窗口被销毁
        self.destroy_safely()
    
    def show(self):
        """显示对话框并等待结果"""
        self.wait_window()
        return self.selected_types 

    def destroy_safely(self):
        """安全地销毁窗口"""
        try:
            self.destroy()
        except:
            # 如果标准destroy失败，尝试强制关闭
            if self.winfo_exists():
                self.quit()
                self.withdraw()


class MediaTasksDialog(tk.Toplevel):
    """媒体任务管理对话框"""
    
    def __init__(self, parent, media_generator=None):
        super().__init__(parent)
        self.parent = parent
        self.media_generator = media_generator
        
        self.title("媒体任务管理")
        self.geometry("900x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # 设置最小窗口大小
        self.minsize(800, 500)
        
        self.create_widgets()
        self.refresh_tasks()
        
        # 居中显示
        self.center_window()
    
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制栏
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(control_frame, text="刷新任务", command=self.refresh_tasks)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 批量查询按钮
        self.batch_query_btn = ttk.Button(control_frame, text="批量查询待处理任务", command=self.batch_query_tasks)
        self.batch_query_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清理旧任务按钮
        self.clean_btn = ttk.Button(control_frame, text="清理7天前任务", command=self.clean_old_tasks)
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态筛选
        ttk.Label(control_frame, text="状态筛选:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter = ttk.Combobox(control_frame, values=["全部", "待处理", "已完成", "失败"], state="readonly", width=10)
        self.status_filter.set("全部")
        self.status_filter.pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter.bind("<<ComboboxSelected>>", self.filter_tasks)
        
        # 任务统计
        self.stats_label = ttk.Label(control_frame, text="")
        self.stats_label.pack(side=tk.RIGHT)
        
        # 任务列表框架
        list_frame = ttk.LabelFrame(main_frame, text="任务列表")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ("local_id", "type", "status", "created_at", "prompt")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.task_tree.heading("local_id", text="任务ID")
        self.task_tree.heading("type", text="类型")
        self.task_tree.heading("status", text="状态")
        self.task_tree.heading("created_at", text="创建时间")
        self.task_tree.heading("prompt", text="提示词")
        
        self.task_tree.column("local_id", width=150)
        self.task_tree.column("type", width=80)
        self.task_tree.column("status", width=100)
        self.task_tree.column("created_at", width=150)
        self.task_tree.column("prompt", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.task_tree.bind("<Double-1>", self.on_task_double_click)
        
        # 详情框架
        detail_frame = ttk.LabelFrame(main_frame, text="任务详情")
        detail_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 详情文本
        self.detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # 底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 查询单个任务按钮
        self.query_btn = ttk.Button(button_frame, text="查询选中任务", command=self.query_selected_task, state=tk.DISABLED)
        self.query_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 手动输入任务ID查询
        ttk.Label(button_frame, text="任务ID:").pack(side=tk.LEFT, padx=(20, 5))
        self.task_id_entry = ttk.Entry(button_frame, width=20)
        self.task_id_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.manual_query_btn = ttk.Button(button_frame, text="查询", command=self.manual_query_task)
        self.manual_query_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 关闭按钮
        self.close_btn = ttk.Button(button_frame, text="关闭", command=self.destroy_safely)
        self.close_btn.pack(side=tk.RIGHT)
        
        # 绑定选择事件
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
    
    def refresh_tasks(self):
        """刷新任务列表"""
        if not self.media_generator:
            messagebox.showwarning("警告", "媒体生成器未初始化")
            return
        
        try:
            # 清空现有项目
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            
            # 获取所有任务
            all_tasks = self.media_generator.get_all_tasks()
            
            # 添加到树视图
            for task in all_tasks:
                # 格式化时间
                created_time = task.get("created_at", "").split("T")[0] if "T" in task.get("created_at", "") else task.get("created_at", "")
                
                # 截断提示词
                prompt = task.get("prompt", "")
                if len(prompt) > 50:
                    prompt = prompt[:50] + "..."
                
                self.task_tree.insert("", tk.END, values=(
                    task.get("local_id", ""),
                    "图片" if task.get("type") == "image" else "音乐",
                    self.translate_status(task.get("status", "")),
                    created_time,
                    prompt
                ))
            
            # 更新统计
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新任务列表失败: {str(e)}")
    
    def translate_status(self, status):
        """翻译状态"""
        status_map = {
            "submitted": "已提交",
            "queued": "排队中",
            "running": "运行中",
            "in_progress": "进行中",
            "success": "成功",
            "complete": "完成",
            "failure": "失败",
            "error": "错误",
            "timeout": "超时"
        }
        return status_map.get(status, status)
    
    def update_stats(self):
        """更新统计信息"""
        if not self.media_generator:
            return
        
        try:
            summary = self.media_generator.get_task_summary()
            stats_text = f"总计: {summary['total']} | 待处理: {summary['pending']} | 已完成: {summary['completed']} | 失败: {summary['failed']}"
            self.stats_label.config(text=stats_text)
        except Exception as e:
            self.stats_label.config(text="统计信息获取失败")
    
    def filter_tasks(self, event=None):
        """根据状态筛选任务"""
        filter_value = self.status_filter.get()
        
        # 清空现有项目
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        if not self.media_generator:
            return
        
        try:
            # 根据筛选条件获取任务
            if filter_value == "待处理":
                tasks = self.media_generator.get_pending_tasks()
            elif filter_value == "已完成":
                tasks = self.media_generator.get_completed_tasks()
            elif filter_value == "失败":
                tasks = self.media_generator.task_manager.get_failed_tasks()
            else:  # 全部
                tasks = self.media_generator.get_all_tasks()
            
            # 添加到树视图
            for task in tasks:
                created_time = task.get("created_at", "").split("T")[0] if "T" in task.get("created_at", "") else task.get("created_at", "")
                prompt = task.get("prompt", "")
                if len(prompt) > 50:
                    prompt = prompt[:50] + "..."
                
                self.task_tree.insert("", tk.END, values=(
                    task.get("local_id", ""),
                    "图片" if task.get("type") == "image" else "音乐",
                    self.translate_status(task.get("status", "")),
                    created_time,
                    prompt
                ))
        
        except Exception as e:
            messagebox.showerror("错误", f"筛选任务失败: {str(e)}")
    
    def on_task_select(self, event):
        """任务选择事件"""
        selection = self.task_tree.selection()
        if selection:
            self.query_btn.config(state=tk.NORMAL)
            # 显示任务详情
            item = self.task_tree.item(selection[0])
            local_id = item['values'][0]
            self.show_task_detail(local_id)
        else:
            self.query_btn.config(state=tk.DISABLED)
            self.detail_text.delete(1.0, tk.END)
    
    def show_task_detail(self, local_id):
        """显示任务详情"""
        if not self.media_generator:
            return
        
        try:
            task = self.media_generator.task_manager.get_task(local_id)
            if task:
                detail_text = f"""任务ID: {task.get('local_id', '')}
API任务ID: {task.get('api_task_id', '')}
类型: {'图片' if task.get('type') == 'image' else '音乐'}
状态: {self.translate_status(task.get('status', ''))}
创建时间: {task.get('created_at', '')}
更新时间: {task.get('updated_at', '')}
输出目录: {task.get('output_dir', '')}

提示词:
{task.get('prompt', '')}

小说信息:
类型: {task.get('novel_info', {}).get('genre', '')}
主角: {task.get('novel_info', {}).get('protagonist', {}).get('name', '')}
背景: {task.get('novel_info', {}).get('background', '')}
"""
                
                if task.get('result'):
                    detail_text += f"\n结果信息:\n{task.get('result')}"
                
                if task.get('error'):
                    detail_text += f"\n错误信息:\n{task.get('error')}"
                
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(1.0, detail_text)
        
        except Exception as e:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, f"获取任务详情失败: {str(e)}")
    
    def on_task_double_click(self, event):
        """双击任务事件"""
        self.query_selected_task()
    
    def query_selected_task(self):
        """查询选中的任务"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
        
        item = self.task_tree.item(selection[0])
        local_id = item['values'][0]
        self.query_task(local_id)
    
    def manual_query_task(self):
        """手动查询任务"""
        task_id = self.task_id_entry.get().strip()
        if not task_id:
            messagebox.showwarning("警告", "请输入任务ID")
            return
        
        self.query_task(task_id)
    
    def query_task(self, local_id):
        """查询任务状态"""
        if not self.media_generator:
            messagebox.showwarning("警告", "媒体生成器未初始化")
            return
        
        try:
            # 在新线程中查询以避免界面卡顿
            import threading
            
            def query_thread():
                try:
                    result = self.media_generator.query_task_by_id(local_id)
                    # 在主线程中更新界面
                    self.after(0, lambda: self.on_query_complete(local_id, result))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("错误", f"查询任务失败: {str(e)}"))
            
            thread = threading.Thread(target=query_thread, daemon=True)
            thread.start()
            
            messagebox.showinfo("提示", f"正在查询任务 {local_id}，请稍候...")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动查询失败: {str(e)}")
    
    def on_query_complete(self, local_id, result):
        """查询完成回调"""
        if result:
            messagebox.showinfo("查询完成", f"任务 {local_id} 查询完成，状态已更新")
        else:
            messagebox.showwarning("查询完成", f"任务 {local_id} 查询完成，但未获取到结果")
        
        # 刷新显示
        self.refresh_tasks()
        self.show_task_detail(local_id)
    
    def batch_query_tasks(self):
        """批量查询待处理任务"""
        if not self.media_generator:
            messagebox.showwarning("警告", "媒体生成器未初始化")
            return
        
        pending_tasks = self.media_generator.get_pending_tasks()
        if not pending_tasks:
            messagebox.showinfo("提示", "没有待处理的任务")
            return
        
        if not messagebox.askyesno("确认", f"将查询 {len(pending_tasks)} 个待处理任务，这可能需要一些时间，是否继续？"):
            return
        
        try:
            import threading
            
            def batch_query_thread():
                try:
                    updated_tasks = self.media_generator.batch_query_pending_tasks()
                    self.after(0, lambda: self.on_batch_query_complete(len(updated_tasks)))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("错误", f"批量查询失败: {str(e)}"))
            
            thread = threading.Thread(target=batch_query_thread, daemon=True)
            thread.start()
            
            messagebox.showinfo("提示", "批量查询已开始，请稍候...")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动批量查询失败: {str(e)}")
    
    def on_batch_query_complete(self, updated_count):
        """批量查询完成回调"""
        messagebox.showinfo("批量查询完成", f"批量查询完成，更新了 {updated_count} 个任务")
        self.refresh_tasks()
    
    def clean_old_tasks(self):
        """清理旧任务"""
        if not self.media_generator:
            messagebox.showwarning("警告", "媒体生成器未初始化")
            return
        
        if not messagebox.askyesno("确认", "将删除7天前的所有任务记录，此操作不可恢复，是否继续？"):
            return
        
        try:
            self.media_generator.task_manager.clean_old_tasks(7)
            messagebox.showinfo("完成", "旧任务清理完成")
            self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("错误", f"清理旧任务失败: {str(e)}")
    
    def show(self):
        """显示对话框"""
        self.center_window()
        self.wait_window()
    
    def destroy_safely(self):
        """安全地销毁对话框"""
        try:
            if self.winfo_exists():
                self.destroy()
        except tk.TclError:
            pass 
