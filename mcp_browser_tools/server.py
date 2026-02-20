"""
MCP 服务器主程序
支持 stdio、SSE 和 Streamable HTTP 传输协议
"""

import asyncio
import json
import logging
import time
from functools import wraps
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

from .browser.tools import BrowserTools
from .config import ServerConfig, BrowserConfig, ToolConfig
from .transports import create_transport, TransportMode
from .utils.logging import setup_logging, log_performance

# 设置日志
logger = logging.getLogger(__name__)


def create_server(config: Optional[ServerConfig] = None) -> Server:
    """
    创建 MCP 服务器实例

    Args:
        config: 服务器配置

    Returns:
        Server: MCP 服务器实例
    """
    config = config or ServerConfig.default()

    # 设置日志
    setup_logging(level=config.log_level)

    # 创建服务器实例
    server = Server(config.server_name)

    # 创建浏览器工具实例
    browser_config = BrowserConfig.default()
    browser_tools = BrowserTools(browser_config)

    def _create_tool_response(result: Dict[str, Any]) -> CallToolResult:
        """创建工具响应"""
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]
        )

    def _create_error_response(error: str) -> CallToolResult:
        """创建错误响应"""
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": error}, ensure_ascii=False)
                )
            ]
        )

    @server.call_tool()
    @log_performance
    async def navigate_to_url(arguments: Dict[str, Any]) -> CallToolResult:
        """导航到指定URL"""
        url = arguments.get("url")
        if not url:
            return _create_error_response("URL参数是必需的")

        try:
            result = await browser_tools.navigate_to_url(url)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"导航到URL失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def get_page_content(arguments: Dict[str, Any]) -> CallToolResult:
        """获取页面内容"""
        try:
            result = await browser_tools.get_page_content()
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def get_page_title(arguments: Dict[str, Any]) -> CallToolResult:
        """获取页面标题"""
        try:
            title = await browser_tools.get_page_title()
            return _create_tool_response({"title": title})
        except Exception as e:
            logger.error(f"获取页面标题失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def click_element(arguments: Dict[str, Any]) -> CallToolResult:
        """点击页面元素"""
        selector = arguments.get("selector")
        if not selector:
            return _create_error_response("选择器参数是必需的")

        try:
            result = await browser_tools.click_element(selector)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def fill_input(arguments: Dict[str, Any]) -> CallToolResult:
        """填充输入框"""
        selector = arguments.get("selector")
        text = arguments.get("text")

        if not selector or not text:
            return _create_error_response("选择器和文本参数都是必需的")

        try:
            result = await browser_tools.fill_input(selector, text)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"填充输入框失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def wait_for_element(arguments: Dict[str, Any]) -> CallToolResult:
        """等待元素出现"""
        selector = arguments.get("selector")
        timeout = arguments.get("timeout", 30)

        if not selector:
            return _create_error_response("选择器参数是必需的")

        try:
            result = await browser_tools.wait_for_element(selector, timeout)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"等待元素失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def take_screenshot(arguments: Dict[str, Any]) -> CallToolResult:
        """截取屏幕"""
        path = arguments.get("path", "screenshot.png")
        try:
            result = await browser_tools.take_screenshot(path)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def execute_javascript(arguments: Dict[str, Any]) -> CallToolResult:
        """执行JavaScript代码"""
        script = arguments.get("script")
        if not script:
            return _create_error_response("JavaScript脚本参数是必需的")

        try:
            result = await browser_tools.execute_javascript(script)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"执行JavaScript失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def get_element_text(arguments: Dict[str, Any]) -> CallToolResult:
        """获取元素文本内容"""
        selector = arguments.get("selector")
        if not selector:
            return _create_error_response("选择器参数是必需的")

        try:
            result = await browser_tools.get_element_text(selector)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return _create_error_response(str(e))

    @server.call_tool()
    @log_performance
    async def get_element_attribute(arguments: Dict[str, Any]) -> CallToolResult:
        """获取元素属性"""
        selector = arguments.get("selector")
        attribute = arguments.get("attribute")
        if not selector or not attribute:
            return _create_error_response("选择器和属性参数都是必需的")

        try:
            result = await browser_tools.get_element_attribute(selector, attribute)
            return _create_tool_response(result)
        except Exception as e:
            logger.error(f"获取元素属性失败: {e}")
            return _create_error_response(str(e))

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
            Tool(
                name="take_screenshot",
                description="截取当前页面屏幕",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "截图保存路径，默认为screenshot.png",
                            "default": "screenshot.png",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="execute_javascript",
                description="执行JavaScript代码",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "要执行的JavaScript代码",
                        }
                    },
                    "required": ["script"],
                },
            ),
            Tool(
                name="get_element_text",
                description="获取元素的文本内容",
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
                name="get_element_attribute",
                description="获取元素的属性值",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "元素选择器（CSS选择器或XPath）",
                        },
                        "attribute": {
                            "type": "string",
                            "description": "要获取的属性名",
                        }
                    },
                    "required": ["selector", "attribute"],
                },
            ),
        ]

        return ListToolsResult(tools=tools)

    return server


async def main():
    """主函数"""
    # 加载配置
    config = ServerConfig.default()

    # 输出启动信息
    print("\n" + "=" * 50)
    print("MCP Browser Tools 启动中...")
    print("=" * 50)
    print(f"版本: {config.server_version}")
    print(f"传输模式: {config.transport_mode.value}")
    print(f"日志级别: {config.log_level}")
    print("=" * 50)

    # 创建服务器
    server = create_server(config)

    # 创建传输协议
    transport_config = config.get_transport_config()
    transport = create_transport(config.transport_mode, **transport_config)

    # 运行服务器
    try:
        await transport.start(
            server,
            {
                "server_name": config.server_name,
                "server_version": config.server_version,
                "transport_mode": config.transport_mode.value,
            }
        )
    except KeyboardInterrupt:
        print("\n\n服务器正在停止...")
        await transport.stop()
        print("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())