"""
Setup configuration for PyPI publishing
"""

from setuptools import setup, find_packages
import os

# 读取 README.md
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "MCP浏览器自动化工具包"

# 读取 pyproject.toml 的依赖
def get_dependencies():
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    # 简单提取依赖，实际项目中建议使用 toml 库
    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if deps_match:
        deps = []
        for line in deps_match.group(1).split('\n'):
            line = line.strip().strip('"').strip("'")
            if line and not line.startswith('#'):
                deps.append(line)
        return deps
    return []

setup(
    name="mcp-browser-tools",
    version="0.1.0",
    description="MCP服务器提供浏览器自动化功能，帮助AI模型获取网页信息",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/mcp-browser-tools",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_dependencies(),
    python_requires=">=3.12",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="mcp browser ai automation web scraping",
    entry_points={
        "console_scripts": [
            "mcp-browser-tools=mcp_browser_tools.server:main",
        ],
    },
)