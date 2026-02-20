# MCP Browser Tools API 参考

## 目录
- [命令行接口](#命令行接口)
- [Python API](#python-api)
- [MCP 协议接口](#mcp-协议接口)
- [配置类](#配置类)
- [工具类](#工具类)
- [传输协议](#传输协议)
- [工具函数](#工具函数)

## 命令行接口

### mcp-browser-tools

主命令行工具，用于启动 MCP 服务器。

**语法：**
```bash
mcp-browser-tools [选项]
```

**选项：**

| 选项 | 缩写 | 描述 | 默认值 |
|------|------|------|--------|
| `--help` | `-h` | 显示帮助信息 | - |
| `--version` | `-v` | 显示版本信息 | - |
| `--list-transports` | - | 列出所有可用的传输协议 | - |
| `--transport` | `-t` | 传输模式：stdio, sse, http_stream | `stdio` |
| `--host` | - | 服务器主机地址 | `127.0.0.1` |
| `--port` | `-p` | 服务器端口号 | `8000` |
| `--log-level` | `-l` | 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL | `INFO` |
| `--server-name` | - | 服务器名称 | `mcp-browser-tools` |
| `--server-version` | - | 服务器版本 | `0.3.0` |

**示例：**
```bash
# 显示帮助
mcp-browser-tools --help

# 显示版本
mcp-browser-tools --version

# 列出传输协议
mcp-browser-tools --list-transports

# 启动 stdio 服务器
mcp-browser-tools --transport stdio

# 启动 SSE 服务器
mcp-browser-tools --transport sse --host 0.0.0.0 --port 8080 --log-level DEBUG
```

### Python 模块方式

也可以直接运行 Python 模块：

```bash
python -m mcp_browser_tools [选项]
```

## Python API

### 主要模块导入

```python
# 导入主要组件
from mcp_browser_tools import __version__, main, create_server
from mcp_browser_tools.config import ServerConfig, BrowserConfig, ToolConfig
from mcp_browser_tools.browser.tools import BrowserTools
from mcp_browser_tools.transports import TransportMode, create_transport
```

### ServerConfig 类

服务器配置类，用于配置 MCP 服务器。

**构造函数：**
```python
ServerConfig(
    server_name: str = "mcp-browser-tools",
    server_version: str = "0.3.0",
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    transport_mode: TransportMode = TransportMode.STDIO,
    data_dir: str = "~/.mcp-browser-tools",
    transport_config: Dict[str, Any] = None
)
```

**属性：**
- `server_name` (str): 服务器名称
- `server_version` (str): 服务器版本
- `log_level` (str): 日志级别
- `log_format` (str): 日志格式
- `transport_mode` (TransportMode): 传输模式
- `data_dir` (str): 数据目录
- `transport_config` (Dict[str, Any]): 传输协议配置

**类方法：**
- `default() -> ServerConfig`: 创建默认配置
- `from_env() -> ServerConfig`: 从环境变量创建配置

**示例：**
```python
from mcp_browser_tools.config import ServerConfig
from mcp_browser_tools.transports import TransportMode

# 创建 SSE 配置
config = ServerConfig(
    server_name="my-browser-server",
    server_version="1.0.0",
    log_level="DEBUG",
    transport_mode=TransportMode.SSE,
    transport_config={
        "host": "0.0.0.0",
        "port": 8080,
        "log_level": "info"
    }
)

# 使用默认配置
default_config = ServerConfig.default()

# 从环境变量创建配置
env_config = ServerConfig.from_env()
```

### BrowserConfig 类

浏览器配置类，用于配置 Playwright 浏览器。

**构造函数：**
```python
BrowserConfig(
    headless: bool = True,
    timeout: int = 30000,
    viewport: Dict[str, int] = None,
    user_agent: str = None,
    locale: str = "en-US",
    timezone_id: str = "UTC"
)
```

**属性：**
- `headless` (bool): 是否无头模式
- `timeout` (int): 超时时间（毫秒）
- `viewport` (Dict[str, int]): 视口大小，如 `{"width": 1920, "height": 1080}`
- `user_agent` (str): 用户代理字符串
- `locale` (str): 区域设置
- `timezone_id` (str): 时区 ID

### ToolConfig 类

工具配置类，用于配置浏览器工具。

**构造函数：**
```python
ToolConfig(
    max_wait_time: int = 30000,
    default_timeout: int = 10000,
    retry_count: int = 3,
    retry_delay: int = 1000
)
```

**属性：**
- `max_wait_time` (int): 最大等待时间（毫秒）
- `default_timeout` (int): 默认超时时间（毫秒）
- `retry_count` (int): 重试次数
- `retry_delay` (int): 重试延迟（毫秒）

## MCP 协议接口

### 服务器接口

MCP Browser Tools 实现了标准的 MCP 服务器接口：

#### 初始化
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client-name",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

#### 列出工具
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 2
}
```

响应示例：
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "navigate_to_url",
        "description": "导航到指定URL",
        "inputSchema": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "description": "目标URL"
            }
          },
          "required": ["url"]
        }
      },
      // ... 其他工具
    ]
  },
  "id": 2
}
```

#### 调用工具
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "navigate_to_url",
    "arguments": {
      "url": "https://example.com"
    }
  },
  "id": 3
}
```

响应示例：
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "成功导航到 https://example.com"
      }
    ]
  },
  "id": 3
}
```

### 服务器推送消息

#### 服务器信息
```json
{
  "jsonrpc": "2.0",
  "method": "server/info",
  "params": {
    "name": "mcp-browser-tools",
    "version": "0.3.0"
  }
}
```

#### 服务器状态
```json
{
  "jsonrpc": "2.0",
  "method": "server/status",
  "params": {
    "status": "running",
    "active_connections": 1
  }
}
```

## 工具类

### BrowserTools 类

浏览器工具主类，提供所有浏览器自动化功能。

**构造函数：**
```python
BrowserTools(config: BrowserConfig = None)
```

**异步上下文管理器：**
```python
async with BrowserTools() as tools:
    # 使用工具
    await tools.navigate_to_url("https://example.com")
```

**方法：**

#### 导航方法
- `async navigate_to_url(url: str) -> Dict[str, Any]`: 导航到指定 URL
- `async go_back() -> Dict[str, Any]`: 返回上一页
- `async go_forward() -> Dict[str, Any]`: 前进到下一页
- `async refresh_page() -> Dict[str, Any]`: 刷新当前页面

#### 内容提取方法
- `async get_page_content(format: str = "text") -> Dict[str, Any]`: 获取页面内容
- `async get_page_title() -> Dict[str, Any]`: 获取页面标题
- `async get_page_url() -> Dict[str, Any]`: 获取当前页面 URL
- `async extract_links(filter: str = None) -> Dict[str, Any]`: 提取页面链接
- `async extract_images() -> Dict[str, Any]`: 提取页面图片

#### 元素操作方法
- `async click_element(selector: str, timeout: int = 30000) -> Dict[str, Any]`: 点击元素
- `async fill_input(selector: str, text: str) -> Dict[str, Any]`: 填充输入框
- `async wait_for_element(selector: str, timeout: int = 30000) -> Dict[str, Any]`: 等待元素出现
- `async get_element_text(selector: str) -> Dict[str, Any]`: 获取元素文本
- `async get_element_attribute(selector: str, attribute: str) -> Dict[str, Any]`: 获取元素属性

#### 高级方法
- `async execute_javascript(script: str) -> Dict[str, Any]`: 执行 JavaScript
- `async take_screenshot(path: str = "screenshot.png", full_page: bool = False) -> Dict[str, Any]`: 截取截图
- `async scroll_to(position: str = "bottom") -> Dict[str, Any]`: 滚动页面
- `async switch_to_frame(selector: str = None) -> Dict[str, Any]`: 切换到 iframe
- `async switch_to_main_frame() -> Dict[str, Any]`: 切换回主框架

**示例：**
```python
from mcp_browser_tools.browser.tools import BrowserTools
import asyncio

async def example():
    async with BrowserTools() as tools:
        # 导航
        await tools.navigate_to_url("https://example.com")

        # 获取内容
        content = await tools.get_page_content()
        print(f"页面标题: {content.get('title')}")

        # 操作元素
        await tools.fill_input("#search", "Python")
        await tools.click_element("#search-button")

        # 等待结果
        await tools.wait_for_element(".results", timeout=10000)

        # 截图
        await tools.take_screenshot("search_results.png", full_page=True)

asyncio.run(example())
```

### BrowserManager 类

浏览器管理器，用于管理浏览器实例的生命周期。

**构造函数：**
```python
BrowserManager(config: BrowserConfig = None)
```

**方法：**
- `async start() -> None`: 启动浏览器管理器
- `async stop() -> None`: 停止浏览器管理器
- `async get_tools() -> BrowserTools`: 获取浏览器工具实例
- `async cleanup() -> None`: 清理资源

**示例：**
```python
from mcp_browser_tools.browser.manager import BrowserManager
import asyncio

async def example():
    manager = BrowserManager()
    await manager.start()

    try:
        # 获取工具实例
        tools = await manager.get_tools()

        # 使用工具
        await tools.navigate_to_url("https://example.com")
        content = await tools.get_page_content()
        print(content)

        # 可以多次获取工具实例，共享浏览器
        tools2 = await manager.get_tools()
        await tools2.navigate_to_url("https://python.org")

    finally:
        await manager.stop()

asyncio.run(example())
```

## 传输协议

### TransportMode 枚举

传输模式枚举，定义支持的传输协议。

```python
from enum import Enum

class TransportMode(Enum):
    STDIO = "stdio"          # 标准输入输出
    SSE = "sse"             # Server-Sent Events
    HTTP_STREAM = "http_stream"  # Streamable HTTP
```

### create_transport 函数

创建传输协议实例。

**函数签名：**
```python
def create_transport(
    mode: TransportMode,
    **config: Any
) -> TransportBase
```

**参数：**
- `mode` (TransportMode): 传输模式
- `**config`: 传输协议配置参数

**返回：**
- `TransportBase`: 传输协议实例

**示例：**
```python
from mcp_browser_tools.transports import create_transport, TransportMode

# 创建 SSE 传输
sse_transport = create_transport(
    TransportMode.SSE,
    host="127.0.0.1",
    port=8000,
    log_level="info"
)

# 创建 stdio 传输
stdio_transport = create_transport(TransportMode.STDIO)

# 创建 HTTP Stream 传输
http_transport = create_transport(
    TransportMode.HTTP_STREAM,
    host="0.0.0.0",
    port=8080
)
```

### TransportBase 抽象基类

传输协议基类，定义所有传输协议的通用接口。

**方法：**
- `async start(server: Server, server_info: Dict[str, Any]) -> None`: 启动传输协议
- `async stop() -> None`: 停止传输协议
- `async handle_message(message: Dict[str, Any]) -> Dict[str, Any]`: 处理消息
- `get_info() -> Dict[str, Any]`: 获取传输协议信息

## 工具函数

### 日志工具

#### setup_logging 函数

设置日志配置。

```python
from mcp_browser_tools.utils.logging import setup_logging

setup_logging(
    level: str = "INFO",
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: str = None
)
```

#### log_performance 装饰器

记录函数执行时间的装饰器。

```python
from mcp_browser_tools.utils.logging import log_performance

@log_performance("操作名称")
async def some_operation():
    # 操作代码
    pass
```

### 验证工具

#### validate_url 函数

验证 URL 格式。

```python
from mcp_browser_tools.utils.validation import validate_url

try:
    validate_url("https://example.com")
    print("URL 有效")
except ValueError as e:
    print(f"URL 无效: {e}")
```

#### validate_selector 函数

验证 CSS 选择器。

```python
from mcp_browser_tools.utils.validation import validate_selector

try:
    validate_selector("#my-element")
    print("选择器有效")
except ValueError as e:
    print(f"选择器无效: {e}")
```

### 工具函数示例

```python
import asyncio
from mcp_browser_tools.utils.logging import setup_logging, log_performance
from mcp_browser_tools.utils.validation import validate_url, validate_selector

# 设置日志
setup_logging(level="DEBUG", log_file="browser_tools.log")

# 使用性能监控装饰器
@log_performance("导航操作")
async def navigate_and_extract(url):
    from mcp_browser_tools.browser.tools import BrowserTools

    # 验证 URL
    validate_url(url)

    async with BrowserTools() as tools:
        await tools.navigate_to_url(url)
        content = await tools.get_page_content()
        return content

# 使用验证函数
def process_user_input(url, selector):
    try:
        validate_url(url)
        validate_selector(selector)
        return True
    except ValueError as e:
        print(f"输入验证失败: {e}")
        return False

# 运行示例
async def main():
    if process_user_input("https://example.com", "#content"):
        result = await navigate_and_extract("https://example.com")
        print(f"获取到内容: {result.get('title')}")

asyncio.run(main())
```

## 错误处理

### 异常类

#### BrowserError
浏览器操作基础异常。

```python
from mcp_browser_tools.exceptions import BrowserError

try:
    # 浏览器操作
    pass
except BrowserError as e:
    print(f"浏览器错误: {e}")
```

#### NavigationError
导航错误异常。

```python
from mcp_browser_tools.exceptions import NavigationError

try:
    await tools.navigate_to_url("invalid-url")
except NavigationError as e:
    print(f"导航错误: {e}")
```

#### ElementNotFoundError
元素未找到异常。

```python
from mcp_browser_tools.exceptions import ElementNotFoundError

try:
    await tools.click_element("#non-existent-element")
except ElementNotFoundError as e:
    print(f"元素未找到: {e}")
```

#### TimeoutError
操作超时异常。

```python
from mcp_browser_tools.exceptions import TimeoutError

try:
    await tools.wait_for_element(".slow-element", timeout=1000)
except TimeoutError as e:
    print(f"操作超时: {e}")
```

### 错误处理示例

```python
import asyncio
from mcp_browser_tools.browser.tools import BrowserTools
from mcp_browser_tools.exceptions import (
    BrowserError, NavigationError,
    ElementNotFoundError, TimeoutError
)

async def safe_browser_operation():
    async with BrowserTools() as tools:
        try:
            # 尝试导航
            await tools.navigate_to_url("https://example.com")

            # 尝试操作元素
            await tools.click_element("#some-button")

            # 尝试等待元素
            await tools.wait_for_element(".result", timeout=5000)

            return True

        except NavigationError as e:
            print(f"导航失败: {e}")
            return False

        except ElementNotFoundError as e:
            print(f"元素未找到: {e}")
            # 可以尝试其他选择器或跳过此操作
            return False

        except TimeoutError as e:
            print(f"操作超时: {e}")
            # 可以重试或调整超时时间
            return False

        except BrowserError as e:
            print(f"浏览器错误: {e}")
            return False

        except Exception as e:
            print(f"未知错误: {e}")
            return False

asyncio.run(safe_browser_operation())
```

## 类型提示

项目使用 Python 类型提示，支持静态类型检查。

### 类型定义

```python
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

# 工具响应类型
ToolResponse = Dict[str, Any]

# 页面内容类型
PageContent = Dict[str, Union[str, List[Dict[str, str]]]]

# 元素信息类型
ElementInfo = Dict[str, str]
```

### 类型检查

使用 mypy 进行类型检查：

```bash
mypy mcp_browser_tools/
```

### 类型提示示例

```python
from typing import Dict, Any, Optional
from mcp_browser_tools.browser.tools import BrowserTools

async def get_page_info(url: str) -> Dict[str, Any]:
    """获取页面信息，包含类型提示"""
    async with BrowserTools() as tools:
        # 导航到页面
        nav_result: Dict[str, Any] = await tools.navigate_to_url(url)

        if not nav_result.get("success", False):
            raise ValueError(f"导航失败: {nav_result.get('error')}")

        # 获取页面内容
        content_result: Dict[str, Any] = await tools.get_page_content()

        # 获取页面标题
        title_result: Dict[str, Any] = await tools.get_page_title()

        return {
            "url": url,
            "title": title_result.get("title", ""),
            "content": content_result.get("content", ""),
            "success": True
        }

# 使用函数
async def main():
    result: Dict[str, Any] = await get_page_info("https://example.com")
    print(f"页面标题: {result['title']}")
```

## 测试 API

### 测试工具

项目包含测试工具，用于验证功能。

#### 测试连接

```python
from mcp_browser_tools.test_connection import test_sse_connection

async def test_server():
    success = await test_sse_connection(
        url="http://localhost:8000/sse",
        timeout=5
    )
    print(f"连接测试: {'成功' if success else '失败'}")
```

#### 测试所有端点

```python
from mcp_browser_tools.test_sse_connection import test_all_endpoints

async def test_all():
    await test_all_endpoints()
```

### 测试示例

创建自定义测试：

```python
import asyncio
import aiohttp
from mcp_browser_tools.browser.tools import BrowserTools

async def test_browser_functionality():
    """测试浏览器功能"""
    print("测试浏览器功能...")

    async with BrowserTools() as tools:
        # 测试导航
        print("1. 测试导航...")
        result = await tools.navigate_to_url("https://example.com")
        assert result.get("success", False), "导航失败"
        print("   ✓ 导航成功")

        # 测试获取标题
        print("2. 测试获取标题...")
        title_result = await tools.get_page_title()
        title = title_result.get("title", "")
        assert title, "获取标题失败"
        print(f"   ✓ 获取到标题: {title}")

        # 测试获取内容
        print("3. 测试获取内容...")
        content_result = await tools.get_page_content()
        content = content_result.get("content", "")
        assert content, "获取内容失败"
        print(f"   ✓ 获取到内容长度: {len(content)} 字符")

        # 测试截图
        print("4. 测试截图...")
        screenshot_result = await tools.take_screenshot("test_screenshot.png")
        assert screenshot_result.get("success", False), "截图失败"
        print("   ✓ 截图成功")

    print("所有测试通过！")

# 运行测试
asyncio.run(test_browser_functionality())
```

这个 API 参考文档提供了 MCP Browser Tools 的完整接口说明，包括命令行接口、Python API、MCP 协议接口和各类工具的使用方法。