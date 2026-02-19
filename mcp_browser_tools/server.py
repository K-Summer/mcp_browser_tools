"""
MCP服务器主程序
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

from .browser_tools import BrowserTools

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("mcp-browser-tools")
browser_tools = BrowserTools()


@server.call_tool()
async def navigate_to_url(arguments: Dict[str, Any]) -> CallToolResult:
    """导航到指定URL"""
    url = arguments.get("url")
    if not url:
        raise ValueError("URL参数是必需的")

    try:
        result = await browser_tools.navigate_to_url(url)
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )
    except Exception as e:
        logger.error(f"导航到URL失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.call_tool()
async def get_page_content(arguments: Dict[str, Any]) -> CallToolResult:
    """获取页面内容"""
    try:
        result = await browser_tools.get_page_content()
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )
    except Exception as e:
        logger.error(f"获取页面内容失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.call_tool()
async def get_page_title(arguments: Dict[str, Any]) -> CallToolResult:
    """获取页面标题"""
    try:
        title = await browser_tools.get_page_title()
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"title": title}, ensure_ascii=False)
                )
            ]
        )
    except Exception as e:
        logger.error(f"获取页面标题失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.call_tool()
async def click_element(arguments: Dict[str, Any]) -> CallToolResult:
    """点击页面元素"""
    selector = arguments.get("selector")
    if not selector:
        raise ValueError("选择器参数是必需的")

    try:
        result = await browser_tools.click_element(selector)
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )
    except Exception as e:
        logger.error(f"点击元素失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.call_tool()
async def fill_input(arguments: Dict[str, Any]) -> CallToolResult:
    """填充输入框"""
    selector = arguments.get("selector")
    text = arguments.get("text")

    if not selector or not text:
        raise ValueError("选择器和文本参数都是必需的")

    try:
        result = await browser_tools.fill_input(selector, text)
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )
    except Exception as e:
        logger.error(f"填充输入框失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.call_tool()
async def wait_for_element(arguments: Dict[str, Any]) -> CallToolResult:
    """等待元素出现"""
    selector = arguments.get("selector")
    timeout = arguments.get("timeout", 30)

    if not selector:
        raise ValueError("选择器参数是必需的")

    try:
        result = await browser_tools.wait_for_element(selector, timeout)
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )
    except Exception as e:
        logger.error(f"等待元素失败: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False)
                )
            ]
        )


@server.list_tools()
async def list_tools(request: ListToolsRequest) -> ListToolsResult:
    """列出所有可用工具"""
    tools = [
        Tool(
            name="navigate_to_url",
            description="导航到指定的URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要访问的URL地址"}
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="get_page_content",
            description="获取当前页面的HTML内容",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_page_title",
            description="获取当前页面的标题",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="click_element",
            description="点击页面上的元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "元素选择器（CSS选择器或XPath）",
                    }
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="fill_input",
            description="在输入框中填写文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "输入框选择器"},
                    "text": {"type": "string", "description": "要填入的文本"},
                },
                "required": ["selector", "text"],
            },
        ),
        Tool(
            name="wait_for_element",
            description="等待元素出现",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "元素选择器"},
                    "timeout": {
                        "type": "number",
                        "description": "超时时间（秒），默认30秒",
                        "default": 30,
                    },
                },
                "required": ["selector"],
            },
        ),
    ]

    return ListToolsResult(tools=tools)


async def main():
    await stdio_server(server)


if __name__ == "__main__":
    asyncio.run(main())