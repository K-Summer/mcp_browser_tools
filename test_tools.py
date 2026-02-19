#!/usr/bin/env python3
"""
工具可用性测试脚本
"""

import asyncio
import json
import sys
import traceback
from mcp_browser_tools.browser_tools import BrowserTools


async def test_navigation():
    """测试导航功能"""
    print("测试导航功能...")
    try:
        async with BrowserTools() as tools:
            result = await tools.navigate_to_url("https://httpbin.org/get")
            if result["success"]:
                print(f"✅ 导航成功: {result['title']}")
                return True
            else:
                print(f"❌ 导航失败: {result.get('error', '未知错误')}")
                return False
    except Exception as e:
        print(f"❌ 导航测试异常: {e}")
        return False


async def test_content_extraction():
    """测试内容提取功能"""
    print("\n测试内容提取功能...")
    try:
        async with BrowserTools() as tools:
            # 导航到一个测试页面
            await tools.navigate_to_url("https://httpbin.org/html")
            content = await tools.get_page_content()

            if content["success"]:
                print(f"✅ 内容提取成功")
                print(f"   - 标题: {content.get('title', 'N/A')}")
                print(f"   - 内容长度: {content.get('content_length', 0)}")
                print(f"   - 链接数量: {len(content.get('links', []))}")
                return True
            else:
                print(f"❌ 内容提取失败: {content.get('error', '未知错误')}")
                return False
    except Exception as e:
        print(f"❌ 内容提取测试异常: {e}")
        return False


async def test_interactions():
    """测试交互功能"""
    print("\n测试交互功能...")
    try:
        async with BrowserTools() as tools:
            # 导航到一个带表单的页面
            await tools.navigate_to_url("https://httpbin.org/forms/post")

            # 测试等待元素
            wait_result = await tools.wait_for_element("form")
            if not wait_result["success"]:
                print(f"❌ 等待元素失败: {wait_result.get('error', '未知错误')}")
                return False

            # 测试填写表单
            fill_result = await tools.fill_input("input[name='custname']", "测试用户")
            if fill_result["success"]:
                print("✅ 表单填写成功")
            else:
                print(f"❌ 表单填写失败: {fill_result.get('error', '未知错误')}")
                return False

            return True
    except Exception as e:
        print(f"❌ 交互测试异常: {e}")
        return False


async def test_javascript_execution():
    """测试JavaScript执行功能"""
    print("\n测试JavaScript执行功能...")
    try:
        async with BrowserTools() as tools:
            await tools.navigate_to_url("https://httpbin.org/get")

            # 执行简单的JavaScript
            result = await tools.execute_javascript("return window.location.href")
            if result["success"]:
                print(f"✅ JavaScript执行成功: {result['result']}")
                return True
            else:
                print(f"❌ JavaScript执行失败: {result.get('error', '未知错误')}")
                return False
    except Exception as e:
        print(f"❌ JavaScript测试异常: {e}")
        return False


async def test_mcp_tools():
    """测试MCP工具列表"""
    print("\n测试MCP工具列表...")
    try:
        from mcp_browser_tools.server import server

        # 获取工具列表
        list_tools_request = type('obj', (object,), {
            'method': 'tools/list',
            'params': {}
        })()

        # 这里只是测试工具定义是否正确
        tools = server.list_tools()
        print("✅ MCP工具列表获取成功")
        print(f"   - 可用工具数量: {len(tools.tools)}")

        for tool in tools.tools:
            print(f"   - {tool.name}: {tool.description}")

        return True
    except Exception as e:
        print(f"❌ MCP工具列表测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("开始测试MCP浏览器工具...\n")

    tests = [
        ("MCP工具列表", test_mcp_tools),
        ("导航功能", test_navigation),
        ("内容提取", test_content_extraction),
        ("交互功能", test_interactions),
        ("JavaScript执行", test_javascript_execution),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            failed += 1
            traceback.print_exc()

    print("\n" + "="*50)
    print(f"测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("所有测试通过！工具可以正常使用。")
        sys.exit(0)
    else:
        print(f"有 {failed} 个测试失败，请检查相关配置。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())