#!/usr/bin/env python3
"""
检查打包结果 - 简单版本
"""

import os
import sys
import tarfile

def check_files():
    """检查文件"""
    print("检查打包文件...")

    # 检查tar.gz文件
    tar_file = "dist/mcp_browser_tools-0.1.0.tar.gz"
    if os.path.exists(tar_file):
        print(f"  OK: {tar_file} 存在")
    else:
        print(f"  ERROR: {tar_file} 不存在")
        return False

    # 检查wheel文件
    wheel_file = "dist/mcp_browser_tools-0.1.0-py3-none-any.whl"
    if os.path.exists(wheel_file):
        print(f"  OK: {wheel_file} 存在")
    else:
        print(f"  ERROR: {wheel_file} 不存在")
        return False

    return True

def check_tar_contents():
    """检查tar包内容"""
    print("\n检查tar包内容...")

    tar_file = "dist/mcp_browser_tools-0.1.0.tar.gz"

    try:
        with tarfile.open(tar_file, "r:gz") as tar:
            # 获取所有文件
            members = tar.getmembers()

            # 检查关键文件
            required_files = [
                "mcp_browser_tools-0.1.0/mcp_browser_tools/__init__.py",
                "mcp_browser_tools-0.1.0/mcp_browser_tools/server.py",
                "mcp_browser_tools-0.1.0/mcp_browser_tools/browser_tools.py",
                "mcp_browser_tools-0.1.0/pyproject.toml",
                "mcp_browser_tools-0.1.0/README.md",
                "mcp_browser_tools-0.1.0/LICENSE",
            ]

            found_files = []
            for member in members:
                if member.name in required_files:
                    found_files.append(member.name)
                    print(f"  OK: {member.name}")

            # 检查是否所有必需文件都存在
            missing = set(required_files) - set(found_files)
            if missing:
                print(f"  ERROR: 缺少文件: {missing}")
                return False

            print(f"  OK: 找到 {len(found_files)}/{len(required_files)} 个必需文件")

            # 统计Python文件数量
            py_files = [m for m in members if m.name.endswith('.py')]
            print(f"  OK: 包中包含 {len(py_files)} 个Python文件")

            return True

    except Exception as e:
        print(f"  ERROR: 打开tar文件失败: {e}")
        return False

def check_metadata():
    """检查元数据"""
    print("\n检查元数据...")

    try:
        # 读取pyproject.toml
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()

        # 检查关键字段
        checks = [
            ("name = \"mcp-browser-tools\"", "项目名称"),
            ("version = \"0.1.0\"", "版本号"),
            ("requires-python = \">=3.12\"", "Python版本要求"),
            ("mcp>=", "MCP依赖"),
            ("playwright>=", "Playwright依赖"),
        ]

        for check_str, description in checks:
            if check_str in content:
                print(f"  OK: {description}")
            else:
                print(f"  ERROR: {description} 未找到")
                return False

        return True

    except Exception as e:
        print(f"  ERROR: 读取元数据失败: {e}")
        return False

def check_import():
    """检查导入"""
    print("\n检查导入...")

    try:
        # 测试导入
        import mcp_browser_tools
        print(f"  OK: 导入成功 - 版本: {mcp_browser_tools.__version__}")

        # 测试服务器模块
        from mcp_browser_tools.server import server
        print(f"  OK: 服务器模块导入成功 - 名称: {server.name}")

        # 测试浏览器工具
        from mcp_browser_tools.browser_tools import BrowserTools
        print(f"  OK: BrowserTools类导入成功")

        return True

    except Exception as e:
        print(f"  ERROR: 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MCP浏览器工具 - 打包验证")
    print("=" * 60)

    results = []

    # 运行所有检查
    checks = [
        ("文件检查", check_files),
        ("元数据检查", check_metadata),
        ("包内容检查", check_tar_contents),
        ("导入检查", check_import),
    ]

    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"  ERROR: {check_name}异常: {e}")
            results.append((check_name, False))

    # 显示结果
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)

    passed = 0
    total = len(results)

    for check_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {check_name}")
        if success:
            passed += 1

    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 项通过")

    if passed == total:
        print("\n打包验证成功！")
        print("\n分发包已准备就绪：")
        print("  dist/mcp_browser_tools-0.1.0.tar.gz")
        print("  dist/mcp_browser_tools-0.1.0-py3-none-any.whl")
        print("\n可以发布到PyPI：")
        print("  twine upload dist/*")
        return True
    else:
        print(f"\n有 {total - passed} 项检查未通过")
        return False

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"验证过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)