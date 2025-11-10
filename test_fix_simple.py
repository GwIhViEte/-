#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import json

# 添加路径以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_config_fix():
    """测试配置修复"""
    print("=== 老王的高级设置配置修复测试 ===")
    
    try:
        # 尝试导入模块 - 优先尝试直接导入
        try:
            from utils.config import save_config, load_config
            print("OK - 成功导入配置模块(直接导入)")
        except ImportError:
            from novel_generator.utils.config import save_config, load_config
            print("OK - 成功导入配置模块(模块导入)")
        
        # 测试配置
        test_config = {
            "advanced_settings": {
                "paragraph_length_preference": "较长段落",
                "dialogue_frequency": "对话较多",
                "temperature": 0.8
            }
        }
        
        print("\n1. 测试配置保存...")
        save_config(test_config)
        print("OK - 配置保存成功")
        
        print("2. 测试配置加载...")
        loaded = load_config()
        adv = loaded.get("advanced_settings", {})
        
        para = adv.get("paragraph_length_preference", "未找到")
        dial = adv.get("dialogue_frequency", "未找到")
        
        print(f"   段落长度倾向: {para}")
        print(f"   对话频率: {dial}")
        
        if para == "较长段落" and dial == "对话较多":
            print("OK - 配置持久化测试通过!")
            return True
        else:
            print("FAIL - 配置值不匹配")
            return False
            
    except Exception as e:
        print(f"FAIL - 测试失败: {e}")
        return False

def test_dialog_params():
    """测试对话框参数"""
    print("\n=== 测试对话框参数传递 ===")
    
    try:
        # 尝试导入对话框模块
        try:
            from ui.dialogs import AdvancedSettingsDialog
            print("OK - 成功导入对话框模块(直接导入)")
        except ImportError:
            from novel_generator.ui.dialogs import AdvancedSettingsDialog
            print("OK - 成功导入对话框模块(模块导入)")
            
        import tkinter as tk
        
        print("1. 创建测试对话框...")
        root = tk.Tk()
        root.withdraw()
        
        # 测试参数传递
        dialog = AdvancedSettingsDialog(
            root,
            paragraph_length_preference="短小精悍",
            dialogue_frequency="对话较少"
        )
        
        # 检查参数
        para_val = dialog.paragraph_length_preference.get()
        dial_val = dialog.dialogue_frequency.get()
        
        print(f"   段落长度倾向: {para_val}")
        print(f"   对话频率: {dial_val}")
        
        # 清理
        dialog.destroy()
        root.destroy()
        
        if para_val == "短小精悍" and dial_val == "对话较少":
            print("OK - 对话框参数传递测试通过!")
            return True
        else:
            print("FAIL - 参数值不匹配")
            return False
            
    except Exception as e:
        print(f"FAIL - 对话框测试失败: {e}")
        return False

def main():
    """主测试"""
    print("老王专治SB配置问题 - 高级设置修复测试")
    print("=" * 60)
    
    results = []
    results.append(test_config_fix())
    results.append(test_dialog_params())
    
    print("\n" + "=" * 60)
    print("测试结果:")
    
    tests = ["配置持久化", "对话框参数传递"]
    passed = 0
    
    for i, result in enumerate(results):
        status = "通过" if result else "失败"
        print(f"  {tests[i]}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 修复成功!")
        print("现在段落长度倾向和对话频率设置可以正常保存了!")
        print("\n修复要点:")
        print("1. AdvancedSettingsDialog增加了新参数支持")
        print("2. UI初始化使用传入参数而不是硬编码默认值")
        print("3. 主应用调用时传入当前配置值")
        print("4. 配置加载提供向后兼容性")
    else:
        print("\n还有问题需要进一步检查...")
    
    return passed == len(results)

if __name__ == "__main__":
    main()