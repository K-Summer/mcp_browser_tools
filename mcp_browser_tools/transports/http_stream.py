"""
Streamable HTTP 传输协议
MCP 规范定义的标准传输协议
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from enum import Enum

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
import threading

from .base import TransportBase

logger = logging.getLogger(__name__)


class HTTPStreamMessageType(str, Enum):
    """HTTP Stream 消息类型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class HTTPStreamTransport(TransportBase):
    """Streamable HTTP 传输协议"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.app = FastAPI(title="MCP Browser Tools HTTP Stream Server")
        self.server_thread: Optional[threading.Thread] = None
        self.mcp_server = None
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.response_queues: Dict[str, asyncio.Queue] = {}

        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 8001)
        self.log_level = self.config.get("log_level", "info")
        self.max_request_size = self.config.get("max_request_size", 1024 * 1024)

        # 设置路由
        self._setup_routes()

    def _setup_routes(self):
        """设置 FastAPI 路由"""

        @self.app.post("/messages")
        async def post_message(request: Request) -> Response:
            """
            发送消息到服务器
            符合 MCP Streamable HTTP 规范
            """
            try:
                # 读取请求体
                body = await request.body()
                if len(body) > self.max_request_size:
                    raise HTTPException(status_code=413, detail="请求体过大")

                # 解析 JSON
                try:
                    message = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError as e:
                    raise HTTPException(status_code=400, detail=f"无效的 JSON: {e}")

                # 验证消息格式
                if not isinstance(message, dict):
                    raise HTTPException(status_code=400, detail="消息必须是 JSON 对象")

                # 生成消息 ID
                message_id = message.get("id") or str(uuid.uuid4())
                message["id"] = message_id

                # 创建响应队列
                response_queue: asyncio.Queue = asyncio.Queue()
                self.response_queues[message_id] = response_queue

                # 将消息放入请求队列
                await self.request_queue.put((message_id, message))

                # 等待响应
                try:
                    response = await asyncio.wait_for(response_queue.get(), timeout=30)
                    return Response(
                        content=json.dumps(response, ensure_ascii=False),
                        media_type="application/json",
                        status_code=200
                    )
                except asyncio.TimeoutError:
                    raise HTTPException(status_code=504, detail="请求超时")
                finally:
                    # 清理响应队列
                    if message_id in self.response_queues:
                        del self.response_queues[message_id]

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")

        @self.app.get("/messages")
        async def get_messages(request: Request) -> StreamingResponse:
            """
            获取服务器消息流
            符合 MCP Streamable HTTP 规范
            """
            async def message_stream() -> AsyncGenerator[str, None]:
                """生成消息流"""
                client_id = str(uuid.uuid4())
                logger.info(f"消息流连接建立: {client_id}")

                try:
                    # 发送连接确认
                    yield json.dumps({
                        "type": "connected",
                        "client_id": client_id,
                        "timestamp": asyncio.get_event_loop().time()
                    }) + "\n"

                    # 处理消息流
                    while True:
                        # 从请求队列获取消息
                        try:
                            message_id, message = await asyncio.wait_for(
                                self.request_queue.get(), timeout=1
                            )
                            yield json.dumps({
                                "type": "request",
                                "id": message_id,
                                "message": message,
                                "timestamp": asyncio.get_event_loop().time()
                            }) + "\n"
                        except asyncio.TimeoutError:
                            # 发送心跳
                            yield json.dumps({
                                "type": "heartbeat",
                                "timestamp": asyncio.get_event_loop().time()
                            }) + "\n"

                except asyncio.CancelledError:
                    logger.info(f"消息流连接结束: {client_id}")
                except Exception as e:
                    logger.error(f"消息流错误: {e}")

            return StreamingResponse(
                message_stream(),
                media_type="application/x-ndjson",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )

        @self.app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """健康检查端点"""
            return {
                "status": "healthy",
                "service": "mcp-browser-tools",
                "version": "0.3.1",
                "transport": "http_stream",
                "active_connections": len(self.response_queues)
            }

        @self.app.get("/info")
        async def server_info() -> Dict[str, Any]:
            """服务器信息端点"""
            return {
                "name": "mcp-browser-tools",
                "version": "0.3.1",
                "protocol": "mcp",
                "transport": "http_stream",
                "capabilities": ["tools/list", "tools/call"],
                "endpoints": {
                    "post_message": f"http://{self.host}:{self.port}/messages",
                    "get_messages": f"http://{self.host}:{self.port}/messages",
                    "health": f"http://{self.host}:{self.port}/health"
                }
            }

    async def start(self, server, server_info: Dict[str, Any]) -> None:
        """启动 HTTP Stream 传输"""
        logger.info(f"启动 HTTP Stream 服务器: {self.host}:{self.port}")

        # 保存 MCP 服务器实例
        self.mcp_server = server

        # 输出启动信息
        print("\n" + "=" * 50)
        print("🚀 MCP Browser Tools - HTTP Stream 模式")
        print("=" * 50)
        print(f"📡 主机: {self.host}")
        print(f"🔌 端口: {self.port}")
        print("🌐 可用端点:")
        print(f"  - POST http://{self.host}:{self.port}/messages (发送消息)")
        print(f"  - GET  http://{self.host}:{self.port}/messages (接收消息流)")
        print(f"  - GET  http://{self.host}:{self.port}/health (健康检查)")
        print(f"  - GET  http://{self.host}:{self.port}/info (服务器信息)")
        print("=" * 50)
        print("📋 协议: MCP Streamable HTTP")
        print("📄 媒体类型: application/x-ndjson")
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
        logger.info("HTTP Stream 服务器已启动")

        # 启动消息处理循环
        asyncio.create_task(self._message_processor())

        # 保持主线程运行
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()

    async def _message_processor(self):
        """消息处理循环"""
        while self.is_running:
            try:
                # 从请求队列获取消息
                message_id, message = await asyncio.wait_for(
                    self.request_queue.get(), timeout=1
                )

                # 处理消息
                response = await self.handle_message(message)

                # 将响应放入对应的队列
                if message_id in self.response_queues:
                    await self.response_queues[message_id].put(response)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"消息处理循环错误: {e}")

    async def stop(self) -> None:
        """停止 HTTP Stream 传输"""
        self.is_running = False
        logger.info("HTTP Stream 传输协议已停止")

    async def _handle_custom_method(self, method: str, params: Dict[str, Any], message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理 HTTP Stream 特有的方法"""
        if method == "server/info":
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "name": "mcp-browser-tools",
                    "version": "0.3.1",
                    "capabilities": ["tools/list", "tools/call"]
                }
            }
        return None

    def get_info(self) -> Dict[str, Any]:
        """获取传输协议信息"""
        info = super().get_info()
        info.update({
            "host": self.host,
            "port": self.port,
            "description": "MCP Streamable HTTP 传输协议",
            "protocol": "MCP Streamable HTTP",
            "features": ["双向通信", "HTTP 兼容", "流式传输", "NDJSON 格式"],
            "endpoints": [
                f"http://{self.host}:{self.port}/messages (POST)",
                f"http://{self.host}:{self.port}/messages (GET)",
                f"http://{self.host}:{self.port}/health",
                f"http://{self.host}:{self.port}/info"
            ],
            "media_types": {
                "request": "application/json",
                "response": "application/x-ndjson"
            }
        })
        return info