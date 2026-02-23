"""
数据验证工具
"""

import re
import json
from typing import Dict, Any, Optional, Tuple, List, Callable
from urllib.parse import urlparse


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    验证URL格式

    Args:
        url: 要验证的URL

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not url:
        return False, "URL不能为空"

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "URL格式无效，必须包含协议和域名"

        # 检查协议
        if result.scheme not in ["http", "https"]:
            return False, "URL协议必须是 http 或 https"

        return True, None
    except Exception as e:
        return False, f"URL解析失败: {str(e)}"


def validate_selector(selector: str) -> Tuple[bool, Optional[str]]:
    """
    验证CSS选择器格式

    Args:
        selector: 要验证的选择器

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not selector:
        return False, "选择器不能为空"

    # 基本CSS选择器验证
    if len(selector) > 1000:
        return False, "选择器过长"

    # 检查常见的选择器模式
    css_patterns = [
        r"^[a-zA-Z][a-zA-Z0-9_-]*$",  # 元素选择器
        r"^\.[a-zA-Z][a-zA-Z0-9_-]*$",  # 类选择器
        r"^#[a-zA-Z][a-zA-Z0-9_-]*$",  # ID选择器
        r"^\[[a-zA-Z][a-zA-Z0-9_-]*(?:[~|^$*]?=.*?)?\]$",  # 属性选择器
        r"^[a-zA-Z*][a-zA-Z0-9_-]*\s+[a-zA-Z*][a-zA-Z0-9_-]*$",  # 后代选择器
    ]

    for pattern in css_patterns:
        if re.match(pattern, selector):
            return True, None

    # 如果不是标准CSS选择器，可能是XPath
    if selector.startswith("//") or selector.startswith(".//"):
        # 简单的XPath验证
        if "//" in selector and len(selector) < 500:
            return True, None

    return False, "选择器格式无效"


def validate_json_rpc(message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证JSON-RPC 2.0消息格式

    Args:
        message: 要验证的消息

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(message, dict):
        return False, "消息必须是JSON对象"

    # 检查jsonrpc版本
    if message.get("jsonrpc") != "2.0":
        return False, "jsonrpc版本必须是2.0"

    # 检查方法
    method = message.get("method")
    if not method or not isinstance(method, str):
        return False, "method字段是必需的且必须是字符串"

    # 检查ID（对于请求是必需的，对于通知是可选的）
    message_id = message.get("id")
    if message_id is not None:
        if not isinstance(message_id, (str, int, float)):
            return False, "id字段必须是字符串、数字或null"

    # 检查参数
    params = message.get("params")
    if params is not None:
        if not isinstance(params, (dict, list)):
            return False, "params字段必须是对象或数组"

    return True, None


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证工具参数

    Args:
        tool_name: 工具名称
        arguments: 工具参数

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(arguments, dict):
        return False, "参数必须是字典"

    # 根据工具名称验证参数
    validation_rules = {
        "navigate_to_url": {
            "required": ["url"],
            "optional": [],
            "validators": {
                "url": validate_url
            }
        },
        "click_element": {
            "required": ["selector"],
            "optional": [],
            "validators": {
                "selector": validate_selector
            }
        },
        "fill_input": {
            "required": ["selector", "text"],
            "optional": [],
            "validators": {
                "selector": validate_selector,
                "text": lambda x: (bool(x and isinstance(x, str)), "text不能为空且必须是字符串")
            }
        },
        "wait_for_element": {
            "required": ["selector"],
            "optional": ["timeout"],
            "validators": {
                "selector": validate_selector,
                "timeout": lambda x: (isinstance(x, (int, float)) and x > 0, "timeout必须是正数")
            }
        },
        "execute_javascript": {
            "required": ["script"],
            "optional": [],
            "validators": {
                "script": lambda x: (bool(x and isinstance(x, str)), "script不能为空且必须是字符串")
            }
        },
        "take_screenshot": {
            "required": [],
            "optional": ["path"],
            "validators": {
                "path": lambda x: (isinstance(x, str) and len(x) < 500, "path必须是字符串且长度小于500")
            }
        },
        "get_element_text": {
            "required": ["selector"],
            "optional": [],
            "validators": {
                "selector": validate_selector
            }
        },
        "get_element_attribute": {
            "required": ["selector", "attribute"],
            "optional": [],
            "validators": {
                "selector": validate_selector,
                "attribute": lambda x: (bool(x and isinstance(x, str)), "attribute不能为空且必须是字符串")
            }
        }
    }

    if tool_name not in validation_rules:
        return True, None

    rules: Dict[str, Any] = validation_rules[tool_name]

    required_params: List[str] = rules["required"]
    for required_param in required_params:
        if required_param not in arguments:
            return False, f"缺少必需参数: {required_param}"

    validators: Optional[Dict[str, Callable]] = rules.get("validators")
    for param_name, param_value in arguments.items():
        if validators and param_name in validators:
            validator = validators[param_name]
            is_valid, error_msg = validator(param_value)
            if not is_valid:
                return False, f"参数 {param_name} 无效: {error_msg}"

    return True, None


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    清理输入字符串

    Args:
        input_str: 输入字符串
        max_length: 最大长度

    Returns:
        str: 清理后的字符串
    """
    if not isinstance(input_str, str):
        return ""

    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x1F\x7F]', '', input_str)

    # 截断长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned.strip()


def validate_port(port: int) -> Tuple[bool, Optional[str]]:
    """
    验证端口号

    Args:
        port: 端口号

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(port, int):
        return False, "端口号必须是整数"

    if port < 1 or port > 65535:
        return False, "端口号必须在1-65535范围内"

    return True, None


def validate_host(host: str) -> Tuple[bool, Optional[str]]:
    """
    验证主机地址

    Args:
        host: 主机地址

    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not host:
        return False, "主机地址不能为空"

    # 检查是否是有效的IP地址或主机名
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'

    if re.match(ip_pattern, host):
        # 验证IP地址的每个部分
        parts = host.split('.')
        for part in parts:
            if int(part) > 255:
                return False, "IP地址无效"
        return True, None
    elif re.match(hostname_pattern, host):
        return True, None
    elif host in ["localhost", "127.0.0.1", "0.0.0.0"]:
        return True, None
    else:
        return False, "主机地址格式无效"