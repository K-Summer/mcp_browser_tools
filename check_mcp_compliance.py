#!/usr/bin/env python3
"""
检查MCP浏览器工具是否符合MCP规范
"""

import ast
import inspect
import json
import sys
from typing import Dict, List, Any

def check_server_structure():
    """检查服务器结构"""
    print("1. 检查服务器结构...")

    try:
        # 导入服务器模块
        from mcp_browser_tools.server import server

        # 检查服务器实例
        print(f"  ✅ 服务器实例: {server.name}")

        # 检查是否有list_tools方法
        if hasattr(server, 'list_tools'):
            print("  ✅ 有list_tools装饰器")
        else:
            print("  ❌ 缺少list_tools装饰器")
            return False

        # 检查是否有call_tool方法
        if hasattr(server, 'call_tool'):
            print("  ✅ 有call_tool装饰器")
        else:
            print("  ❌ 缺少call_tool装饰器")
            return False

        return True

    except Exception as e:
        print(f"  ❌ 服务器结构检查失败: {e}")
        return False

def check_tool_definitions():
    """检查工具定义"""
    print("\n2. 检查工具定义...")

    try:
        # 读取服务器文件
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 解析AST
        tree = ast.parse(content)

        # 查找工具定义
        tool_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查是否有装饰器
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr'):
                            if decorator.func.attr == 'call_tool':
                                tool_names.append(node.name)
                                print(f"  ✅ 找到工具: {node.name}")

        # 检查工具数量
        if len(tool_names) >= 1:
            print(f"  ✅ 定义了 {len(tool_names)} 个工具")
        else:
            print("  ❌ 没有定义任何工具")
            return False

        # 检查list_tools函数
        has_list_tools = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'list_tools':
                has_list_tools = True
                break

        if has_list_tools:
            print("  ✅ 有list_tools函数")
        else:
            print("  ❌ 缺少list_tools函数")
            return False

        return True

    except Exception as e:
        print(f"  ❌ 工具定义检查失败: {e}")
        return False

def check_input_schemas():
    """检查输入模式"""
    print("\n3. 检查输入模式...")

    try:
        # 导入服务器模块
        from mcp_browser_tools.server import server

        # 检查工具定义
        tools = [
            {
                "name": "navigate_to_url",
                "required_params": ["url"],
                "optional_params": []
            },
            {
                "name": "get_page_content",
                "required_params": [],
                "optional_params": []
            },
            {
                "name": "get_page_title",
                "required_params": [],
                "optional_params": []
            },
            {
                "name": "click_element",
                "required_params": ["selector"],
                "optional_params": []
            },
            {
                "name": "fill_input",
                "required_params": ["selector", "text"],
                "optional_params": []
            },
            {
                "name": "wait_for_element",
                "required_params": ["selector"],
                "optional_params": ["timeout"]
            }
        ]

        all_ok = True
        for tool in tools:
            print(f"  检查工具: {tool['name']}")

            # 这里我们只能检查工具是否存在，实际参数验证需要运行时
            # 但我们可以检查工具定义是否完整
            try:
                # 尝试获取工具函数
                module = __import__('mcp_browser_tools.server', fromlist=[tool['name']])
                if hasattr(module, tool['name']):
                    print(f"    ✅ 工具函数存在")
                else:
                    print(f"    ❌ 工具函数不存在")
                    all_ok = False
            except:
                print(f"    ⚠️ 无法检查工具函数")

        return all_ok

    except Exception as e:
        print(f"  ❌ 输入模式检查失败: {e}")
        return False

def check_response_format():
    """检查响应格式"""
    print("\n4. 检查响应格式...")

    try:
        # 读取服务器文件检查返回类型
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否使用了正确的返回类型
        required_imports = [
            "CallToolResult",
            "ListToolsResult",
            "TextContent"
        ]

        for import_name in required_imports:
            if import_name in content:
                print(f"  ✅ 使用了 {import_name}")
            else:
                print(f"  ❌ 缺少 {import_name}")
                return False

        # 检查是否使用了正确的返回结构
        if "CallToolResult(" in content and "TextContent(" in content:
            print("  ✅ 使用了正确的响应结构")
        else:
            print("  ❌ 响应结构不正确")
            return False

        return True

    except Exception as e:
        print(f"  ❌ 响应格式检查失败: {e}")
        return False

def check_communication_protocol():
    """检查通信协议"""
    print("\n5. 检查通信协议...")

    try:
        # 检查是否使用了stdio_server
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        if "stdio_server" in content:
            print("  ✅ 使用了stdio_server")
        else:
            print("  ❌ 未使用stdio_server")
            return False

        if "server.run(" in content:
            print("  ✅ 使用了server.run方法")
        else:
            print("  ❌ 未使用server.run方法")
            return False

        return True

    except Exception as e:
        print(f"  ❌ 通信协议检查失败: {e}")
        return False

def check_error_handling():
    """检查错误处理"""
    print("\n6. 检查错误处理...")

    try:
        # 读取服务器文件
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否有错误处理
        error_patterns = [
            "try:",
            "except Exception",
            "logger.error",
            "json.dumps({\"error\""
        ]

        for pattern in error_patterns:
            if pattern in content:
                print(f"  ✅ 包含错误处理: {pattern}")
            else:
                print(f"  ⚠️ 缺少错误处理模式: {pattern}")

        # 检查是否有日志记录
        if "logging.getLogger" in content:
            print("  ✅ 有日志记录")
        else:
            print("  ⚠️ 缺少日志记录")

        return True

    except Exception as e:
        print(f"  ❌ 错误处理检查失败: {e}")
        return False

def check_mcp_best_practices():
    """检查MCP最佳实践"""
    print("\n7. 检查MCP最佳实践...")

    checks = [
        ("有清晰的工具描述", "description=", True),
        ("使用JSON Schema定义输入", "inputSchema=", True),
        ("工具名称有意义", "navigate_to_url", True),
        ("参数有描述", "\"description\":", True),
        ("有默认值设置", "\"default\":", False),  # 可选
        ("使用异步函数", "async def", True),
        ("有类型提示", "-> CallToolResult", True),
    ]

    try:
        with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        all_ok = True
        for check_name, pattern, required in checks:
            if pattern in content:
                status = "✅" if required else "✅"
                print(f"  {status} {check_name}")
            else:
                if required:
                    print(f"  ❌ 缺少: {check_name}")
                    all_ok = False
                else:
                    print(f"  ⚠️ 可选: {check_name} (未实现)")

        return all_ok

    except Exception as e:
        print(f"  ❌ 最佳实践检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MCP规范符合性检查")
    print("=" * 60)

    results = []

    # 运行所有检查
    checks = [
        ("服务器结构", check_server_structure),
        ("工具定义", check_tool_definitions),
        ("输入模式", check_input_schemas),
        ("响应格式", check_response_format),
        ("通信协议", check_communication_protocol),
        ("错误处理", check_error_handling),
        ("最佳实践", check_mcp_best_practices),
    ]

    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"  ❌ {check_name}检查异常: {e}")
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
        print("\n✅ 完全符合MCP规范！")
        print("项目可以正常作为MCP服务器运行。")
    elif passed >= total * 0.8:
        print(f"\n⚠️ 基本符合MCP规范 ({passed}/{total})")
        print("项目可以作为MCP服务器运行，但有一些建议改进。")
    else:
        print(f"\n❌ 不符合MCP规范 ({passed}/{total})")
        print("项目需要修复才能作为MCP服务器运行。")

    # 提供建议
    print("\n" + "=" * 60)
    print("建议改进:")
    print("1. 确保所有工具都有完整的JSON Schema定义")
    print("2. 添加更详细的错误处理和日志记录")
    print("3. 考虑添加资源管理功能（如果需要）")
    print("4. 添加测试用例验证MCP协议兼容性")
    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"检查过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)