"""
浏览器管理器
管理多个浏览器实例
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .tools import BrowserTools, BrowserConfig

logger = logging.getLogger(__name__)


@dataclass
class BrowserInstance:
    """浏览器实例"""
    id: str
    tools: BrowserTools
    config: BrowserConfig
    created_at: float
    last_used_at: float


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, max_instances: int = 5, idle_timeout: int = 300):
        """
        初始化浏览器管理器

        Args:
            max_instances: 最大浏览器实例数
            idle_timeout: 空闲超时时间（秒）
        """
        self.max_instances = max_instances
        self.idle_timeout = idle_timeout
        self.instances: Dict[str, BrowserInstance] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """启动管理器"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"浏览器管理器已启动，最大实例数: {self.max_instances}")

    async def stop(self):
        """停止管理器"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # 关闭所有浏览器实例
        async with self._lock:
            for instance_id, instance in list(self.instances.items()):
                try:
                    await instance.tools.close_browser()
                    logger.info(f"关闭浏览器实例: {instance_id}")
                except Exception as e:
                    logger.error(f"关闭浏览器实例失败 {instance_id}: {e}")

            self.instances.clear()

        logger.info("浏览器管理器已停止")

    async def get_browser(self, config: Optional[BrowserConfig] = None) -> BrowserTools:
        """
        获取浏览器实例

        Args:
            config: 浏览器配置

        Returns:
            BrowserTools: 浏览器工具实例
        """
        config = config or BrowserConfig.default()

        async with self._lock:
            # 查找可用的浏览器实例
            for instance_id, instance in self.instances.items():
                if instance.config == config:
                    # 更新最后使用时间
                    instance.last_used_at = asyncio.get_event_loop().time()
                    logger.debug(f"重用浏览器实例: {instance_id}")
                    return instance.tools

            # 创建新的浏览器实例
            if len(self.instances) >= self.max_instances:
                # 清理最旧的实例
                await self._cleanup_oldest_instance()

            instance_id = f"browser_{len(self.instances) + 1}"
            tools = BrowserTools(config)
            await tools.start_browser()

            instance = BrowserInstance(
                id=instance_id,
                tools=tools,
                config=config,
                created_at=asyncio.get_event_loop().time(),
                last_used_at=asyncio.get_event_loop().time()
            )

            self.instances[instance_id] = instance
            logger.info(f"创建新的浏览器实例: {instance_id}")

            return tools

    async def release_browser(self, instance_id: str):
        """
        释放浏览器实例

        Args:
            instance_id: 浏览器实例ID
        """
        async with self._lock:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                instance.last_used_at = asyncio.get_event_loop().time()
                logger.debug(f"释放浏览器实例: {instance_id}")

    async def close_browser(self, instance_id: str):
        """
        关闭浏览器实例

        Args:
            instance_id: 浏览器实例ID
        """
        async with self._lock:
            if instance_id in self.instances:
                instance = self.instances.pop(instance_id)
                try:
                    await instance.tools.close_browser()
                    logger.info(f"关闭浏览器实例: {instance_id}")
                except Exception as e:
                    logger.error(f"关闭浏览器实例失败 {instance_id}: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """获取管理器统计信息"""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            active_instances = []
            idle_instances = []

            for instance_id, instance in self.instances.items():
                instance_info = {
                    "id": instance_id,
                    "created_at": instance.created_at,
                    "last_used_at": instance.last_used_at,
                    "idle_time": now - instance.last_used_at,
                    "config": {
                        "headless": instance.config.headless,
                        "timeout": instance.config.timeout
                    }
                }

                if now - instance.last_used_at > self.idle_timeout:
                    idle_instances.append(instance_info)
                else:
                    active_instances.append(instance_info)

            return {
                "total_instances": len(self.instances),
                "max_instances": self.max_instances,
                "active_instances": len(active_instances),
                "idle_instances": len(idle_instances),
                "active_instances_info": active_instances,
                "idle_instances_info": idle_instances
            }

    async def _cleanup_oldest_instance(self):
        """清理最旧的浏览器实例"""
        if not self.instances:
            return

        # 找到最久未使用的实例
        oldest_instance_id = None
        oldest_last_used = float('inf')

        for instance_id, instance in self.instances.items():
            if instance.last_used_at < oldest_last_used:
                oldest_last_used = instance.last_used_at
                oldest_instance_id = instance_id

        if oldest_instance_id:
            await self.close_browser(oldest_instance_id)

    async def _cleanup_loop(self):
        """清理循环"""
        try:
            while True:
                await asyncio.sleep(60)  # 每分钟检查一次

                async with self._lock:
                    now = asyncio.get_event_loop().time()
                    instances_to_remove = []

                    for instance_id, instance in self.instances.items():
                        if now - instance.last_used_at > self.idle_timeout:
                            instances_to_remove.append(instance_id)

                    for instance_id in instances_to_remove:
                        await self.close_browser(instance_id)

                if instances_to_remove:
                    logger.info(f"清理了 {len(instances_to_remove)} 个空闲浏览器实例")

        except asyncio.CancelledError:
            logger.info("清理循环已取消")
        except Exception as e:
            logger.error(f"清理循环错误: {e}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()