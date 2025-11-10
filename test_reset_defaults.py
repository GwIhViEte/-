#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试恢复默认按钮功能

老王专治各种SB按钮问题
"""

import sys
import os
import tkinter as tk

# 添加路径以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_reset_defaults():
    """测试恢复默认按钮功能"""
    print("=== 测试恢复默认按钮功能 ===")
    
    try:
        # 导入对话框模块
        from ui.dialogs import AdvancedSettingsDialog
        
        print("1. 创建测试对话框...")
        root = tk.Tk()
        root.withdraw()
        
        # 创建对话框，传入非默认值
        dialog = AdvancedSettingsDialog(
            root,
            temperature=0.5,  # 非默认值
            paragraph_length_preference="短小精悍",  # 非默认值
            dialogue_frequency="对话较少"  # 非默认值
        )
        
        print("2. 验证初始非默认值...")
        print(f"   温度: {dialog.temperature.get()}")
        print(f"   段落长度倾向: {dialog.paragraph_length_preference.get()}")
        print(f"   对话频率: {dialog.dialogue_frequency.get()}")
        
        # 调用恢复默认方法
        print("3. 执行恢复默认...")
        dialog.reset_defaults()
        
        print("4. 验证恢复后的值...")
        temp_after = dialog.temperature.get()
        para_after = dialog.paragraph_length_preference.get()
        dial_after = dialog.dialogue_frequency.get()
        
        print(f"   温度: {temp_after}")
        print(f"   段落长度倾向: {para_after}")
        print(f"   对话频率: {dial_after}")
        
        # 清理
        dialog.destroy()
        root.destroy()
        
        # 验证结果
        success = True
        if temp_after != 0.8:
            print(f"FAIL - 温度未正确重置，期望0.8，实际{temp_after}")
            success = False
            
        if para_after != "适中":
            print(f"FAIL - 段落长度倾向未正确重置，期望'适中'，实际'{para_after}'")
            success = False
            
        if dial_after != "适中":
            print(f"FAIL - 对话频率未正确重置，期望'适中'，实际'{dial_after}'")
            success = False
            
        if success:
            print("OK - 恢复默认功能测试通过!")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"FAIL - 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("老王专治SB恢复默认按钮测试")
    print("=" * 50)
    
    result = test_reset_defaults()
    
    print("\n" + "=" * 50)
    if result:
        print("测试通过 - 恢复默认按钮修复成功!")
        print("\n现在用户点击'恢复默认'按钮时，")
        print("段落长度倾向和对话频率也会正确重置为'适中'了!")
    else:
        print("测试失败 - 恢复默认按钮仍有问题")
    
    return result

if __name__ == "__main__":
    main()