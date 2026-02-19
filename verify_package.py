#!/usr/bin/env python3
"""
验证打包结果
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"运行: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  成功")
            return True, result.stdout
        else:
            print(f"  失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"  异常: {e}")
        return False, str(e)

def main():
    """主函数"""
    print("=" * 60)
    print("验证打包结果")
    print("=" * 60)

    # 1. 检查构建文件
    print("\n1. 检查构建文件...")
    if os.path.exists("dist/mcp_browser_tools-0.1.0.tar.gz"):
        print("  ✅ tar.gz 文件存在")
    else:
        print("  ❌ tar.gz 文件不存在")
        return False

    if os.path.exists("dist/mcp_browser_tools-0.1.0-py3-none-any.whl"):
        print("  ✅ wheel 文件存在")
    else:
        print("  ❌ wheel 文件不存在")
        return False

    # 2. 测试安装
    print("\n2. 测试安装...")

    # 创建临时目录测试安装
    temp_dir = "test_install"
    os.makedirs(temp_dir, exist_ok=True)

    # 复制wheel文件到临时目录
    import shutil
    wheel_file = "dist/mcp_browser_tools-0.1.0-py3-none-any.whl"
    temp_wheel = os.path.join(temp_dir, os.path.basename(wheel_file))
    shutil.copy(wheel_file, temp_wheel)

    # 在临时目录中安装
    os.chdir(temp_dir)

    # 使用pip安装
    success, output = run_command(
        f"pip install {os.path.basename(wheel_file)} --no-deps",
        "安装wheel包"
    )

    if not success:
        print("安装失败")
        return False

    # 3. 验证安装
    print("\n3. 验证安装...")

    # 测试导入
    success, output = run_command(
        "python -c \"import mcp_browser_tools; print('导入成功:', mcp_browser_tools.__version__)\"",
        "导入模块"
    )

    if not success:
        print("导入失败")
        return False

    # 测试命令行工具
    success, output = run_command(
        "python -c \"from mcp_browser_tools.server import main; print('服务器模块可用')\"",
        "检查服务器模块"
    )

    if not success:
        print("服务器模块检查失败")
        return False

    # 4. 清理
    print("\n4. 清理...")
    os.chdir("..")
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 5. 验证包内容
    print("\n5. 验证包内容...")

    # 检查tar包中的文件
    success, output = run_command(
        "tar -tzf dist/mcp_browser_tools-0.1.0.tar.gz | grep -E 'mcp_browser_tools/.*\.py$' | wc -l",
        "统计Python文件数量"
    )

    if success:
        file_count = int(output.strip())
        print(f"  ✅ 包中包含 {file_count} 个Python文件")
        if file_count >= 3:  # __init__.py, server.py, browser_tools.py
            print("  ✅ 核心文件完整")
        else:
            print("  ❌ 核心文件可能缺失")
            return False

    # 检查元数据
    success, output = run_command(
        "tar -xzf dist/mcp_browser_tools-0.1.0.tar.gz -O mcp_browser_tools-0.1.0/pyproject.toml | head -20",
        "检查pyproject.toml"
    )

    if success:
        if "mcp-browser-tools" in output:
            print("  ✅ 项目名称正确")
        else:
            print("  ❌ 项目名称不正确")
            return False

    print("\n" + "=" * 60)
    print("✅ 打包验证成功！")
    print("\n分发包已准备就绪：")
    print("  - dist/mcp_browser_tools-0.1.0.tar.gz")
    print("  - dist/mcp_browser_tools-0.1.0-py3-none-any.whl")
    print("\n可以发布到PyPI：")
    print("  twine upload dist/*")
    print("=" * 60)

    return True

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