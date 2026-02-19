"""
MCP 浏览器工具配置
"""

import logging
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerConfig:
    """服务器配置"""
    server_name: str = "mcp-browser-tools"
    server_version: str = "0.2.1"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    transport_mode: str = "sse"  # 传输模式: "stdio" 或 "sse"
    sse_host: str = "localhost"
    sse_port: int = 8000

    @classmethod
    def default(cls) -> "ServerConfig":
        return cls()

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
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format
    )

def get_data_dir() -> Path:
    """获取数据目录"""
    return Path.home() / ".mcp-browser-tools"