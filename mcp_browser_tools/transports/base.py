"""
传输协议基类
定义所有传输协议的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging

from mcp.server import Server

logger = logging.getLogger(__name__)


class TransportBase(ABC):
    """传输协议基类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化传输协议

        Args:
            config: 传输协议配置
        """
        self.config = config or {}
        self.is_running = False
        self.server_task: Optional[asyncio.Task] = None

    @abstractmethod
    async def start(self, server: Server, server_info: Dict[str, Any]) -> None:
        """
        启动传输协议

        Args:
            server: MCP 服务器实例
            server_info: 服务器信息
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止传输协议"""
        pass

    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息

        Args:
            message: 输入消息

        Returns:
            Dict[str, Any]: 响应消息
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        获取传输协议信息

        Returns:
            Dict[str, Any]: 传输协议信息
        """
        return {
            "type": self.__class__.__name__,
            "config": self.config,
            "is_running": self.is_running,
        }

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"