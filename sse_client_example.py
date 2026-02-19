"""
MCP SSE 客户端示例
演示如何使用 SSE 协议连接到 MCP 服务器
"""

import asyncio
import json
import aiohttp
from typing import AsyncGenerator, Dict, Any


class MCPClient:
    """MCP SSE 客户端"""

    def __init__(self, server_url: str = "http://localhost:8000/mcp-sse"):
        self.server_url = server_url
        self.session = None
        self.event_queue = asyncio.Queue()
        self.connected = False

    async def connect(self):
        """连接到 SSE 服务器"""
        try:
            self.session = aiohttp.ClientSession()

            # 建立 SSE 连接
            async with self.session.get(self.server_url) as response:
                if response.status == 200:
                    self.connected = True
                    print("✅ 成功连接到 MCP SSE 服务器")

                    # 监听事件流
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            await self.event_queue.put(data)
                else:
                    print(f"❌ 连接失败: HTTP {response.status}")
                    self.connected = False

        except Exception as e:
            print(f"❌ 连接错误: {e}")
            self.connected = False

    async def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.session:
            await self.session.close()
            self.session = None
        print("🔌 已断开连接")

    async def listen_events(self):
        """监听服务器事件"""
        while self.connected:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                print(f"📥 收到事件: {event.get('method', 'unknown')}")

                # 处理不同类型的事件
                if event.get("method") == "server/info":
                    print(f"🖥️ 服务器信息: {event['params']}")

                elif event.get("method") == "server/status":
                    status = event['params']
                    print(f"📊 服务器状态: {status['status']}, 活跃连接: {status['active_connections']}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ 处理事件错误: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """调用工具"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return None

        tool_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        print(f"🔧 调用工具: {tool_name}")
        print(f"📦 参数: {arguments}")

        # 通过 WebSocket 发送请求
        ws_url = "ws://localhost:8000/ws"
        async with self.session.ws_connect(ws_url) as ws:
            await ws.send_json(tool_request)

            # 等待响应
            response = await ws.receive_json()
            print(f"📤 收到响应: {response}")

            return response

    async def list_tools(self):
        """获取工具列表"""
        if not self.connected:
            print("❌ 未连接到服务器")
            return None

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }

        ws_url = "ws://localhost:8000/ws"
        async with self.session.ws_connect(ws_url) as ws:
            await ws.send_json(request)
            response = await ws.receive_json()

            tools = response.get("result", {}).get("tools", [])
            print(f"🛠️ 可用工具 ({len(tools)} 个):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")

            return response


async def main():
    """主函数"""
    client = MCPClient()

    try:
        # 连接服务器
        await client.connect()

        # 启动事件监听
        listen_task = asyncio.create_task(client.listen_events())

        # 获取工具列表
        print("\n" + "="*50)
        print("获取可用工具列表...")
        await client.list_tools()

        # 演示工具调用
        print("\n" + "="*50)
        print("演示工具调用...")

        # 导航示例
        await client.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        # 获取页面内容示例
        await client.call_tool("get_page_content", {})

        # 等待一段时间观察服务器状态
        print("\n" + "="*50)
        print("等待 10 秒观察服务器状态...")
        await asyncio.sleep(10)

    finally:
        # 清理
        listen_task.cancel()
        await client.disconnect()


async def simple_sse_example():
    """简单的 SSE 连接示例"""
    print("="*50)
    print("简单 SSE 连接示例")
    print("="*50)

    session = aiohttp.ClientSession()

    try:
        # 建立 SSE 连接
        async with session.get("http://localhost:8000/sse") as response:
            print(f"连接状态: {response.status}")

            # 读取事件流
            event_count = 0
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"事件 #{event_count + 1}: {data}")
                    event_count += 1

                    # 只接收前 3 个事件
                    if event_count >= 3:
                        break

    except Exception as e:
        print(f"错误: {e}")
    finally:
        await session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        # 运行简单示例
        asyncio.run(simple_sse_example())
    else:
        # 运行完整示例
        asyncio.run(main())