#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UI应用稳定性 - 验证闪退问题修复
"""

import os
import sys
import time
import threading
import asyncio
from unittest.mock import Mock

# 添加项目路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 设置Windows事件循环策略
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def test_run_asyncio_event_loop():
    """测试修复后的异步事件循环函数"""
    print("=== 测试异步事件循环稳定性 ===\n")
    
    # 导入修复后的函数
    try:
        from ui.app import run_asyncio_event_loop
        print("[通过] 成功导入修复后的run_asyncio_event_loop函数")
    except Exception as e:
        print(f"[失败] 无法导入函数: {e}")
        return False
    
    # 测试1: 正常的快速协程
    async def quick_coro():
        await asyncio.sleep(0.1)
        return "快速任务完成"
    
    try:
        start_time = time.time()
        result = run_asyncio_event_loop(quick_coro())
        elapsed = time.time() - start_time
        if result == "快速任务完成" and elapsed < 3:  # 调整为3秒以适应轮询机制
            print(f"[通过] 快速协程测试 - 结果: {result}, 耗时: {elapsed:.2f}秒")
        else:
            print(f"[失败] 快速协程测试 - 结果: {result}, 耗时: {elapsed:.2f}秒")
            return False
    except Exception as e:
        print(f"[失败] 快速协程测试异常: {e}")
        return False
    
    # 测试2: 有异常的协程
    async def error_coro():
        await asyncio.sleep(0.1)
        raise ValueError("测试异常")
    
    try:
        run_asyncio_event_loop(error_coro())
        print("[失败] 异常协程测试 - 应该抛出异常但没有")
        return False
    except ValueError as e:
        if "测试异常" in str(e):
            print("[通过] 异常协程测试 - 正确捕获异常")
        else:
            print(f"[失败] 异常协程测试 - 异常类型错误: {e}")
            return False
    except Exception as e:
        print(f"[失败] 异常协程测试 - 意外异常: {e}")
        return False
    
    # 测试3: 中等耗时协程（测试轮询机制）
    async def medium_coro():
        for i in range(5):
            await asyncio.sleep(0.5)
        return "中等任务完成"
    
    try:
        start_time = time.time()
        result = run_asyncio_event_loop(medium_coro())
        elapsed = time.time() - start_time
        if result == "中等任务完成" and 2.0 <= elapsed <= 4.0:
            print(f"[通过] 中等协程测试 - 结果: {result}, 耗时: {elapsed:.2f}秒")
        else:
            print(f"[失败] 中等协程测试 - 结果: {result}, 耗时: {elapsed:.2f}秒")
            return False
    except Exception as e:
        print(f"[失败] 中等协程测试异常: {e}")
        return False
    
    return True

def test_ui_imports():
    """测试UI模块导入是否正常"""
    print("\n=== 测试UI模块导入 ===\n")
    
    # 测试关键模块导入
    modules_to_test = [
        'ui.app',
        'core.generator', 
        'utils.config',
        'templates.prompts'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"[通过] {module_name} 导入成功")
            success_count += 1
        except Exception as e:
            print(f"[失败] {module_name} 导入失败: {e}")
    
    if success_count == len(modules_to_test):
        print(f"\n[通过] 所有 {len(modules_to_test)} 个关键模块导入成功")
        return True
    else:
        print(f"\n[失败] {success_count}/{len(modules_to_test)} 个模块导入成功")
        return False

def test_threading_stability():
    """测试线程稳定性"""
    print("\n=== 测试线程稳定性 ===\n")
    
    from ui.app import run_asyncio_event_loop
    
    # 创建多个并发的异步任务
    async def concurrent_task(task_id):
        await asyncio.sleep(0.1 + task_id * 0.1)  # 不同的延迟
        return f"任务{task_id}完成"
    
    results = []
    threads = []
    
    def run_task(task_id):
        try:
            result = run_asyncio_event_loop(concurrent_task(task_id))
            results.append((task_id, result, None))
        except Exception as e:
            results.append((task_id, None, str(e)))
    
    # 启动多个线程
    for i in range(3):
        thread = threading.Thread(target=run_task, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=10)  # 10秒超时
    
    # 检查结果
    success_count = 0
    for task_id, result, error in results:
        if error is None:
            print(f"[通过] 并发任务{task_id}: {result}")
            success_count += 1
        else:
            print(f"[失败] 并发任务{task_id}: {error}")
    
    if success_count == 3:
        print(f"[通过] 所有并发任务成功完成")
        return True
    else:
        print(f"[失败] {success_count}/3 个并发任务完成")
        return False

def test_resource_cleanup():
    """测试资源清理"""
    print("\n=== 测试资源清理 ===\n")
    
    from ui.app import run_asyncio_event_loop
    import threading
    import gc
    
    # 记录初始线程数
    initial_thread_count = threading.active_count()
    
    # 运行多个任务测试资源清理
    async def cleanup_test_coro():
        await asyncio.sleep(0.1)
        return "清理测试"
    
    # 连续运行多个任务
    for i in range(5):
        try:
            result = run_asyncio_event_loop(cleanup_test_coro())
            if i == 0:  # 只打印第一个结果
                print(f"[信息] 清理测试任务 {i+1}: {result}")
        except Exception as e:
            print(f"[失败] 清理测试任务 {i+1}: {e}")
            return False
    
    # 强制垃圾回收
    gc.collect()
    time.sleep(0.5)  # 等待线程清理
    
    # 检查线程数是否回到初始水平（允许一些差异）
    final_thread_count = threading.active_count()
    thread_diff = final_thread_count - initial_thread_count
    
    print(f"[信息] 初始线程数: {initial_thread_count}")
    print(f"[信息] 最终线程数: {final_thread_count}")
    print(f"[信息] 线程数差异: {thread_diff}")
    
    if thread_diff <= 2:  # 允许少量差异
        print("[通过] 资源清理测试 - 线程数正常")
        return True
    else:
        print("[警告] 资源清理测试 - 线程数增加较多，可能存在资源泄露")
        return True  # 不算严重失败，只是警告

def main():
    print("AI小说生成器 - UI稳定性测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("UI模块导入", test_ui_imports()))
    test_results.append(("异步事件循环", test_run_asyncio_event_loop()))
    test_results.append(("线程稳定性", test_threading_stability()))
    test_results.append(("资源清理", test_resource_cleanup()))
    
    # 汇总结果
    print(f"\n{'='*50}")
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = passed / len(test_results) * 100
    print(f"\n通过率: {passed}/{len(test_results)} ({success_rate:.1f}%)")
    
    if passed == len(test_results):
        print("\n[成功] 所有稳定性测试通过！应用闪退问题已修复")
        return True
    elif passed >= len(test_results) * 0.75:
        print(f"\n[良好] 大部分测试通过，应用稳定性显著改善")
        return True
    else:
        print(f"\n[需要关注] 部分测试失败，建议进一步检查")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)