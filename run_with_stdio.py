"""
使用 stdio 模式运行 MCP 服务器（推荐）
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """主函数"""
    print("启动 MCP Browser Tools (stdio 模式)...")

    # 设置环境变量使用 stdio 模式
    os.environ["MCP_TRANSPORT_MODE"] = "stdio"

    from mcp_browser_tools.config import ServerConfig
    from mcp_browser_tools.transport import create_transport
    from mcp.server import Server

    # 创建配置
    config = ServerConfig.default()

    # 创建传输层
    transport = create_transport(config)

    # 创建 MCP 服务器
    server = Server(config.server_name)

    print("使用 stdio 传输模式")
    print("通过标准输入输出进行通信")
    print("按 Ctrl+C 停止服务器")

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

if __name__ == "__main__":
    asyncio.run(main())