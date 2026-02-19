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

    def __init__(self, config: ServerConfig = None):
        self.config = config

    async def run(self, server: Server, server_info: Dict[str, Any]):
        """运行 stdio 传输"""
        from mcp.server.stdio import stdio_server

        # 输出配置信息
        if self.config:
            print("\n" + "="*50)
            print("MCP Browser Tools 配置信息")
            print("="*50)
            print(f"服务器名称: {self.config.server_name}")
            print(f"服务器版本: {self.config.server_version}")
            print(f"传输模式: {self.config.transport_mode}")
            print(f"日志级别: {self.config.log_level}")
            print("="*50)
            print("\n下次启动时可以使用以下配置:")
            print(f"export MCP_SERVER_NAME='{self.config.server_name}'")
            print(f"export MCP_SERVER_VERSION='{self.config.server_version}'")
            print(f"export MCP_TRANSPORT_MODE='{self.config.transport_mode}'")
            print(f"export MCP_LOG_LEVEL='{self.config.log_level}'")
            print("="*50 + "\n")

        print("✅ 使用 stdio 传输模式")
        print("📡 通过标准输入输出进行通信")
        print("\n按 Ctrl+C 停止服务器\n")

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
        from .sse_server import run_sse_server, sse_manager, set_mcp_server

        self.is_running = True

        # 设置 MCP 服务器实例
        set_mcp_server(server)

        # 启动 SSE 服务器
        self.server_thread = await run_sse_server(self.config)

        print("MCP 服务器已通过 SSE 传输层启动")
        print("等待客户端连接...")
        print("客户端可以通过以下方式连接:")
        print(f"  1. WebSocket: ws://{self.config.sse_host}:{self.config.sse_port}/ws")
        print(f"  2. SSE 端点: http://{self.config.sse_host}:{self.config.sse_port}/mcp-sse")

        # 等待停止信号
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.is_running = False
            await self.stop()

    async def stop(self):
        """停止 SSE 传输"""
        self.is_running = False
        # 服务器线程是守护线程，主程序退出时会自动结束


def create_transport(config: ServerConfig) -> TransportBase:
    """根据配置创建传输层"""

    if config.transport_mode == "stdio":
        return StdioTransport(config)
    elif config.transport_mode == "sse":
        return SSETransport(config)
    else:
        raise ValueError(f"不支持的传输模式: {config.transport_mode}")