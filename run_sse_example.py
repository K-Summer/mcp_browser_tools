"""
运行 SSE 服务器示例
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_sse_server():
    """运行 SSE 服务器"""
    print("启动 MCP Browser Tools (SSE 模式)...")

    from mcp_browser_tools.config import ServerConfig
    from mcp_browser_tools.transport import create_transport
    from mcp.server import Server

    # 创建 SSE 配置
    config = ServerConfig(
        transport_mode="sse",
        sse_host="localhost",
        sse_port=8000
    )

    # 创建传输层
    transport = create_transport(config)

    # 创建 MCP 服务器
    server = Server(config.server_name)

    print(f"SSE 服务器地址: http://{config.sse_host}:{config.sse_port}")
    print("可用端点:")
    print("  - GET /sse      : 简单的 SSE 事件流")
    print("  - GET /mcp-sse  : MCP over SSE 端点")
    print("  - WS /ws        : WebSocket 双向通信")
    print("\n按 Ctrl+C 停止服务器")

    try:
        # 启动服务器
        await transport.run(
            server,
            {
                "server_name": config.server_name,
                "server_version": config.server_version
            }
        )
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        await transport.stop()
        print("服务器已停止")

async def test_sse_client():
    """测试 SSE 客户端连接"""
    print("\n测试 SSE 客户端连接...")

    import aiohttp
    import json

    try:
        async with aiohttp.ClientSession() as session:
            # 连接到 SSE 端点
            print("连接到 SSE 端点...")
            async with session.get("http://localhost:8000/sse") as response:
                if response.status == 200:
                    print("连接成功，等待事件...")

                    # 读取前几个事件
                    event_count = 0
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            print(f"事件 {event_count + 1}: {data}")
                            event_count += 1

                            if event_count >= 3:
                                break
                else:
                    print(f"连接失败: HTTP {response.status}")

    except Exception as e:
        print(f"客户端测试失败: {e}")

async def main():
    """主函数"""
    print("="*50)
    print("MCP Browser Tools SSE 服务器示例")
    print("="*50)

    # 启动服务器
    server_task = asyncio.create_task(run_sse_server())

    # 等待服务器启动
    await asyncio.sleep(3)

    # 测试客户端连接
    await test_sse_client()

    # 等待服务器运行
    try:
        await server_task
    except KeyboardInterrupt:
        print("\n程序结束")

if __name__ == "__main__":
    asyncio.run(main())