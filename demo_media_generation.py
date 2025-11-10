#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI小说生成器 - 媒体生成功能演示脚本
展示如何使用新的封面和音乐生成功能
"""

import os
import sys
import json
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.generator import NovelGenerator
from core.media_generator import MediaGenerator

def demo_media_generation():
    """演示媒体生成功能"""
    
    print("🎨 AI小说生成器 - 媒体生成功能演示")
    print("=" * 50)
    
    # 演示配置
    demo_config = {
        "api_key": "your_api_key_here",  # 请替换为实际的API密钥
        "model": "gemini-2.0-flash",
        "language": "中文",
        "novel_type": "奇幻冒险",
        "target_length": 1000,  # 演示用较短长度
        "num_novels": 1,
        "generate_cover": True,
        "generate_music": True,
        "num_cover_images": 2
    }
    
    print("📋 当前配置:")
    for key, value in demo_config.items():
        if key == "api_key":
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 检查API密钥
    if demo_config["api_key"] == "your_api_key_here":
        print("⚠️  请先设置有效的API密钥")
        print("   在 demo_config['api_key'] 中填入您的API密钥")
        print("\n🔗 获取API密钥: https://api.gwihviete.xyz")
        return
    
    # 创建输出目录
    output_dir = f"demo_output_{int(time.time())}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    # 状态回调函数
    def status_callback(message):
        print(f"📢 {message}")
    
    # 进度回调函数
    def progress_callback(progress_data):
        if "percent" in progress_data:
            print(f"📊 进度: {progress_data['percent']:.1f}%")
    
    try:
        print("\n🚀 开始生成小说...")
        
        # 创建小说生成器（包含媒体生成功能）
        generator = NovelGenerator(
            api_key=demo_config["api_key"],
            model=demo_config["model"],
            language=demo_config["language"],
            novel_type=demo_config["novel_type"],
            target_length=demo_config["target_length"],
            num_novels=demo_config["num_novels"],
            status_callback=status_callback,
            progress_callback=progress_callback,
            generate_cover=demo_config["generate_cover"],
            generate_music=demo_config["generate_music"],
            num_cover_images=demo_config["num_cover_images"]
        )
        
        # 设置输出目录
        generator.output_dir = output_dir
        
        print("\n📝 生成小说文本...")
        # 这里可以调用生成器的方法来生成小说
        # 由于这是演示，我们创建一个模拟的小说设置
        
        # 模拟小说设置
        novel_setup = {
            "genre": demo_config["novel_type"],
            "title": "魔法世界的冒险",
            "protagonist": {
                "name": "林逸",
                "gender": "男",
                "age": "青年",
                "background": "来自普通世界的少年，意外获得魔法力量"
            },
            "world_building": {
                "setting": "一个充满魔法和神秘生物的奇幻世界",
                "time_period": "中世纪奇幻时代",
                "location": "艾泽拉斯大陆"
            },
            "themes": ["友情", "成长", "冒险", "正义", "勇气"],
            "story_structure": {
                "opening": "平凡少年的奇遇",
                "development": "魔法学院的学习与成长",
                "climax": "对抗黑暗势力的最终战斗",
                "resolution": "成为真正的魔法师"
            }
        }
        
        # 模拟小说内容
        novel_content = """
第一章 奇遇

林逸是一个普通的高中生，直到那个雨夜，他发现了一本古老的魔法书...

在那本书的指引下，林逸踏上了前往魔法世界的旅程。艾泽拉斯大陆广袤无垠，充满了神秘和危险。

第二章 魔法学院

进入魔法学院后，林逸遇到了许多志同道合的朋友。他们一起学习魔法，一起面对挑战...

第三章 最终战斗

黑暗势力的威胁日益严重，林逸和他的朋友们必须团结一致，运用所学的魔法知识来保护这个世界...

经过激烈的战斗，正义终于战胜了邪恶，林逸也成长为一名真正的魔法师。
        """.strip()
        
        # 保存小说文本
        novel_filename = f"novel_demo_{demo_config['novel_type']}_林逸.txt"
        novel_filepath = os.path.join(output_dir, novel_filename)
        
        with open(novel_filepath, 'w', encoding='utf-8') as f:
            f.write(novel_content)
        
        print(f"✅ 小说文本已保存: {novel_filename}")
        
        # 保存元数据
        meta_filename = novel_filename.replace('.txt', '_meta.json')
        meta_filepath = os.path.join(output_dir, meta_filename)
        
        with open(meta_filepath, 'w', encoding='utf-8') as f:
            json.dump(novel_setup, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 元数据已保存: {meta_filename}")
        
        # 演示媒体生成功能
        if generator.media_generator:
            print("\n🎨 开始生成媒体内容...")
            
            # 生成封面
            if demo_config["generate_cover"]:
                print(f"\n🖼️  生成 {demo_config['num_cover_images']} 张封面图片...")
                
                # 展示封面提示词
                cover_prompt = generator.media_generator._generate_cover_prompt(novel_setup)
                print(f"📝 封面提示词: {cover_prompt}")
                
                # 这里会调用实际的API（如果有有效密钥）
                # image_ids = generator.media_generator.generate_cover_images(novel_setup, demo_config["num_cover_images"])
                
                # 模拟生成结果
                mock_image_results = []
                for i in range(demo_config["num_cover_images"]):
                    mock_image_results.append({
                        "imageUrl": f"https://example.com/cover_{i+1}.jpg",
                        "id": f"demo_image_{i+1}",
                        "prompt": cover_prompt
                    })
                
                print(f"✅ 封面图片生成完成（模拟）")
            
            # 生成音乐
            if demo_config["generate_music"]:
                print(f"\n🎵 生成主题音乐...")
                
                # 展示音乐提示词
                music_prompt = generator.media_generator._generate_music_prompt(novel_setup)
                print(f"📝 音乐提示词: {music_prompt}")
                
                # 这里会调用实际的API（如果有有效密钥）
                # music_id = generator.media_generator.generate_music(novel_setup)
                
                # 模拟生成结果
                mock_music_result = {
                    "audio_url": "https://example.com/theme_music.mp3",
                    "title": "魔法世界的冒险 - 主题音乐",
                    "id": "demo_music_1",
                    "gpt_description_prompt": music_prompt
                }
                
                print(f"✅ 主题音乐生成完成（模拟）")
            
            # 保存媒体信息
            if demo_config["generate_cover"] or demo_config["generate_music"]:
                print(f"\n💾 保存媒体信息...")
                
                # 使用模拟数据保存媒体信息
                generator.media_generator.save_media_info(
                    output_dir, 
                    novel_setup, 
                    mock_image_results if demo_config["generate_cover"] else [],
                    mock_music_result if demo_config["generate_music"] else None
                )
                
                print(f"✅ 媒体信息已保存到: media_info.json")
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        print(f"\n📁 生成的文件:")
        
        # 列出生成的文件
        for file in os.listdir(output_dir):
            filepath = os.path.join(output_dir, file)
            size = os.path.getsize(filepath)
            print(f"  📄 {file} ({size} bytes)")
        
        print(f"\n🔗 查看结果: {os.path.abspath(output_dir)}")
        
        # 显示媒体信息内容
        media_info_path = os.path.join(output_dir, "media_info.json")
        if os.path.exists(media_info_path):
            print(f"\n📋 媒体信息内容:")
            with open(media_info_path, 'r', encoding='utf-8') as f:
                media_info = json.load(f)
                print(json.dumps(media_info, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

def show_feature_overview():
    """显示功能概览"""
    print("\n📖 媒体生成功能概览:")
    print("=" * 30)
    
    features = [
        ("🖼️  封面生成", "根据小说类型和内容自动生成封面图片"),
        ("🎵 音乐生成", "为小说创作配套的主题音乐"),
        ("🎨 智能提示词", "基于小说元素自动生成高质量提示词"),
        ("📊 多种类型", "支持奇幻、都市、科幻等多种小说类型"),
        ("⚙️  灵活配置", "可自定义封面数量和生成选项"),
        ("💾 完整保存", "自动保存媒体文件信息和下载链接")
    ]
    
    for title, desc in features:
        print(f"{title}: {desc}")
    
    print("\n🔧 支持的API服务:")
    print("  • MidJourney API - 高质量图片生成")
    print("  • Suno API - 专业音乐创作")
    
    print("\n📋 支持的小说类型:")
    types = [
        "奇幻冒险", "都市言情", "玄幻修真", "科幻未来",
        "悬疑推理", "历史穿越", "武侠江湖", "恐怖灵异"
    ]
    for i, novel_type in enumerate(types, 1):
        print(f"  {i}. {novel_type}")

if __name__ == "__main__":
    show_feature_overview()
    print("\n" + "=" * 50)
    demo_media_generation() 