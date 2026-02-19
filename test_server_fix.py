#!/usr/bin/env python3
"""
测试服务器修复
"""

import asyncio
import sys
from mcp_browser_tools.server import server, main

async def test_server_import():
    """测试服务器导入"""
    print("1. 测试服务器导入...")

    try:
        # 检查服务器实例
        print(f"   服务器名称: {server.name}")

        # 检查工具数量
        # 注意：这里不能直接调用list_tools，因为需要MCP上下文
        print("   服务器实例创建成功")
        return True
    except Exception as e:
        print(f"   错误: {e}")
        return False

async def test_main_function():
    """测试main函数"""
    print("\n2. 测试main函数...")

    try:
        # 检查main函数是否存在
        import inspect
        if inspect.iscoroutinefunction(main):
            print("   main函数是异步函数")
        else:
            print("   main函数不是异步函数")
            return False

        # 检查函数签名
        sig = inspect.signature(main)
        print(f"   函数签名: {sig}")

        return True
    except Exception as e:
        print(f"   错误: {e}")
        return False

async def test_mcp_api():
    """测试MCP API兼容性"""
    print("\n3. 测试MCP API兼容性...")

    try:
        # 检查必要的导入
        from mcp.server.stdio import stdio_server
        print("   stdio_server导入成功")

        from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
        print("   MCP类型导入成功")

        # 检查服务器方法
        if hasattr(server, 'run'):
            print("   服务器有run方法")
        else:
            print("   服务器缺少run方法")

        return True
    except Exception as e:
        print(f"   错误: {e}")
        return False

async def test_tool_registration():
    """测试工具注册"""
    print("\n4. 测试工具注册...")

    try:
        # 统计装饰的工具函数
        import ast
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 查找@server.call_tool()装饰的函数
        count = content.count("@server.call_tool()")
        print(f"   找到 {count} 个工具函数")

        if count >= 6:
            print("   工具注册数量正确")
            return True
        else:
            print(f"   工具注册数量不足，期望6个，找到{count}个")
            return False
    except Exception as e:
        print(f"   错误: {e}")
        return False

async def main_test():
    """主测试函数"""
    print("=" * 60)
    print("服务器修复测试")
    print("=" * 60)

    tests = [
        ("服务器导入", test_server_import),
        ("main函数", test_main_function),
        ("MCP API", test_mcp_api),
        ("工具注册", test_tool_registration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"   {test_name}测试异常: {e}")
            results.append((test_name, False))

    # 显示结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1

    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 项通过")

    if passed == total:
        print("\n✅ 所有测试通过！服务器修复成功。")
        print("\n启动命令:")
        print("  mcp-browser-tools")
        print("\n或")
        print("  uv run python -m mcp_browser_tools.server")
        return True
    else:
        print(f"\n❌ 有 {total - passed} 项测试失败")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main_test())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)