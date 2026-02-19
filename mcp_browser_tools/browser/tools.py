"""
浏览器自动化工具实现
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


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


class BrowserTools:
    """浏览器自动化工具类"""

    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig.default()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_browser()

    async def start_browser(self):
        """启动浏览器"""
        async with self._lock:
            if self.browser is None:
                logger.info("启动浏览器...")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox"
                    ]
                )
                self.context = await self.browser.new_context(
                    user_agent=self.config.user_agent,
                    viewport={"width": 1920, "height": 1080}
                )
                self.page = await self.context.new_page()
                logger.info("浏览器启动完成")

    async def close_browser(self):
        """关闭浏览器"""
        async with self._lock:
            if self.browser:
                logger.info("关闭浏览器...")
                await self.browser.close()
                self.browser = None
                self.page = None
                self.context = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        await self.start_browser()

        try:
            logger.info(f"导航到URL: {url}")
            await self.page.goto(url, timeout=self.config.load_timeout, wait_until="networkidle")
            await self.page.wait_for_load_state("networkidle")

            # 获取页面信息
            title = await self.page.title()
            current_url = self.page.url

            return {
                "success": True,
                "url": current_url,
                "title": title,
                "message": f"成功导航到 {current_url}"
            }
        except Exception as e:
            logger.error(f"导航到URL失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"导航到 {url} 失败"
            }

    async def get_page_content(self, max_length: int = 10000) -> Dict[str, Any]:
        """获取页面内容"""
        await self.start_browser()

        try:
            # 获取HTML内容
            html = await self.page.content()

            # 使用BeautifulSoup解析
            soup = BeautifulSoup(html, 'html.parser')

            # 提取文本内容
            text = soup.get_text(separator=' ', strip=True)
            if len(text) > max_length:
                text = text[:max_length] + "..."

            # 提取链接
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('http'):
                    links.append({
                        "url": href,
                        "text": a.get_text(strip=True)[:100]
                    })

            # 提取图片
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                images.append({
                    "src": src,
                    "alt": alt[:100]
                })

            return {
                "success": True,
                "title": await self.page.title(),
                "url": self.page.url,
                "text": text,
                "links_count": len(links),
                "images_count": len(images),
                "links": links[:10],  # 只返回前10个链接
                "images": images[:10]  # 只返回前10个图片
            }
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取页面内容失败"
            }

    async def get_page_title(self) -> str:
        """获取页面标题"""
        await self.start_browser()
        return await self.page.title()

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """点击页面元素"""
        await self.start_browser()

        try:
            logger.info(f"点击元素: {selector}")
            await self.page.click(selector, timeout=self.config.click_timeout)

            return {
                "success": True,
                "selector": selector,
                "message": f"成功点击元素 {selector}"
            }
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e),
                "message": f"点击元素 {selector} 失败"
            }

    async def fill_input(self, selector: str, text: str) -> Dict[str, Any]:
        """填充输入框"""
        await self.start_browser()

        try:
            logger.info(f"填充输入框: {selector} -> {text}")
            await self.page.fill(selector, text)

            return {
                "success": True,
                "selector": selector,
                "text": text,
                "message": f"成功填充输入框 {selector}"
            }
        except Exception as e:
            logger.error(f"填充输入框失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "text": text,
                "error": str(e),
                "message": f"填充输入框 {selector} 失败"
            }

    async def wait_for_element(self, selector: str, timeout: int = 30) -> Dict[str, Any]:
        """等待元素出现"""
        await self.start_browser()

        try:
            logger.info(f"等待元素: {selector}, 超时: {timeout}秒")
            await self.page.wait_for_selector(selector, timeout=timeout * 1000)

            return {
                "success": True,
                "selector": selector,
                "timeout": timeout,
                "message": f"元素 {selector} 已出现"
            }
        except Exception as e:
            logger.error(f"等待元素失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "timeout": timeout,
                "error": str(e),
                "message": f"等待元素 {selector} 超时"
            }

    async def take_screenshot(self, path: str = "screenshot.png") -> Dict[str, Any]:
        """截取页面截图"""
        await self.start_browser()

        try:
            logger.info(f"截取截图: {path}")
            await self.page.screenshot(path=path, full_page=True)

            return {
                "success": True,
                "path": path,
                "message": f"截图已保存到 {path}"
            }
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return {
                "success": False,
                "path": path,
                "error": str(e),
                "message": f"截图保存到 {path} 失败"
            }

    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """执行JavaScript代码"""
        await self.start_browser()

        try:
            logger.info(f"执行JavaScript: {script[:100]}...")
            result = await self.page.evaluate(script)

            return {
                "success": True,
                "script": script,
                "result": result,
                "message": "JavaScript执行成功"
            }
        except Exception as e:
            logger.error(f"执行JavaScript失败: {e}")
            return {
                "success": False,
                "script": script,
                "error": str(e),
                "message": "JavaScript执行失败"
            }

    async def get_element_text(self, selector: str) -> Dict[str, Any]:
        """获取元素文本内容"""
        await self.start_browser()

        try:
            logger.info(f"获取元素文本: {selector}")
            text = await self.page.text_content(selector)

            return {
                "success": True,
                "selector": selector,
                "text": text,
                "message": f"成功获取元素 {selector} 的文本"
            }
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e),
                "message": f"获取元素 {selector} 的文本失败"
            }

    async def get_element_attribute(self, selector: str, attribute: str) -> Dict[str, Any]:
        """获取元素属性"""
        await self.start_browser()

        try:
            logger.info(f"获取元素属性: {selector}.{attribute}")
            value = await self.page.get_attribute(selector, attribute)

            return {
                "success": True,
                "selector": selector,
                "attribute": attribute,
                "value": value,
                "message": f"成功获取元素 {selector} 的属性 {attribute}"
            }
        except Exception as e:
            logger.error(f"获取元素属性失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "attribute": attribute,
                "error": str(e),
                "message": f"获取元素 {selector} 的属性 {attribute} 失败"
            }

    async def get_current_url(self) -> str:
        """获取当前URL"""
        await self.start_browser()
        return self.page.url

    async def reload_page(self) -> Dict[str, Any]:
        """重新加载页面"""
        await self.start_browser()

        try:
            logger.info("重新加载页面")
            await self.page.reload(wait_until="networkidle")

            return {
                "success": True,
                "message": "页面重新加载成功"
            }
        except Exception as e:
            logger.error(f"重新加载页面失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "页面重新加载失败"
            }

    async def go_back(self) -> Dict[str, Any]:
        """返回上一页"""
        await self.start_browser()

        try:
            logger.info("返回上一页")
            await self.page.go_back(wait_until="networkidle")

            return {
                "success": True,
                "message": "返回上一页成功"
            }
        except Exception as e:
            logger.error(f"返回上一页失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "返回上一页失败"
            }

    async def go_forward(self) -> Dict[str, Any]:
        """前进到下一页"""
        await self.start_browser()

        try:
            logger.info("前进到下一页")
            await self.page.go_forward(wait_until="networkidle")

            return {
                "success": True,
                "message": "前进到下一页成功"
            }
        except Exception as e:
            logger.error(f"前进到下一页失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "前进到下一页失败"
            }