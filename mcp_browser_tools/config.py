"""
MCP 浏览器工具配置
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

from .transports import TransportMode


@dataclass
class ServerConfig:
    """服务器配置"""
    server_name: str = "mcp-browser-tools"
    server_version: str = "0.3.1"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    transport_mode: TransportMode = TransportMode.STDIO
    data_dir: str = "~/.mcp-browser-tools"

    # 传输协议配置
    transport_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "ServerConfig":
        """从环境变量或默认值创建配置"""
        # 获取传输模式
        transport_mode_str = os.environ.get("MCP_TRANSPORT_MODE", "stdio")
        try:
            transport_mode = TransportMode(transport_mode_str)
        except ValueError:
            transport_mode = TransportMode.STDIO

        # 构建传输配置
        transport_config = {
            "host": os.environ.get("MCP_HOST", "127.0.0.1"),
            "port": int(os.environ.get("MCP_PORT", "8000")),
            "log_level": os.environ.get("MCP_LOG_LEVEL", "info"),
        }

        # 根据传输模式添加特定配置
        if transport_mode == TransportMode.SSE:
            transport_config.update({
                "sse_endpoint": os.environ.get("MCP_SSE_ENDPOINT", "/sse"),
                "mcp_sse_endpoint": os.environ.get("MCP_MCP_SSE_ENDPOINT", "/mcp-sse"),
                "websocket_endpoint": os.environ.get("MCP_WEBSOCKET_ENDPOINT", "/ws"),
            })
        elif transport_mode == TransportMode.HTTP_STREAM:
            transport_config.update({
                "messages_endpoint": os.environ.get("MCP_MESSAGES_ENDPOINT", "/messages"),
                "max_request_size": int(os.environ.get("MCP_MAX_REQUEST_SIZE", "1048576")),  # 1MB
            })

        return cls(
            server_name=os.environ.get("MCP_SERVER_NAME", "mcp-browser-tools"),
            server_version=os.environ.get("MCP_SERVER_VERSION", "0.3.1"),
            log_level=os.environ.get("MCP_LOG_LEVEL", "INFO"),
            transport_mode=transport_mode,
            data_dir=os.environ.get("MCP_DATA_DIR", "~/.mcp-browser-tools"),
            transport_config=transport_config
        )

    def get_transport_config(self) -> Dict[str, Any]:
        """获取传输协议配置"""
        config = self.transport_config.copy()

        # 添加通用配置
        config.update({
            "server_name": self.server_name,
            "server_version": self.server_version,
            "log_level": self.log_level.lower(),
        })

        return config

@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    timeout: int = 30000
    wait_timeout: int = 30000
    click_timeout: int = 5000
    load_timeout: int = 10000

    @classmethod
    def default(cls) -> "BrowserConfig":
        return cls()

@dataclass
class ToolConfig:
    """工具配置"""
    max_content_length: int = 5000
    max_links: int = 100
    max_images: int = 100

    @classmethod
    def default(cls) -> "ToolConfig":
        return cls()

def setup_logging(config: ServerConfig) -> None:
    """设置日志记录"""
    from .utils.logging import setup_logging as setup_logging_util

    setup_logging_util(
        level=config.log_level,
        format_str=config.log_format
    )

def get_data_dir() -> Path:
    """获取数据目录"""
    return Path.home() / ".mcp-browser-tools"