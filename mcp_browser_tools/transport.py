"""
传输层抽象
支持 stdio 和 SSE 两种传输方式
"""

from abc import ABC, abstractmethod
import asyncio
from typing import Dict, Any

from .config import ServerConfig
from mcp.server import Server


class TransportBase(ABC):
    """传输层基类"""

    @abstractmethod
    async def run(self, server: Server, server_info: Dict[str, Any]):
        """运行传输层"""
        pass

    @abstractmethod
    async def stop(self):
        """停止传输层"""
        pass


class StdioTransport(TransportBase):
    """_stdio 传输层（保持原有功能）"""

    async def run(self, server: Server, server_info: Dict[str, Any]):
        """运行 stdio 传输"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server_info)

    async def stop(self):
        """停止 stdio 传输（无操作）"""
        pass


class SSETransport(TransportBase):
    """SSE 传输层"""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.server_task = None
        self.is_running = False

    async def run(self, server: Server, server_info: Dict[str, Any]):
        """运行 SSE 传输"""
        from .sse_server import run_sse_server, sse_manager

        self.is_running = True

        # 启动 SSE 服务器
        self.server_task = asyncio.create_task(
            run_sse_server(self.config)
        )

        # 定期广播服务器状态
        async def broadcast_status():
            while self.is_running:
                try:
                    status_message = {
                        "type": "server_status",
                        "data": {
                            "status": "running",
                            "server_name": server_info.get("server_name"),
                            "server_version": server_info.get("server_version"),
                            "active_connections": len(sse_manager.active_connections)
                        }
                    }
                    await sse_manager.broadcast(status_message)
                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"广播状态失败: {e}")
                    break

        # 启动状态广播任务
        status_task = asyncio.create_task(broadcast_status())

        # 等待停止信号
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.is_running = False
            status_task.cancel()
            await self.stop()

    async def stop(self):
        """停止 SSE 传输"""
        self.is_running = False
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass


def create_transport(config: ServerConfig) -> TransportBase:
    """根据配置创建传输层"""

    if config.transport_mode == "stdio":
        return StdioTransport()
    elif config.transport_mode == "sse":
        return SSETransport(config)
    else:
        raise ValueError(f"不支持的传输模式: {config.transport_mode}")