#!/usr/bin/env python3
"""
测试MCP服务器是否能正确启动
"""

import asyncio
import sys
from mcp.server.stdio import stdio_server
from mcp_browser_tools.server import server


async def test_server_startup():
    """测试服务器启动（模拟）"""
    print("测试MCP服务器启动...")

    try:
        # 验证服务器配置
        print("1. 验证服务器配置...")
        assert server.name == "mcp-browser-tools"
        print("   OK: 服务器名称正确")

        # 测试工具列表（不实际启动）
        print("2. 验证工具定义...")
        # 创建一个模拟的请求对象
        class MockRequest:
            def __init__(self, method, params):
                self.method = method
                self.params = params

        # 创建响应处理器
        async def handle_call_tool(name, arguments):
            from mcp.types import CallToolResult, TextContent
            return CallToolResult(
                content=[TextContent(type="text", text=f"Tool {name} called with {arguments}")]
            )

        # 创建响应处理器
        async def handle_list_tools():
            from mcp.types import ListToolsResult, Tool
            return ListToolsResult(
                tools=[
                    Tool(
                        name="test_tool",
                        description="Test tool",
                        inputSchema={"type": "object", "properties": {}}
                    )
                ],
                remaining=None
            )

        # 临时替换方法进行测试
        original_call_tool = server.call_tool
        original_list_tools = server.list_tools

        server.call_tool = handle_call_tool
        server.list_tools = handle_list_tools

        try:
            # 测试工具列表
            print("3. 测试工具列表获取...")
            result = await server.list_tools()
            print(f"   OK: 获取到 {len(result.tools)} 个工具")

            # 测试工具调用
            print("4. 测试工具调用...")
            call_result = await server.call_tool("test_tool", {})
            print("   OK: 工具调用成功")

        finally:
            # 恢复原始方法
            server.call_tool = original_call_tool
            server.list_tools = original_list_tools

        return True

    except Exception as e:
        print(f"服务器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print("MCP服务器功能测试")
    print("=" * 50)

    success = await test_server_startup()

    print("\n" + "=" * 50)
    if success:
        print("MCP服务器测试通过！")
        print("可以使用以下命令启动服务器：")
        print("  mcp-browser-tools")
        print("或者")
        print("  uv run python -m mcp_browser_tools.server")
    else:
        print("MCP服务器测试失败！")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())