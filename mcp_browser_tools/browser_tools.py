"""
浏览器自动化工具实现
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class BrowserTools:
    """浏览器自动化工具类"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close_browser()

    async def start_browser(self) -> None:
        """启动浏览器"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # 有头模式，便于调试
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            self.page = await self.context.new_page()
            logger.info("浏览器启动成功")
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            raise

    async def close_browser(self) -> None:
        """关闭浏览器"""
        try:
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

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """导航到指定URL"""
        if not self.page:
            await self.start_browser()
        if not self.page:
            logger.error("页面尚未初始化，无法导航。")
            return {
                "success": False,
                "error": "页面尚未初始化，无法导航。",
                "url": url
            }

        try:
            # 验证URL格式
            parsed = urlparse(url)
            if not parsed.scheme:
                url = "https://" + url

            logger.info(f"导航到: {url}")
            await self.page.goto(url, timeout=30000, wait_until="networkidle")

            # 等待页面加载
            if self.page is not None:
                await self.page.wait_for_load_state("networkidle", timeout=30000)

            return {
                "success": True,
                "url": url,
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
        if not self.page:
            await self.start_browser()

        try:
            # 获取HTML内容
            if self.page is None:
                raise RuntimeError("页面尚未初始化，无法获取内容。")
            html = await self.page.content()

            # 使用BeautifulSoup解析
            soup = BeautifulSoup(html, 'html.parser')

            # 提取文本内容
            text_content = soup.get_text('\n', strip=True)

            # 提取标题
            title = soup.title.string if soup.title else ""

            # 提取所有链接
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    "text": link.get_text(strip=True),
                    "href": link['href']
                })

            # 提取所有图片
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
                "text": text_content[:5000],  # 限制长度
                "links": links[:100],  # 限制数量
                "images": images[:100],  # 限制数量
                "full_html": html[:5000]  # 返回部分HTML
            }
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_page_title(self) -> str:
        """获取页面标题"""
        if not self.page:
            await self.start_browser()

        try:
            if self.page is not None:
                title = await self.page.title()
                return title
            else:
                logger.error("页面尚未初始化，无法获取标题。")
                return ""
        except Exception as e:
            logger.error(f"获取页面标题失败: {e}")
            return ""

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """点击页面元素"""
        if not self.page:
            await self.start_browser()

        try:
            # 尝试点击元素
            if self.page is not None:
                await self.page.click(selector, timeout=5000)
                await self.page.wait_for_load_state("networkidle", timeout=10000)

                return {
                    "success": True,
                    "selector": selector,
                    "message": "元素点击成功"
                }
            else:
                logger.error("页面尚未初始化，无法点击元素。")
                return {
                    "success": False,
                    "selector": selector,
                    "error": "页面尚未初始化，无法点击元素。"
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
        if not self.page:
            await self.start_browser()

        try:
            # 清空输入框
            if self.page is not None:
                await self.page.fill(selector, "")
                # 填入文本
                await self.page.fill(selector, text)
            else:
                raise RuntimeError("页面尚未初始化，无法填充输入框。")

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
        if not self.page:
            await self.start_browser()

        try:
            # 等待元素出现
            if self.page is not None:
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
            else:
                logger.error("页面尚未初始化，无法等待元素。")
                return {
                    "success": False,
                    "selector": selector,
                    "error": "页面尚未初始化，无法等待元素。"
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
        if not self.page:
            await self.start_browser()

        try:
            if self.page is not None:
                await self.page.screenshot(path=path)
                return {
                    "success": True,
                    "path": path,
                    "message": "截图成功"
                }
            else:
                raise RuntimeError("页面尚未初始化，无法截图。")
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """执行JavaScript代码"""
        if not self.page:
            await self.start_browser()

        try:
            if self.page is not None:
                result = await self.page.evaluate(script)
                return {
                    "success": True,
                    "result": result
                }
            else:
                raise RuntimeError("页面尚未初始化，无法执行JavaScript。")
        except Exception as e:
            logger.error(f"执行JavaScript失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }