"""
Stdio 传输协议
通过标准输入输出进行通信
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

from mcp.server.stdio import stdio_server
from .base import TransportBase

logger = logging.getLogger(__name__)


class StdioTransport(TransportBase):
    """Stdio 传输协议"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.read_stream = None
        self.write_stream = None

    async def start(self, server, server_info: Dict[str, Any]) -> None:
        """启动 stdio 传输"""
        logger.info("启动 stdio 传输协议")

        # 输出启动信息
        print("\n" + "=" * 50)
        print("🚀 MCP Browser Tools - Stdio 模式")
        print("=" * 50)
        print("📡 通过标准输入输出进行通信")
        print("📋 支持 JSON-RPC 2.0 协议")
        print("🛠️  可用工具: navigate_to_url, get_page_content, ...")
        print("=" * 50)
        print("\n按 Ctrl+C 停止服务器\n")

        # 使用 stdio 服务器
        async with stdio_server() as (read_stream, write_stream):
            self.read_stream = read_stream
            self.write_stream = write_stream
            self.is_running = True

            # 运行服务器
            await server.run(read_stream, write_stream, server_info)

    async def stop(self) -> None:
        """停止 stdio 传输"""
        self.is_running = False
        logger.info("Stdio 传输协议已停止")

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息（stdio 模式下由 MCP 库自动处理）

        Args:
            message: 输入消息

        Returns:
            Dict[str, Any]: 响应消息
        """
        # stdio 模式下消息处理由 MCP 库完成
        # 这里只记录日志
        logger.debug(f"收到消息: {message}")
        return {"status": "processed_by_mcp"}

    def get_info(self) -> Dict[str, Any]:
        """获取传输协议信息"""
        info = super().get_info()
        info.update({
            "description": "通过标准输入输出进行通信",
            "features": ["JSON-RPC 2.0", "双向通信", "本地集成"],
        })
        return info