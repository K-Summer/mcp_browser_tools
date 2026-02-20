# MCP Browser Tools 使用指南

## 目录
- [安装和配置](#安装和配置)
- [传输协议详解](#传输协议详解)
- [工具使用说明](#工具使用说明)
- [MCP 客户端集成](#mcp-客户端集成)
- [故障排除](#故障排除)
- [高级配置](#高级配置)

## 安装和配置

### 系统要求
- Python 3.12 或更高版本
- Playwright 浏览器（自动安装）
- 网络连接（用于访问网页）

### 安装步骤

#### 1. 安装 Python 包
```bash
# 从 PyPI 安装
pip install mcp-browser-tools

# 或从源码安装
git clone https://github.com/K-Summer/mcp-browser-tools.git
cd mcp-browser-tools
uv build
uv pip install dist/mcp_browser_tools-*.whl
```

#### 2. 安装 Playwright 浏览器
```bash
playwright install
```

#### 3. 验证安装
```bash
# 检查版本
mcp-browser-tools --version

# 测试命令行工具
mcp-browser-tools --help
mcp-browser-tools --list-transports
```

## 传输协议详解

### 1. stdio 协议（标准输入输出）

**适用场景：**
- 命令行工具集成
- 本地开发环境
- 简单的脚本调用

**启动命令：**
```bash
mcp-browser-tools --transport stdio
```

**特点：**
- 通过标准输入输出进行通信
- 无需网络配置
- 适合与 CLI 工具集成
- 功能完整，性能最佳

### 2. SSE 协议（Server-Sent Events）

**适用场景：**
- Web 应用程序
- 需要服务器推送的场景
- 实时数据更新

**启动命令：**
```bash
mcp-browser-tools --transport sse --host 127.0.0.1 --port 8000
```

**可用端点：**
- `http://localhost:8000/sse` - 基本的 SSE 事件流
- `http://localhost:8000/mcp-sse` - MCP over SSE 协议端点
- `ws://localhost:8000/ws` - WebSocket 端点（双向通信）

**特点：**
- 基于 HTTP，兼容性好
- 支持服务器主动推送
- 适合浏览器端集成
- 支持长连接

### 3. HTTP Stream 协议

**适用场景：**
- 流式 API
- 需要双向通信的场景
- 自定义客户端集成

**启动命令：**
```bash
mcp-browser-tools --transport http_stream --host 0.0.0.0 --port 8080
```

**特点：**
- 双向流式通信
- 灵活的数据交换
- 适合自定义协议实现

## 工具使用说明

### 导航工具

#### navigate_to_url
导航到指定 URL。

**参数：**
- `url` (string): 目标 URL

**示例：**
```json
{
  "name": "navigate_to_url",
  "arguments": {
    "url": "https://example.com"
  }
}
```

**响应：**
```json
{
  "content": [
    {
      "type": "text",
      "text": "成功导航到 https://example.com"
    }
  ]
}
```

### 内容提取工具

#### get_page_content
获取当前页面的完整内容。

**参数：**
- `format` (string, 可选): 返回格式，可选 "html" 或 "text"，默认为 "text"

**示例：**
```json
{
  "name": "get_page_content",
  "arguments": {
    "format": "text"
  }
}
```

**响应：**
```json
{
  "content": [
    {
      "type": "text",
      "text": "页面标题: Example Domain\n页面内容: This domain is for use in illustrative examples..."
    }
  ]
}
```

#### get_page_title
获取页面标题。

**参数：** 无

**示例：**
```json
{
  "name": "get_page_title",
  "arguments": {}
}
```

### 元素操作工具

#### click_element
点击页面元素。

**参数：**
- `selector` (string): CSS 选择器
- `timeout` (number, 可选): 等待超时时间（秒），默认为 30

**示例：**
```json
{
  "name": "click_element",
  "arguments": {
    "selector": "#submit-button",
    "timeout": 10
  }
}
```

#### fill_input
填充输入框。

**参数：**
- `selector` (string): CSS 选择器
- `text` (string): 要输入的文本

**示例：**
```json
{
  "name": "fill_input",
  "arguments": {
    "selector": "#username",
    "text": "john_doe"
  }
}
```

#### wait_for_element
等待元素出现。

**参数：**
- `selector` (string): CSS 选择器
- `timeout` (number, 可选): 等待超时时间（秒），默认为 30

**示例：**
```json
{
  "name": "wait_for_element",
  "arguments": {
    "selector": ".loading-spinner",
    "timeout": 60
  }
}
```

### 高级工具

#### execute_javascript
在页面中执行 JavaScript 代码。

**参数：**
- `script` (string): JavaScript 代码

**示例：**
```json
{
  "name": "execute_javascript",
  "arguments": {
    "script": "return document.title"
  }
}
```

#### take_screenshot
截取页面截图。

**参数：**
- `path` (string, 可选): 保存路径，默认为 "screenshot.png"
- `full_page` (boolean, 可选): 是否截取完整页面，默认为 false

**示例：**
```json
{
  "name": "take_screenshot",
  "arguments": {
    "path": "page_screenshot.png",
    "full_page": true
  }
}
```

#### extract_links
提取页面中的所有链接。

**参数：**
- `filter` (string, 可选): 过滤条件，如 ".article a"

**示例：**
```json
{
  "name": "extract_links",
  "arguments": {
    "filter": ".news-item a"
  }
}
```

## MCP 客户端集成

### 使用 Claude Desktop

1. 编辑 Claude Desktop 配置文件：
```json
{
  "mcpServers": {
    "browser-tools": {
      "command": "python",
      "args": [
        "-m",
        "mcp_browser_tools",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

2. 重启 Claude Desktop

### 使用自定义 MCP 客户端

#### Python 客户端示例

```python
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 创建服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_browser_tools", "--transport", "stdio"]
    )

    # 创建客户端会话
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()

            # 列出可用工具
            tools = await session.list_tools()
            print("可用工具:", tools)

            # 调用工具
            result = await session.call_tool(
                "navigate_to_url",
                {"url": "https://example.com"}
            )
            print("导航结果:", result)

            # 获取页面内容
            content = await session.call_tool("get_page_content", {})
            print("页面内容:", content)

asyncio.run(main())
```

#### SSE 客户端示例

```python
import asyncio
import aiohttp
import json

async def connect_to_sse():
    url = "http://localhost:8000/mcp-sse"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"连接到 {url}, 状态码: {response.status}")

            # 读取服务器推送的消息
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"收到消息: {data}")

                    # 处理不同类型的消息
                    if data.get("method") == "server/info":
                        print(f"服务器信息: {data.get('params')}")

                    # 可以在这里发送请求到服务器
                    # 注意：SSE 是单向的，需要额外的 HTTP 请求来发送命令

asyncio.run(connect_to_sse())
```

## 故障排除

### 常见问题

#### 1. 连接被拒绝 (Connection Refused)
**症状：** `net::ERR_CONNECTION_REFUSED`
**解决方案：**
```bash
# 检查服务器是否运行
python check_server.py

# 启动服务器
python -m mcp_browser_tools --transport sse --host localhost --port 8000

# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/macOS
```

#### 2. Playwright 浏览器安装失败
**解决方案：**
```bash
# 手动安装浏览器
playwright install chromium
playwright install firefox
playwright install webkit

# 检查安装
playwright --version
```

#### 3. Unicode 编码错误（Windows）
**症状：** `UnicodeEncodeError: 'gbk' codec can't encode character`
**解决方案：**
- 已修复，确保使用最新版本
- 设置控制台编码：
  ```bash
  chcp 65001  # 设置为 UTF-8
  ```

#### 4. 日志级别错误
**症状：** `KeyError: 'INFO'`
**解决方案：**
- 已修复，确保使用最新版本
- 日志级别使用小写：
  ```bash
  mcp-browser-tools --transport sse --log-level info
  ```

### 调试模式

启用调试日志获取详细信息：

```bash
# 启用 DEBUG 日志
mcp-browser-tools --transport stdio --log-level DEBUG

# 或设置环境变量
export MCP_LOG_LEVEL=DEBUG
mcp-browser-tools --transport stdio
```

## 高级配置

### 环境变量配置

支持以下环境变量：

```bash
# 服务器配置
export MCP_SERVER_NAME="custom-browser-tools"
export MCP_SERVER_VERSION="1.0.0"
export MCP_LOG_LEVEL="INFO"

# 传输协议配置
export MCP_TRANSPORT_MODE="sse"  # stdio, sse, http_stream
export MCP_HOST="0.0.0.0"
export MCP_PORT="8000"

# 浏览器配置
export MCP_BROWSER_HEADLESS="true"
export MCP_BROWSER_TIMEOUT="30000"
```

### 自定义浏览器配置

通过代码自定义浏览器行为：

```python
from mcp_browser_tools.browser.tools import BrowserTools
import asyncio

async def custom_browser():
    async with BrowserTools() as tools:
        # 自定义浏览器启动参数
        tools.browser = await tools.playwright.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ],
            slow_mo=100  # 减慢操作速度，便于调试
        )

        # 自定义上下文
        tools.context = await tools.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )

        # 使用自定义配置的工具
        await tools.navigate_to_url("https://example.com")
        content = await tools.get_page_content()
        print(content)

asyncio.run(custom_browser())
```

### 性能优化

#### 1. 重用浏览器实例
```python
# 创建可重用的浏览器管理器
from mcp_browser_tools.browser.manager import BrowserManager

async def reuse_browser():
    manager = BrowserManager()
    await manager.start()

    try:
        # 多次使用同一个浏览器实例
        for url in ["https://example1.com", "https://example2.com"]:
            tools = await manager.get_tools()
            await tools.navigate_to_url(url)
            content = await tools.get_page_content()
            print(f"{url}: {content['title']}")
    finally:
        await manager.stop()
```

#### 2. 并发控制
```python
import asyncio
from mcp_browser_tools.browser.tools import BrowserTools

async def concurrent_operations():
    # 使用信号量控制并发数
    semaphore = asyncio.Semaphore(3)  # 最多3个并发

    async def process_url(url):
        async with semaphore:
            async with BrowserTools() as tools:
                await tools.navigate_to_url(url)
                return await tools.get_page_title()

    urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
    tasks = [process_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(results)
```

### 安全注意事项

1. **输入验证**：所有用户输入都经过验证，防止注入攻击
2. **资源限制**：默认限制页面加载时间和内存使用
3. **沙箱环境**：浏览器在隔离的环境中运行
4. **日志记录**：所有操作都有详细日志，便于审计

### 监控和日志

启用详细日志记录：

```bash
# 结构化日志输出
mcp-browser-tools --transport stdio --log-level INFO

# 日志文件输出
export MCP_LOG_FILE="browser_tools.log"
mcp-browser-tools --transport stdio
```

查看性能指标：

```python
from mcp_browser_tools.utils.logging import log_performance

# 装饰器自动记录执行时间
@log_performance("操作名称")
async def some_operation():
    # 操作代码
    pass
```

## 更新和维护

### 更新到最新版本

```bash
# 更新 PyPI 包
pip install --upgrade mcp-browser-tools

# 更新源码
cd mcp-browser-tools
git pull
uv build
uv pip install --force-reinstall dist/mcp_browser_tools-*.whl
```

### 报告问题

遇到问题时，请提供以下信息：

1. MCP Browser Tools 版本：`mcp-browser-tools --version`
2. Python 版本：`python --version`
3. 操作系统信息
4. 错误日志和堆栈跟踪
5. 复现步骤

### 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。