"""
MCP Browser Tools 命令行入口点
"""

import asyncio
import sys
import argparse
from typing import Optional

from .server import main as server_main, create_server
from .config import ServerConfig
from .transports import TransportMode, get_available_transports


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MCP Browser Tools - 浏览器自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 stdio 传输模式
  python -m mcp_browser_tools --transport stdio

  # 使用 SSE 传输模式
  python -m mcp_browser_tools --transport sse --host 127.0.0.1 --port 8000

  # 使用 HTTP Stream 传输模式
  python -m mcp_browser_tools --transport http_stream --host 0.0.0.0 --port 8080

  # 设置日志级别
  python -m mcp_browser_tools --transport stdio --log-level DEBUG

环境变量:
  MCP_TRANSPORT_MODE    传输模式 (stdio/sse/http_stream)
  MCP_HOST              主机地址
  MCP_PORT              端口号
  MCP_LOG_LEVEL         日志级别
  MCP_SERVER_NAME       服务器名称
  MCP_SERVER_VERSION    服务器版本
        """
    )

    # 传输模式
    parser.add_argument(
        "--transport", "-t",
        type=str,
        choices=[mode.value for mode in TransportMode],
        default="stdio",
        help="传输模式 (默认: stdio)"
    )

    # 网络配置
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="主机地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="端口号 (默认: 8000)"
    )

    # 日志配置
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )

    # 服务器配置
    parser.add_argument(
        "--server-name",
        type=str,
        default="mcp-browser-tools",
        help="服务器名称 (默认: mcp-browser-tools)"
    )
    parser.add_argument(
        "--server-version",
        type=str,
        default="0.3.0",
        help="服务器版本 (默认: 0.3.0)"
    )

    # 其他命令
    parser.add_argument(
        "--list-transports",
        action="store_true",
        help="列出所有可用的传输协议"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="显示版本信息"
    )

    return parser.parse_args()


def list_transports():
    """列出所有可用的传输协议"""
    transports = get_available_transports()

    print("\n" + "=" * 50)
    print("📡 可用的传输协议")
    print("=" * 50)

    for mode, description in transports.items():
        print(f"  {mode}: {description}")

    print("=" * 50)
    print("\n使用示例:")
    print("  python -m mcp_browser_tools --transport stdio")
    print("  python -m mcp_browser_tools --transport sse --port 8000")
    print("  python -m mcp_browser_tools --transport http_stream --host 0.0.0.0")


def show_version():
    """显示版本信息"""
    from . import __version__
    print(f"\nMCP Browser Tools v{__version__}")
    print("浏览器自动化工具，支持 MCP 协议")
    print("GitHub: https://github.com/yourusername/mcp_browser_tools")


def create_config_from_args(args) -> ServerConfig:
    """从命令行参数创建配置"""
    # 设置环境变量（优先级高于默认值）
    import os
    os.environ["MCP_TRANSPORT_MODE"] = args.transport
    os.environ["MCP_HOST"] = args.host
    os.environ["MCP_PORT"] = str(args.port)
    os.environ["MCP_LOG_LEVEL"] = args.log_level
    os.environ["MCP_SERVER_NAME"] = args.server_name
    os.environ["MCP_SERVER_VERSION"] = args.server_version

    # 创建配置
    config = ServerConfig.default()

    # 根据传输模式添加特定配置
    transport_mode = TransportMode(args.transport)
    if transport_mode == TransportMode.SSE:
        config.transport_config.update({
            "sse_endpoint": "/sse",
            "mcp_sse_endpoint": "/mcp-sse",
            "websocket_endpoint": "/ws",
        })
    elif transport_mode == TransportMode.HTTP_STREAM:
        config.transport_config.update({
            "messages_endpoint": "/messages",
            "max_request_size": 1048576,  # 1MB
        })

    return config


def main():
    """主函数"""
    args = parse_args()

    # 处理特殊命令
    if args.list_transports:
        list_transports()
        return 0

    if args.version:
        show_version()
        return 0

    # 创建配置
    config = create_config_from_args(args)

    # 输出启动信息
    print("\n" + "=" * 50)
    print("🚀 MCP Browser Tools 启动中...")
    print("=" * 50)
    print(f"📦 版本: {config.server_version}")
    print(f"📡 传输模式: {config.transport_mode.value}")
    print(f"🌐 主机: {config.transport_config.get('host', '127.0.0.1')}")
    print(f"🔌 端口: {config.transport_config.get('port', 8000)}")
    print(f"📊 日志级别: {config.log_level}")
    print("=" * 50)

    # 运行服务器
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())