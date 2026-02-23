"""
浏览器自动化工具实现
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..config import BrowserConfig

logger = logging.getLogger(__name__)


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

    def _ensure_page(self) -> Page:
        """确保 page 已初始化并返回"""
        if self.page is None:
            raise RuntimeError("浏览器页面未初始化，请先调用 start_browser()")
        return self.page

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
        page = self._ensure_page()

        try:
            logger.info(f"导航到URL: {url}")
            await page.goto(url, timeout=self.config.load_timeout, wait_until="networkidle")
            await page.wait_for_load_state("networkidle")

            title = await page.title()
            current_url = page.url

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
        page = self._ensure_page()

        try:
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            text = soup.get_text(separator=' ', strip=True)
            if len(text) > max_length:
                text = text[:max_length] + "..."

            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if isinstance(href, str) and href.startswith('http'):
                    links.append({
                        "url": href,
                        "text": a.get_text(strip=True)[:100]
                    })

            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                alt_str = str(alt)[:100] if alt else ''
                images.append({
                    "src": src,
                    "alt": alt_str
                })

            return {
                "success": True,
                "title": await page.title(),
                "url": page.url,
                "text": text,
                "links_count": len(links),
                "images_count": len(images),
                "links": links[:10],
                "images": images[:10]
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
        page = self._ensure_page()
        return await page.title()

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """点击页面元素"""
        await self.start_browser()
        page = self._ensure_page()

        try:
            logger.info(f"点击元素: {selector}")
            await page.click(selector, timeout=self.config.click_timeout)

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
        page = self._ensure_page()

        try:
            logger.info(f"填充输入框: {selector} -> {text}")
            await page.fill(selector, text)

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
        page = self._ensure_page()

        try:
            logger.info(f"等待元素: {selector}, 超时: {timeout}秒")
            await page.wait_for_selector(selector, timeout=timeout * 1000)

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
        page = self._ensure_page()

        try:
            logger.info(f"截取截图: {path}")
            await page.screenshot(path=path, full_page=True)

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
        page = self._ensure_page()

        try:
            logger.info(f"执行JavaScript: {script[:100]}...")
            result = await page.evaluate(script)

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
        page = self._ensure_page()

        try:
            logger.info(f"获取元素文本: {selector}")
            text = await page.text_content(selector)

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
        page = self._ensure_page()

        try:
            logger.info(f"获取元素属性: {selector}.{attribute}")
            value = await page.get_attribute(selector, attribute)

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
        page = self._ensure_page()
        return page.url

    async def reload_page(self) -> Dict[str, Any]:
        """重新加载页面"""
        await self.start_browser()
        page = self._ensure_page()

        try:
            logger.info("重新加载页面")
            await page.reload(wait_until="networkidle")

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
        page = self._ensure_page()

        try:
            logger.info("返回上一页")
            await page.go_back(wait_until="networkidle")

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
        page = self._ensure_page()

        try:
            logger.info("前进到下一页")
            await page.go_forward(wait_until="networkidle")

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
