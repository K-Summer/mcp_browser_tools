"""
MCP Browser Tools - 浏览器自动化工具包

提供浏览器自动化功能，帮助AI模型获取网页信息
"""

__version__ = "0.2.2"
__author__ = "MCP Browser Tools"

from .server import main
from .browser_tools import BrowserTools, BrowserConfig

__all__ = [
    "main",
    "BrowserTools",
    "BrowserConfig",
    "__version__"
]