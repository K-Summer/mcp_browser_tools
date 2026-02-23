"""
MCP Browser Tools - 浏览器自动化工具包

提供浏览器自动化功能，帮助AI模型获取网页信息
支持 stdio、SSE 和 Streamable HTTP 传输协议
"""

__version__ = "0.3.1"
__author__ = "MCP Browser Tools"

# 导出主要接口
from .server import main, create_server
from .config import ServerConfig, BrowserConfig, ToolConfig
from .browser.tools import BrowserTools
from .transports import TransportMode, create_transport

__all__ = [
    "main",
    "create_server",
    "ServerConfig",
    "BrowserConfig",
    "ToolConfig",
    "BrowserTools",
    "TransportMode",
    "create_transport",
    "__version__"
]