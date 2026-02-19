# MCP Browser Tools

MCP (Model Context Protocol) 浏览器自动化工具包，提供网页信息获取和浏览器操作功能，帮助AI模型与网页进行交互。

## 功能特性

- 🌐 **网页导航**：导航到任意URL并等待页面加载完成
- 📄 **内容提取**：获取页面HTML、文本内容和元信息
- 🎯 **元素操作**：点击、填写表单等页面交互操作
- ⏱️ **智能等待**：等待特定元素出现
- 🔍 **信息提取**：提取页面中的链接、图片等结构化信息

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

```bash
mcp-browser-tools
```

### 3. 使用示例

```python
import json
from mcp.server.stdio import stdio_server
from mcp_browser_tools.server import server

async def main():
    # MCP服务器会自动连接到stdio
    await stdio_server(server)

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

### v0.1.0
- 初始版本发布
- 支持基本的浏览器操作功能
- MCP 服务器实现