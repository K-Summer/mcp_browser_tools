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
        """异步上下文管理器退出"""
        await self.close_browser()

    async def _ensure_browser_initialized(self) -> None:
        """确保浏览器已初始化"""
        if not self.page:
            await self.start_browser()
        if not self.page:
            raise RuntimeError("页面尚未初始化，无法执行操作。")

    async def start_browser(self) -> None:
        """启动浏览器"""
        async with self._lock:
            if self.browser:
                logger.warning("浏览器已启动，跳过重复启动")
                return

            try:
                logger.info("启动浏览器...")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
                self.context = await self.browser.new_context(
                    user_agent=self.config.user_agent
                )
                self.page = await self.context.new_page()
                logger.info("浏览器启动成功")
            except Exception as e:
                logger.error(f"启动浏览器失败: {e}")
                await self.close_browser()
                raise

    async def close_browser(self) -> None:
        """关闭浏览器"""
        async with self._lock:
            if not self.browser:
                logger.warning("浏览器未启动，无需关闭")
                return

            try:
                logger.info("关闭浏览器...")
                if self.page:
                    await self.page.close()
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
                if self.playwright:
                    await self.playwright.stop()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
            finally:
                self.playwright = None
                self.browser = None
                self.page = None
                self.context = None

    async def _validate_url(self, url: str) -> str:
        """验证并规范化URL"""
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"https://{url}"
        return url

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        try:
            await self._ensure_browser_initialized()
            validated_url = await self._validate_url(url)
            logger.info(f"导航到: {validated_url}")

            await self.page.goto(validated_url, timeout=self.config.timeout, wait_until="networkidle")
            await self.page.wait_for_load_state("networkidle", timeout=self.config.wait_timeout)

            return {
                "success": True,
                "url": validated_url,
                "title": await self.get_page_title()
            }
        except Exception as e:
            logger.error(f"导航到URL失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    async def get_page_content(self) -> Dict[str, Any]:
        """获取页面内容"""
        try:
            await self._ensure_browser_initialized()
            html = await self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            text_content = soup.get_text('\n', strip=True)
            title = soup.title.string if soup.title else ""

            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    "text": link.get_text(strip=True),
                    "href": link['href']
                })

            images = []
            for img in soup.find_all('img', src=True):
                images.append({
                    "src": img['src'],
                    "alt": img.get('alt', '')
                })

            return {
                "success": True,
                "title": title,
                "content_length": len(text_content),
                "text": text_content[:5000],
                "links": links[:100],
                "images": images[:100],
                "full_html": html[:5000]
            }
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_page_title(self) -> str:
        """获取页面标题"""
        try:
            await self._ensure_browser_initialized()
            return await self.page.title()
        except Exception as e:
            logger.error(f"获取页面标题失败: {e}")
            return ""

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """点击页面元素"""
        try:
            await self._ensure_browser_initialized()
            await self.page.click(selector, timeout=self.config.click_timeout)
            await self.page.wait_for_load_state("networkidle", timeout=self.config.load_timeout)

            return {
                "success": True,
                "selector": selector,
                "message": "元素点击成功"
            }
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }

    async def fill_input(self, selector: str, text: str) -> Dict[str, Any]:
        """填充输入框"""
        try:
            await self._ensure_browser_initialized()
            await self.page.fill(selector, "")
            await self.page.fill(selector, text)

            return {
                "success": True,
                "selector": selector,
                "text": text,
                "message": "输入框填充成功"
            }
        except Exception as e:
            logger.error(f"填充输入框失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }

    async def wait_for_element(self, selector: str, timeout: int = 30) -> Dict[str, Any]:
        """等待元素出现"""
        try:
            await self._ensure_browser_initialized()
            element = await self.page.wait_for_selector(selector, timeout=timeout * 1000)

            if element:
                return {
                    "success": True,
                    "selector": selector,
                    "message": f"元素在{timeout}秒内出现"
                }
            else:
                return {
                    "success": False,
                    "selector": selector,
                    "message": f"在{timeout}秒内未找到元素"
                }
        except Exception as e:
            logger.error(f"等待元素失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }

    async def take_screenshot(self, path: str = "screenshot.png") -> Dict[str, Any]:
        """截取屏幕"""
        try:
            await self._ensure_browser_initialized()
            await self.page.screenshot(path=path)
            return {
                "success": True,
                "path": path,
                "message": "截图成功"
            }
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """执行JavaScript代码"""
        try:
            await self._ensure_browser_initialized()
            result = await self.page.evaluate(script)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"执行JavaScript失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_element_text(self, selector: str) -> Dict[str, Any]:
        """获取元素文本内容"""
        try:
            await self._ensure_browser_initialized()
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return {
                    "success": True,
                    "selector": selector,
                    "text": text.strip() if text else ""
                }
            return {
                "success": False,
                "selector": selector,
                "message": "元素未找到"
            }
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }

    async def get_element_attribute(self, selector: str, attribute: str) -> Dict[str, Any]:
        """获取元素属性"""
        try:
            await self._ensure_browser_initialized()
            element = await self.page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return {
                    "success": True,
                    "selector": selector,
                    "attribute": attribute,
                    "value": value
                }
            return {
                "success": False,
                "selector": selector,
                "message": "元素未找到"
            }
        except Exception as e:
            logger.error(f"获取元素属性失败: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }