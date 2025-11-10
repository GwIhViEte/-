#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试高级设置配置持久化修复效果

修复了以下问题：
1. AdvancedSettingsDialog初始化时未接收paragraph_length_preference和dialogue_frequency参数
2. 调用对话框时没有传入这两个参数的当前值
3. UI组件初始化时硬编码为默认值，没有使用传入的参数
4. 配置加载时没有向后兼容处理新增参数

作者：老王 - 专治各种SB代码问题
"""

import sys
import os
import json

# 添加路径以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from novel_generator.utils.config import save_config, load_config
    from novel_generator.ui.dialogs import AdvancedSettingsDialog
    print("OK 成功导入新版本模块")
except ImportError:
    try:
        from utils.config import save_config, load_config
        from ui.dialogs import AdvancedSettingsDialog
        print("OK 成功导入旧版本模块")
    except ImportError as e:
        print(f"FAIL 导入失败: {e}")
        sys.exit(1)

def test_config_persistence():
    """测试配置持久化"""
    print("\n=== 测试配置持久化修复效果 ===")
    
    # 测试配置
    test_config = {
        "api_key": "test_key",
        "base_url": "https://test.api.com",
        "model": "test-model",
        "advanced_settings": {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 8000,
            "context_length": 100000,
            "autosave_interval": 60,
            "auto_summary": True,
            "auto_summary_interval": 10000,
            "creativity": 0.7,
            "formality": 0.5,
            "detail_level": 0.6,
            "writing_style": "平衡",
            "paragraph_length_preference": "较长段落",  # 非默认值
            "dialogue_frequency": "对话较多"  # 非默认值
        }
    }
    
    print("1. 保存测试配置...")
    try:
        save_config(test_config)
        print("OK 配置保存成功")
    except Exception as e:
        print(f"FAIL 配置保存失败: {e}")
        return False
    
    print("2. 加载配置并验证...")
    try:
        loaded_config = load_config()
        advanced_settings = loaded_config.get("advanced_settings", {})
        
        # 检查关键参数
        paragraph_pref = advanced_settings.get("paragraph_length_preference")
        dialogue_freq = advanced_settings.get("dialogue_frequency")
        
        print(f"   段落长度倾向: {paragraph_pref}")
        print(f"   对话频率: {dialogue_freq}")
        
        if paragraph_pref == "较长段落" and dialogue_freq == "对话较多":
            print("✓ 配置加载验证成功 - 自定义值正确保存和加载")
            return True
        else:
            print("✗ 配置加载验证失败 - 自定义值丢失")
            return False
            
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_dialog_initialization():
    """测试对话框初始化"""
    print("\n=== 测试对话框初始化修复效果 ===")
    
    try:
        # 测试对话框能否接收新参数
        print("1. 测试对话框参数传递...")
        
        # 创建一个虚拟的parent（这里我们不会实际显示对话框）
        import tkinter as tk
        
        # 创建测试用的主窗口（不显示）
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 测试创建对话框实例（带新参数）
        dialog = AdvancedSettingsDialog(
            root,
            temperature=0.75,
            paragraph_length_preference="短小精悍",
            dialogue_frequency="对话较少"
        )
        
        # 验证参数是否正确设置
        paragraph_value = dialog.paragraph_length_preference.get()
        dialogue_value = dialog.dialogue_frequency.get()
        
        print(f"   段落长度倾向初始值: {paragraph_value}")
        print(f"   对话频率初始值: {dialogue_value}")
        
        # 清理
        dialog.destroy()
        root.destroy()
        
        if paragraph_value == "短小精悍" and dialogue_value == "对话较少":
            print("✓ 对话框初始化验证成功 - 参数正确传递")
            return True
        else:
            print("✗ 对话框初始化验证失败 - 参数传递有问题")
            return False
            
    except Exception as e:
        print(f"✗ 对话框初始化测试失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")
    
    # 创建一个旧版本的配置（没有新参数）
    old_config = {
        "api_key": "test_key",
        "advanced_settings": {
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": 6000,
            # 注意：没有paragraph_length_preference和dialogue_frequency
        }
    }
    
    print("1. 保存旧版本配置...")
    try:
        save_config(old_config)
        print("✓ 旧版本配置保存成功")
    except Exception as e:
        print(f"✗ 旧版本配置保存失败: {e}")
        return False
    
    print("2. 加载配置并检查默认值...")
    try:
        loaded_config = load_config()
        advanced_settings = loaded_config.get("advanced_settings", {})
        
        # 检查是否自动添加了默认值
        paragraph_pref = advanced_settings.get("paragraph_length_preference")
        dialogue_freq = advanced_settings.get("dialogue_frequency")
        
        print(f"   段落长度倾向默认值: {paragraph_pref}")
        print(f"   对话频率默认值: {dialogue_freq}")
        
        # 这个测试需要实际的加载逻辑，这里我们模拟检查
        if paragraph_pref is not None and dialogue_freq is not None:
            print("✓ 向后兼容性验证成功 - 自动添加了默认值")
            return True
        else:
            print("✗ 向后兼容性验证失败 - 缺少默认值")
            return False
            
    except Exception as e:
        print(f"✗ 向后兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("老王的高级设置配置持久化修复测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_config_persistence())
    test_results.append(test_dialog_initialization())
    test_results.append(test_backward_compatibility())
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    test_names = [
        "配置持久化测试",
        "对话框初始化测试", 
        "向后兼容性测试"
    ]
    
    passed = 0
    for i, result in enumerate(test_results):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_names[i]}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(test_results)} 个测试通过")
    
    if passed == len(test_results):
        print("\n🎉 所有测试通过！配置持久化修复成功！")
        print("\n修复说明:")
        print("1. AdvancedSettingsDialog现在正确接收和使用paragraph_length_preference和dialogue_frequency参数")
        print("2. UI组件初始化时使用传入的参数值而不是硬编码默认值")
        print("3. 主应用调用对话框时传入当前配置值")
        print("4. 配置加载时提供向后兼容性，自动为旧配置添加新参数默认值")
        print("\n用户现在可以正常保存和恢复段落长度倾向和对话频率设置了！")
    else:
        print(f"\n❌ 有 {len(test_results) - passed} 个测试失败，需要进一步检查")
    
    return passed == len(test_results)

if __name__ == "__main__":
    main()