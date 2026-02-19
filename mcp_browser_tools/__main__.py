"""
MCP 浏览器工具入口点
"""

import asyncio
import logging
from .config import ServerConfig, setup_logging

# 加载配置
server_config = ServerConfig.default()
setup_logging(server_config)

from .server import main as server_main

def main():
    """入口函数"""
    return asyncio.run(server_main())

if __name__ == "__main__":
    main()