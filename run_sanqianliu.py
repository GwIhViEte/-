#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三千流小说生成器启动脚本

用法：
1. 设置API_KEY环境变量或在下方直接填写
2. 运行脚本：python run_sanqianliu.py
3. 根据提示选择功能

此脚本提供了三千流小说生成器的简单命令行界面，允许用户执行各种功能。
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any

from core.sanqianliu_interface import SanQianLiuInterface, get_interface

def get_api_key() -> str:
    """获取API密钥"""
    # 优先从环境变量获取
    api_key = os.environ.get("API_KEY")
    
    # 如果环境变量中没有，则提示用户输入
    if not api_key:
        api_key = input("请输入API密钥: ")
        
    return api_key

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(description="三千流小说生成器")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 初始化命令
    init_parser = subparsers.add_parser("init", help="初始化生成器")
    init_parser.add_argument("--target_length", type=int, default=5000000, help="目标字数")
    init_parser.add_argument("--explosion_interval", type=int, default=5, help="爆点间隔章节数")
    
    # 生成大纲命令
    outline_parser = subparsers.add_parser("outline", help="生成小说大纲")
    
    # 生成角色系统命令
    character_parser = subparsers.add_parser("characters", help="生成角色系统")
    
    # 生成修炼境界图表命令
    chart_parser = subparsers.add_parser("chart", help="生成修炼境界图表")
    
    # 生成小说概要命令
    summary_parser = subparsers.add_parser("summary", help="生成小说概要")
    
    # 生成单章命令
    chapter_parser = subparsers.add_parser("chapter", help="生成单个章节")
    chapter_parser.add_argument("chapter_number", type=int, help="章节号")
    
    # 批量生成命令
    batch_parser = subparsers.add_parser("batch", help="批量生成章节")
    batch_parser.add_argument("--start", type=int, default=1, help="起始章节号")
    batch_parser.add_argument("--count", type=int, default=10, help="生成章节数量")
    
    # 交互模式命令
    interactive_parser = subparsers.add_parser("interactive", help="进入交互模式")
    
    return parser

def run_interactive_mode(interface: SanQianLiuInterface) -> None:
    """运行交互模式"""
    while True:
        print("\n==== 小说生成器 ====")
        print("API充值地址: api.gwihviete.xyz")
        
        print("1. 初始化生成器")
        print("2. 生成小说大纲")
        print("3. 生成角色系统")
        print("4. 生成修炼境界图表")
        print("5. 生成小说概要")
        print("6. 生成单个章节")
        print("7. 批量生成章节")
        print("0. 退出")
        
        choice = input("\n请选择功能 (0-7): ")
        
        if choice == "0":
            print("再见！")
            break
        elif choice == "1":
            try:
                target_length = int(input("请输入目标字数 (默认5000000): ") or "5000000")
                explosion_interval = int(input("请输入爆点间隔章节数 (默认5): ") or "5")
                interface.initialize_generator(target_length, explosion_interval)
            except ValueError as e:
                print(f"输入错误: {e}")
        elif choice == "2":
            interface.generate_novel_outline()
        elif choice == "3":
            interface.generate_character_system()
        elif choice == "4":
            interface.generate_cultivation_chart()
        elif choice == "5":
            interface.export_story_summary()
        elif choice == "6":
            try:
                chapter_number = int(input("请输入章节号: "))
                interface.generate_chapter(chapter_number)
            except ValueError as e:
                print(f"输入错误: {e}")
        elif choice == "7":
            try:
                start_chapter = int(input("请输入起始章节号 (默认1): ") or "1")
                num_chapters = int(input("请输入生成章节数量 (默认10): ") or "10")
                interface.generate_novel_batch(start_chapter, num_chapters)
            except ValueError as e:
                print(f"输入错误: {e}")
        else:
            print("无效选择，请重试")

def main() -> None:
    """主函数"""
    # 获取API密钥
    api_key = get_api_key()
    if not api_key:
        print("未提供API密钥，退出程序")
        sys.exit(1)
        
    # 创建接口实例
    interface = get_interface(api_key)
    
    # 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 处理命令
    if args.command == "init":
        interface.initialize_generator(args.target_length, args.explosion_interval)
    elif args.command == "outline":
        interface.generate_novel_outline()
    elif args.command == "characters":
        interface.generate_character_system()
    elif args.command == "chart":
        interface.generate_cultivation_chart()
    elif args.command == "summary":
        interface.export_story_summary()
    elif args.command == "chapter":
        interface.generate_chapter(args.chapter_number)
    elif args.command == "batch":
        interface.generate_novel_batch(args.start, args.count)
    elif args.command == "interactive" or not args.command:
        run_interactive_mode(interface)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 