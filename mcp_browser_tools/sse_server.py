"""
MCP SSE 服务器实现
支持 Server-Sent Events 传输协议
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid

from .server import server
from .config import ServerConfig

logger = logging.getLogger(__name__)

class SSEMessage(BaseModel):
    """SSE 消息格式"""
    type: str
    data: Dict[str, Any]
    id: Optional[str] = None

class SSEConnectionManager:
    """SSE 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: str):
        """建立 SSE 连接"""
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket
        logger.info(f"SSE 连接建立: {client_id}")

    async def disconnect(self, client_id: str):
        """断开 SSE 连接"""
        async with self.lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
        logger.info(f"SSE 连接断开: {client_id}")

    async def send_to_client(self, client_id: str, message: SSEMessage):
        """向特定客户端发送消息"""
        async with self.lock:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(
                        f"data: {message.model_dump_json()}\n\n"
                    )
                except Exception as e:
                    logger.error(f"发送消息失败 {client_id}: {e}")
                    await self.disconnect(client_id)

    async def broadcast(self, message: SSEMessage):
        """广播消息到所有客户端"""
        async with self.lock:
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(
                        f"data: {message.model_dump_json()}\n\n"
                    )
                except Exception as e:
                    logger.error(f"广播消息失败 {client_id}: {e}")
                    await self.disconnect(client_id)

# 创建 SSE 连接管理器
sse_manager = SSEConnectionManager()

# 创建 FastAPI 应用
sse_app = FastAPI()

@sse_app.post("/sse")
async def sse_endpoint() -> StreamingResponse:
    """SSE 端点，服务器推送事件到客户端"""

    async def event_generator() -> AsyncGenerator[str, None]:
        """生成 SSE 事件流"""
        client_id = str(uuid.uuid4())

        # 发送连接确认
        yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\n\n"

        # 保持连接活跃
        try:
            while True:
                # 定期发送心跳
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info(f"SSE 连接结束: {client_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@sse_app.post("/mcp-sse")
async def mcp_sse_endpoint() -> StreamingResponse:
    """MCP over SSE 端点"""

    async def mcp_event_generator() -> AsyncGenerator[str, None]:
        """生成 MCP 事件流"""
        client_id = str(uuid.uuid4())

        # 发送 MCP 服务器信息
        server_info = {
            "jsonrpc": "2.0",
            "method": "server/info",
            "params": {
                "name": "mcp-browser-tools",
                "version": "0.2.1"
            }
        }
        yield f"data: {json.dumps(server_info)}\n\n"

        # 处理 MCP 消息流
        try:
            while True:
                # 这里可以实现双向通信逻辑
                # 目前先发送定期状态更新
                status_update = {
                    "jsonrpc": "2.0",
                    "method": "server/status",
                    "params": {
                        "status": "running",
                        "active_connections": len(sse_manager.active_connections)
                    }
                }
                yield f"data: {json.dumps(status_update)}\n\n"
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info(f"MCP SSE 连接结束: {client_id}")

    return StreamingResponse(
        mcp_event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@sse_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点，用于双向通信"""
    client_id = str(uuid.uuid4())
    await sse_manager.connect(websocket, client_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理 MCP 消息
            if message.get("jsonrpc") == "2.0":
                # 处理工具调用等 MCP 消息
                response = await handle_mcp_message(message)
                await websocket.send_text(json.dumps(response))
            else:
                # 处理自定义消息
                await websocket.send_text(json.dumps({
                    "type": "echo",
                    "data": message
                }))
    except WebSocketDisconnect:
        await sse_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        await sse_manager.disconnect(client_id)

async def handle_mcp_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """处理 MCP 消息"""
    try:
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
                        },
                        {
                            "name": "get_page_content",
                            "description": "获取页面内容",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            }

        elif method.startswith("tools/call"):
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
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": f"内部错误: {str(e)}"
            }
        }

async def run_sse_server(config: ServerConfig):
    """运行 SSE 服务器"""
    import uvicorn

    logger.info(f"启动 SSE 服务器: {config.sse_host}:{config.sse_port}")

    config_dict = {
        "host": config.sse_host,
        "port": config.sse_port,
        "log_level": config.log_level.lower(),
        "access_log": True
    }

    # 在实际使用中，需要在新的事件循环中运行服务器
    # 这里使用 asyncio.create_task 来避免阻塞主事件循环
    server_task = asyncio.create_task(
        uvicorn.run(sse_app, **config_dict)
    )

    return server_task