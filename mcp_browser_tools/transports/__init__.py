"""
传输协议模块
支持 stdio、SSE 和 Streamable HTTP 传输协议
"""

from enum import Enum
from typing import Type, Dict, Any

from .base import TransportBase
from .stdio import StdioTransport
from .sse import SSETransport
from .http_stream import HTTPStreamTransport


class TransportMode(str, Enum):
    """传输模式枚举"""
    STDIO = "stdio"
    SSE = "sse"
    HTTP_STREAM = "http_stream"


# 传输协议映射
_TRANSPORT_MAP = {
    TransportMode.STDIO: StdioTransport,
    TransportMode.SSE: SSETransport,
    TransportMode.HTTP_STREAM: HTTPStreamTransport,
}


def create_transport(mode: TransportMode, config: Dict[str, Any] = None, **kwargs) -> TransportBase:
    """
    创建传输协议实例

    Args:
        mode: 传输模式
        config: 传输协议配置字典
        **kwargs: 额外的传输协议参数（将合并到config中）

    Returns:
        TransportBase: 传输协议实例
    """
    transport_class = _TRANSPORT_MAP.get(mode)
    if not transport_class:
        raise ValueError(f"不支持的传输模式: {mode}")

    # 合并配置
    merged_config = config or {}
    if kwargs:
        merged_config.update(kwargs)

    return transport_class(config=merged_config)


def get_available_transports() -> dict:
    """获取可用的传输协议列表"""
    return {
        mode.value: transport_class.__doc__ or transport_class.__name__
        for mode, transport_class in _TRANSPORT_MAP.items()
    }


__all__ = [
    "TransportBase",
    "StdioTransport",
    "SSETransport",
    "HTTPStreamTransport",
    "TransportMode",
    "create_transport",
    "get_available_transports",
]