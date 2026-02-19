"""
日志配置工具
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_str: Optional[str] = None,
    **kwargs
) -> None:
    """
    设置日志配置

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        format_str: 日志格式字符串
        **kwargs: 其他配置参数
    """
    # 默认日志格式
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(format_str)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 如果需要，创建文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 设置特定库的日志级别
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info(f"日志配置完成，级别: {level}")


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        logging.Logger: 日志记录器实例
    """
    logger = logging.getLogger(name)

    if level:
        logger.setLevel(getattr(logging, level.upper()))

    return logger


class LogContext:
    """日志上下文管理器"""

    def __init__(self, logger: logging.Logger, level: str = "INFO"):
        self.logger = logger
        self.level = getattr(logging, level.upper())
        self.start_time = None

    def __enter__(self):
        self.start_time = logging.time.time()
        self.logger.log(self.level, "开始执行")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = logging.time.time() - self.start_time
        if exc_type is None:
            self.logger.log(self.level, f"执行完成，耗时: {elapsed:.3f}秒")
        else:
            self.logger.error(f"执行失败，耗时: {elapsed:.3f}秒，错误: {exc_val}")


def log_performance(func):
    """性能监控装饰器"""
    import time
    import functools

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = get_logger(func.__module__)
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} 执行耗时: {elapsed:.3f}秒")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {elapsed:.3f}秒，错误: {e}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = get_logger(func.__module__)
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} 执行耗时: {elapsed:.3f}秒")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {elapsed:.3f}秒，错误: {e}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# 导入 asyncio 用于检查协程函数
import asyncio