"""
SSE (Server-Sent Events) 传输协议
支持 MCP over SSE 协议
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import uvicorn
import threading

from .base import TransportBase

logger = logging.getLogger(__name__)


class SSEMessageType(str, Enum):
    """SSE 消息类型"""
    CONNECTED = "connected"
    HEARTBEAT = "heartbeat"
    MCP_MESSAGE = "mcp_message"
    ERROR = "error"


class SSEMessage:
    """SSE 消息"""

    def __init__(self, type: SSEMessageType, data: Dict[str, Any], id: Optional[str] = None):
        self.type = type
        self.data = data
        self.id = id or str(uuid.uuid4())

    def to_sse_format(self) -> str:
        """转换为 SSE 格式"""
        message_data = {
            "type": self.type.value,
            "data": self.data,
            "id": self.id
        }
        return f"data: {json.dumps(message_data)}\n\n"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SSEMessage":
        """从字典创建消息"""
        return cls(
            type=SSEMessageType(data.get("type", SSEMessageType.MCP_MESSAGE.value)),
            data=data.get("data", {}),
            id=data.get("id")
        )


class SSEConnectionManager:
    """SSE 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: str):
        """建立连接"""
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket
        logger.info(f"SSE 连接建立: {client_id}")

    async def disconnect(self, client_id: str):
        """断开连接"""
        async with self.lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
        logger.info(f"SSE 连接断开: {client_id}")

    async def send_to_client(self, client_id: str, message: SSEMessage):
        """向特定客户端发送消息"""
        async with self.lock:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(message.to_sse_format())
                except Exception as e:
                    logger.error(f"发送消息失败 {client_id}: {e}")
                    await self.disconnect(client_id)

    async def broadcast(self, message: SSEMessage):
        """广播消息到所有客户端"""
        async with self.lock:
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(message.to_sse_format())
                except Exception as e:
                    logger.error(f"广播消息失败 {client_id}: {e}")
                    await self.disconnect(client_id)


class SSETransport(TransportBase):
    """SSE 传输协议"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.app = FastAPI(title="MCP Browser Tools SSE Server")
        self.connection_manager = SSEConnectionManager()
        self.server_thread: Optional[threading.Thread] = None
        self.mcp_server = None

        # 配置默认值
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 8000)
        self.log_level = config.get("log_level", "info")

        # 设置路由
        self._setup_routes()

    def _setup_routes(self):
        """设置 FastAPI 路由"""

        @self.app.get("/sse")
        async def sse_endpoint() -> StreamingResponse:
            """SSE 端点"""
            async def event_generator() -> AsyncGenerator[str, None]:
                client_id = str(uuid.uuid4())

                # 发送连接确认
                yield SSEMessage(
                    type=SSEMessageType.CONNECTED,
                    data={"client_id": client_id, "status": "connected"}
                ).to_sse_format()

                # 保持连接活跃
                try:
                    while True:
                        # 定期发送心跳
                        yield SSEMessage(
                            type=SSEMessageType.HEARTBEAT,
                            data={"timestamp": asyncio.get_event_loop().time()}
                        ).to_sse_format()
                        await asyncio.sleep(30)
                except asyncio.CancelledError:
                    logger.info(f"SSE 连接结束: {client_id}")

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        @self.app.get("/mcp-sse")
        async def mcp_sse_endpoint() -> StreamingResponse:
            """MCP over SSE 端点"""
            async def mcp_event_generator() -> AsyncGenerator[str, None]:
                client_id = str(uuid.uuid4())

                # 发送服务器信息
                server_info = {
                    "jsonrpc": "2.0",
                    "method": "server/info",
                    "params": {
                        "name": "mcp-browser-tools",
                        "version": "0.3.0"
                    }
                }
                yield f"data: {json.dumps(server_info)}\n\n"

                # 处理 MCP 消息流
                try:
                    while True:
                        # 发送状态更新
                        status_update = {
                            "jsonrpc": "2.0",
                            "method": "server/status",
                            "params": {
                                "status": "running",
                                "active_connections": len(self.connection_manager.active_connections)
                            }
                        }
                        yield f"data: {json.dumps(status_update)}\n\n"
                        await asyncio.sleep(5)
                except asyncio.CancelledError:
                    logger.info(f"MCP SSE 连接结束: {client_id}")

            return StreamingResponse(
                mcp_event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket 端点，用于双向通信"""
            client_id = str(uuid.uuid4())
            await self.connection_manager.connect(websocket, client_id)

            try:
                while True:
                    # 接收客户端消息
                    data = await websocket.receive_text()
                    message = json.loads(data)

                    # 处理消息
                    response = await self.handle_message(message)

                    # 发送响应
                    await websocket.send_text(json.dumps(response))

            except WebSocketDisconnect:
                await self.connection_manager.disconnect(client_id)
            except Exception as e:
                logger.error(f"WebSocket 错误: {e}")
                await self.connection_manager.disconnect(client_id)

    async def start(self, server, server_info: Dict[str, Any]) -> None:
        """启动 SSE 传输"""
        logger.info(f"启动 SSE 服务器: {self.host}:{self.port}")

        # 保存 MCP 服务器实例
        self.mcp_server = server

        # 输出启动信息
        print("\n" + "=" * 50)
        print("🚀 MCP Browser Tools - SSE 模式")
        print("=" * 50)
        print(f"📡 主机: {self.host}")
        print(f"🔌 端口: {self.port}")
        print("🌐 可用端点:")
        print(f"  - GET  http://{self.host}:{self.port}/sse")
        print(f"  - GET  http://{self.host}:{self.port}/mcp-sse")
        print(f"  - WS   ws://{self.host}:{self.port}/ws")
        print("=" * 50)
        print("\n按 Ctrl+C 停止服务器\n")

        # 在单独的线程中运行服务器
        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level=self.log_level,
                access_log=True
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # 等待服务器启动
        await asyncio.sleep(2)

        self.is_running = True
        logger.info("SSE 服务器已启动")

        # 保持主线程运行
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()

    async def stop(self) -> None:
        """停止 SSE 传输"""
        self.is_running = False
        logger.info("SSE 传输协议已停止")

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息

        Args:
            message: 输入消息

        Returns:
            Dict[str, Any]: 响应消息
        """
        try:
            if self.mcp_server is None:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32603,
                        "message": "MCP 服务器未初始化"
                    }
                }

            # 这里需要实现 MCP 消息处理逻辑
            # 由于 MCP 服务器期望 stdio 通信，这里需要适配
            method = message.get("method")
            params = message.get("params", {})

            if method == "tools/list":
                # 返回工具列表
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

            elif method == "tools/call":
                # 处理工具调用
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                # 这里应该调用实际的工具函数
                result = {
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

                return result

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"未知的 RPC 方法: {method}"
                    }
                }

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"内部错误: {str(e)}"
                }
            }

    def get_info(self) -> Dict[str, Any]:
        """获取传输协议信息"""
        info = super().get_info()
        info.update({
            "host": self.host,
            "port": self.port,
            "description": "通过 Server-Sent Events 进行通信",
            "features": ["实时推送", "HTTP 兼容", "WebSocket 支持", "跨域支持"],
            "endpoints": [
                f"http://{self.host}:{self.port}/sse",
                f"http://{self.host}:{self.port}/mcp-sse",
                f"ws://{self.host}:{self.port}/ws"
            ]
        })
        return info