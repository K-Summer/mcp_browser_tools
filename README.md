# MCP Browser Tools

MCP (Model Context Protocol) 浏览器自动化工具包，提供网页信息获取和浏览器操作功能，帮助AI模型与网页进行交互。

## 功能特性

- 🌐 **网页导航**：导航到任意URL并等待页面加载完成
- 📄 **内容提取**：获取页面HTML、文本内容和元信息
- 🎯 **元素操作**：点击、填写表单等页面交互操作
- ⏱️ **智能等待**：等待特定元素出现
- 🔍 **信息提取**：提取页面中的链接、图片等结构化信息
- 📸 **截图功能**：截取页面截图
- 💻 **JavaScript执行**：在页面中执行JavaScript代码
- 🔄 **多协议支持**：支持 stdio、SSE 和 Streamable HTTP 三种传输协议
- ⚡ **实时通信**：通过 SSE 和 HTTP Stream 实现服务器推送和双向通信
- 🛡️ **安全验证**：输入验证和错误处理
- 📊 **性能监控**：工具执行时间监控和日志记录

## 安装

```bash
pip install mcp-browser-tools
```

## 快速开始

### 1. 安装 Playwright 浏览器

```bash
playwright install
```

### 2. 运行 MCP 服务器

#### 命令行方式
```bash
# 显示帮助信息
mcp-browser-tools --help

# 使用 stdio 协议（推荐，功能完整）
mcp-browser-tools --transport stdio

# 使用 SSE 协议
mcp-browser-tools --transport sse --host 127.0.0.1 --port 8000

# 使用 HTTP Stream 协议
mcp-browser-tools --transport http_stream --host 0.0.0.0 --port 8080

# 设置日志级别
mcp-browser-tools --transport stdio --log-level DEBUG

# 列出所有可用的传输协议
mcp-browser-tools --list-transports

# 显示版本信息
mcp-browser-tools --version
```

#### 环境变量方式
```bash
# 使用 stdio 协议
export MCP_TRANSPORT_MODE=stdio
mcp-browser-tools

# 使用 SSE 协议
export MCP_TRANSPORT_MODE=sse
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
mcp-browser-tools

# 使用 HTTP Stream 协议
export MCP_TRANSPORT_MODE=http_stream
export MCP_HOST=0.0.0.0
export MCP_PORT=8080
mcp-browser-tools
```

#### Python 模块方式
```bash
# 直接运行模块
python -m mcp_browser_tools --transport stdio

# 使用不同的传输协议
python -m mcp_browser_tools --transport sse --port 9000
python -m mcp_browser_tools --transport http_stream --host localhost
```

### 3. 使用示例

```python
import asyncio
import json
from mcp.server.stdio import stdio_server
from mcp_browser_tools.server import main

async def main():
    # MCP服务器会自动连接到stdio
    await stdio_server(main)

if __name__ == "__main__":
    asyncio.run(main())
```

## 可用工具

### 1. navigate_to_url
导航到指定URL

```json
{
  "name": "navigate_to_url",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 2. get_page_content
获取当前页面内容

```json
{
  "name": "get_page_content",
  "arguments": {}
}
```

### 3. get_page_title
获取页面标题

```json
{
  "name": "get_page_title",
  "arguments": {}
}
```

### 4. click_element
点击页面元素

```json
{
  "name": "click_element",
  "arguments": {
    "selector": "#submit-button"
  }
}
```

### 5. fill_input
填充输入框

```json
{
  "name": "fill_input",
  "arguments": {
    "selector": "#username",
    "text": "myusername"
  }
}
```

### 6. wait_for_element
等待元素出现

```json
{
  "name": "wait_for_element",
  "arguments": {
    "selector": ".result-item",
    "timeout": 30
  }
}
```

### 7. execute_javascript
执行 JavaScript 代码

```json
{
  "name": "execute_javascript",
  "arguments": {
    "script": "return document.title"
  }
}
```

### 8. take_screenshot
截取页面截图

```json
{
  "name": "take_screenshot",
  "arguments": {
    "path": "screenshot.png"
  }
}
```

## 高级功能

### 直接使用 BrowserTools 类

```python
from mcp_browser_tools.browser_tools import BrowserTools
import asyncio

async def main():
    async with BrowserTools() as tools:
        # 导航到网站
        await tools.navigate_to_url("https://example.com")

        # 获取页面内容
        content = await tools.get_page_content()
        print(content["title"])

        # 点击按钮
        await tools.click_element("#submit")

        # 填写表单
        await tools.fill_input("#name", "John Doe")

        # 等待结果
        await tools.wait_for_element(".success-message")

asyncio.run(main())
```

### SSE 客户端连接

```python
import aiohttp
import asyncio

async def connect_sse():
    # 连接到 SSE 端点
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/mcp-sse") as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"服务器事件: {data}")

asyncio.run(connect_sse())
```

### 使用 SSE 双向通信

```python
import asyncio
from sse_client_example import MCPClient

async def main():
    client = MCPClient("http://localhost:8000")

    await client.connect()

    # 获取工具列表
    await client.list_tools()

    # 调用工具
    await client.call_tool("navigate_to_url", {
        "url": "https://example.com"
    })

    await client.disconnect()

asyncio.run(main())
```

### 配置传输模式

```python
from mcp_browser_tools.config import ServerConfig

# 创建 SSE 配置
config = ServerConfig(
    transport_mode="sse",
    sse_host="0.0.0.0",
    sse_port=8000
)

# 运行 SSE 服务器
# await main()
```

### 执行 JavaScript

```python
result = await tools.execute_javascript("return window.location.href")
print(result)
```

### 截图功能

```python
await tools.take_screenshot("page.png")
```

## 配置

### 服务器配置

服务器启动时会输出完整的配置信息，方便下次启动时使用相同的配置。

#### 环境变量配置

支持通过环境变量配置服务器参数：

```bash
# 服务器基本信息
export MCP_SERVER_NAME="mcp-browser-tools"
export MCP_SERVER_VERSION="0.2.3"
export MCP_LOG_LEVEL="INFO"

# 传输模式配置
export MCP_TRANSPORT_MODE="sse"  # 或 "stdio"

# SSE 服务器配置
export MCP_SSE_HOST="localhost"
export MCP_SSE_PORT="8000"
```

#### 配置文件方式

```python
from mcp_browser_tools.config import ServerConfig

# 使用 SSE（默认）
config = ServerConfig(
    transport_mode="sse",
    sse_host="localhost",
    sse_port=8000
)

# 使用 stdio
config = ServerConfig(
    transport_mode="stdio"
)
```

### 自定义浏览器启动参数

```python
from mcp_browser_tools.browser_tools import BrowserTools
from playwright.async_api import async_playwright

async with BrowserTools() as tools:
    tools.browser = await tools.playwright.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage'
        ]
)
```

### 设置用户代理

```python
tools.context = await tools.browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

## 使用场景

### 1. 网页信息爬取

```json
[
  {"name": "navigate_to_url", "arguments": {"url": "https://news.ycombinator.com"}},
  {"name": "get_page_content", "arguments": {}},
  {"name": "get_page_title", "arguments": {}}
]
```

### 2. 自动化表单填写

```json
[
  {"name": "navigate_to_url", "arguments": {"url": "https://example.com/login"}},
  {"name": "fill_input", "arguments": {"selector": "#username", "text": "user"}},
  {"name": "fill_input", "arguments": {"selector": "#password", "text": "pass"}},
  {"name": "click_element", "arguments": {"selector": "#login-button"}}
]
```

### 3. 等待动态内容

```json
[
  {"name": "navigate_to_url", "arguments": {"url": "https://dynamic-site.com"}},
  {"name": "wait_for_element", "arguments": {"selector": ".dynamic-content", "timeout": 60}},
  {"name": "get_page_content", "arguments": {}}
]
```

## 开发

### 安装开发依赖

```bash
uv add --dev pytest pytest-asyncio black isort mypy
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black mcp_browser_tools/
isort mcp_browser_tools/
```

### 类型检查

```bash
mypy mcp_browser_tools/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.2.3
- **版本号升级**：从 0.2.2 升级到 0.2.3
- **配置输出功能**：服务器启动时输出完整的配置信息
- **环境变量支持**：支持通过环境变量配置服务器参数
- **SSE 服务器基础功能**：提供基本的 SSE 服务器功能
- **文档完善**：更新所有文档中的版本信息
- **注意**：SSE 模式目前提供基础功能，推荐使用 stdio 模式获得完整功能

### v0.2.2
- **默认使用 SSE (Server-Sent Events) 传输协议**
- 修复了 SSE 服务器启动问题，确保服务器能正确启动
- 修复了 HTTP 方法错误，SSE 端点现在使用正确的 GET 方法
- 改进了 SSE 服务器线程管理，避免阻塞主事件循环
- 更新了所有相关文档和示例代码

### v0.2.1
- 添加了 SSE (Server-Sent Events) 传输协议支持
- 实现了双协议架构：stdio 和 SSE 两种传输模式
- **默认使用 SSE 传输协议**，提供更好的实时通信体验
- 新增 SSE 服务器端点和 WebSocket 双向通信
- 提供了完整的 SSE 客户端示例
- 修复了入口点配置问题，解决了 uvx 命令的协程警告
- 更新了依赖配置，将已弃用的 `tool.uv.dev-dependencies` 替换为 `dependency-groups.dev`
- 改进了 UTF-8 编码支持，确保所有文件正确使用 UTF-8 编码

### v0.2.0
- 添加了完整的错误处理和重试机制
- 改进了页面内容提取功能，支持自定义提取规则
- 优化了浏览器性能和内存使用
- 增加了详细的日志记录和调试信息
- 完善了配置管理，支持自定义浏览器设置

### v0.1.0
- 初始版本发布
- 支持基本的浏览器操作功能
- MCP 服务器实现