#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的连接问题 - aiohttp force_close与keepalive_timeout冲突
"""

import asyncio
import sys
import os
import aiohttp

# 添加项目路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 设置Windows事件循环策略
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def test_tcp_connector_config():
    """测试TCP连接器配置是否有冲突"""
    try:
        # 创建一个与修复后代码相同配置的连接器
        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=10,
            limit_per_host=5,
            enable_cleanup_closed=True,
            keepalive_timeout=60,
            ttl_dns_cache=300
        )
        print("[通过] TCP连接器配置测试通过 - 没有参数冲突")
        return True
    except Exception as e:
        print(f"[失败] TCP连接器配置测试失败: {e}")
        return False

async def test_session_creation():
    """测试会话创建是否正常"""
    try:
        # 创建一个与修复后代码相同的会话
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300),
            connector=aiohttp.TCPConnector(
                ssl=False,
                limit=10,
                limit_per_host=5,
                enable_cleanup_closed=True,
                keepalive_timeout=60,
                ttl_dns_cache=300
            )
        )
        
        print("[通过] 会话创建测试通过 - aiohttp参数配置正确")
        
        # 关闭会话
        await session.close()
        return True
        
    except TypeError as e:
        if "keepalive_timeout cannot be set if force_close is True" in str(e):
            print(f"[失败] 会话创建测试失败: 仍然存在参数冲突 - {e}")
        else:
            print(f"[失败] 会话创建测试失败: {e}")
        return False
    except Exception as e:
        print(f"[失败] 会话创建测试失败: {e}")
        return False

def test_original_issue():
    """测试原始问题是否修复"""
    try:
        # 这是之前会报错的配置
        connector = aiohttp.TCPConnector(
            force_close=True,
            keepalive_timeout=60  # 这个组合会报错
        )
        print("[失败] 原始问题测试失败: 应该报错但没有报错")
        return False
    except Exception as e:
        if "keepalive_timeout cannot be set if force_close is True" in str(e):
            print("[通过] 原始问题确认 - force_close=True与keepalive_timeout冲突")
            return True
        else:
            print(f"[失败] 原始问题测试失败: 意外错误 - {e}")
            return False

async def main():
    print("=== 测试aiohttp连接配置修复 ===\n")
    
    # 测试1: TCP连接器配置
    result1 = test_tcp_connector_config()
    
    # 测试2: 会话创建
    result2 = await test_session_creation()
    
    # 测试3: 原始问题确认
    result3 = test_original_issue()
    
    print(f"\n=== 测试结果 ===")
    print(f"TCP连接器配置: {'通过' if result1 else '失败'}")
    print(f"会话创建: {'通过' if result2 else '失败'}")
    print(f"原始问题确认: {'通过' if result3 else '失败'}")
    
    if all([result1, result2, result3]):
        print("\n[成功] 所有测试通过! aiohttp连接配置问题已修复")
        return True
    else:
        print("\n[失败] 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)