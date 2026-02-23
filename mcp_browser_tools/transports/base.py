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
        self.mcp_server: Optional[Server] = None

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

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息（默认实现）

        子类可以重写此方法以提供自定义逻辑，
        或者重写 _handle_* 方法来处理特定方法类型。

        Args:
            message: 输入消息

        Returns:
            Dict[str, Any]: 响应消息
        """
        try:
            if self.mcp_server is None:
                return self._error_response(
                    message.get("id"),
                    -32603,
                    "MCP 服务器未初始化"
                )

            method = message.get("method")
            params = message.get("params", {})

            if method == "tools/list":
                return await self._handle_tools_list(message)
            elif method == "tools/call":
                return await self._handle_tools_call(message, params)
            else:
                custom_result = await self._handle_custom_method(method or "", params, message)
                if custom_result is not None:
                    return custom_result
                return self._error_response(
                    message.get("id"),
                    -32601,
                    f"未知的 RPC 方法: {method}"
                )

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return self._error_response(
                message.get("id"),
                -32603,
                f"内部错误: {str(e)}"
            )

    async def _handle_tools_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理 tools/list 方法"""
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "navigate_to_url",
                        "description": "导航到指定URL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"}
                            },
                            "required": ["url"]
                        }
                    }
                ]
            }
        }

    async def _handle_tools_call(self, message: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """处理 tools/call 方法"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"工具 {tool_name} 调用成功，参数: {arguments}"
                    }
                ]
            }
        }

    async def _handle_custom_method(self, method: str, params: Dict[str, Any], message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理自定义方法（子类可重写）

        Args:
            method: 方法名
            params: 参数
            message: 原始消息

        Returns:
            处理结果，如果返回 None 则表示未处理
        """
        return None

    def _error_response(self, message_id: Any, code: int, message: str) -> Dict[str, Any]:
        """生成错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message
            }
        }

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
