#!/usr/bin/env python3
"""
简单MCP规范检查
"""

import ast
import sys

def check_imports():
    """检查导入"""
    print("1. 检查导入...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    required_imports = [
        "from mcp.server import Server",
        "from mcp.server.stdio import stdio_server",
        "from mcp.types import",
        "CallToolResult",
        "ListToolsResult",
        "TextContent",
        "Tool"
    ]

    all_ok = True
    for imp in required_imports:
        if imp in content:
            print(f"  OK: {imp}")
        else:
            print(f"  ERROR: 缺少 {imp}")
            all_ok = False

    return all_ok

def check_server_instance():
    """检查服务器实例"""
    print("\n2. 检查服务器实例...")

    try:
        from mcp_browser_tools.server import server

        # 检查服务器名称
        if hasattr(server, 'name'):
            print(f"  OK: 服务器名称: {server.name}")
        else:
            print("  ERROR: 服务器没有名称属性")
            return False

        # 检查装饰器
        if hasattr(server, 'call_tool'):
            print("  OK: 有call_tool装饰器")
        else:
            print("  ERROR: 缺少call_tool装饰器")
            return False

        if hasattr(server, 'list_tools'):
            print("  OK: 有list_tools装饰器")
        else:
            print("  ERROR: 缺少list_tools装饰器")
            return False

        return True

    except Exception as e:
        print(f"  ERROR: 检查服务器实例失败: {e}")
        return False

def check_tool_functions():
    """检查工具函数"""
    print("\n3. 检查工具函数...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 查找装饰的函数
    tree = ast.parse(content)

    tool_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if hasattr(decorator.func, 'attr'):
                        if decorator.func.attr == 'call_tool':
                            tool_functions.append(node.name)

    print(f"  OK: 找到 {len(tool_functions)} 个工具函数")
    for func in tool_functions:
        print(f"    - {func}")

    if len(tool_functions) >= 1:
        return True
    else:
        print("  ERROR: 没有找到工具函数")
        return False

def check_list_tools():
    """检查list_tools函数"""
    print("\n4. 检查list_tools函数...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否有list_tools函数
    if "def list_tools" in content:
        print("  OK: 有list_tools函数")
    else:
        print("  ERROR: 缺少list_tools函数")
        return False

    # 检查是否返回ListToolsResult
    if "ListToolsResult(" in content:
        print("  OK: 返回ListToolsResult")
    else:
        print("  ERROR: 没有返回ListToolsResult")
        return False

    # 检查工具定义
    if "Tool(" in content:
        print("  OK: 使用Tool类定义工具")
    else:
        print("  ERROR: 没有使用Tool类")
        return False

    return True

def check_response_format():
    """检查响应格式"""
    print("\n5. 检查响应格式...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否使用CallToolResult
    if "CallToolResult(" in content:
        print("  OK: 使用CallToolResult")
    else:
        print("  ERROR: 没有使用CallToolResult")
        return False

    # 检查是否使用TextContent
    if "TextContent(" in content:
        print("  OK: 使用TextContent")
    else:
        print("  ERROR: 没有使用TextContent")
        return False

    # 检查是否有JSON序列化
    if "json.dumps" in content:
        print("  OK: 使用JSON序列化")
    else:
        print("  WARNING: 没有使用JSON序列化")

    return True

def check_communication():
    """检查通信"""
    print("\n6. 检查通信...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否使用stdio_server
    if "stdio_server" in content:
        print("  OK: 使用stdio_server")
    else:
        print("  ERROR: 没有使用stdio_server")
        return False

    # 检查是否有main函数
    if "def main()" in content:
        print("  OK: 有main函数")
    else:
        print("  ERROR: 没有main函数")
        return False

    # 检查是否使用server.run
    if "server.run(" in content:
        print("  OK: 使用server.run")
    else:
        print("  ERROR: 没有使用server.run")
        return False

    return True

def check_error_handling():
    """检查错误处理"""
    print("\n7. 检查错误处理...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否有错误处理
    if "try:" in content and "except" in content:
        print("  OK: 有错误处理")
    else:
        print("  WARNING: 缺少错误处理")

    # 检查是否有日志
    if "logging" in content:
        print("  OK: 有日志记录")
    else:
        print("  WARNING: 缺少日志记录")

    return True

def check_json_schema():
    """检查JSON Schema"""
    print("\n8. 检查JSON Schema...")

    with open("mcp_browser_tools/server.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否有inputSchema
    if "inputSchema" in content:
        print("  OK: 有inputSchema定义")
    else:
        print("  ERROR: 缺少inputSchema定义")
        return False

    # 检查是否有类型定义
    if '"type": "object"' in content:
        print("  OK: 有类型定义")
    else:
        print("  ERROR: 缺少类型定义")
        return False

    # 检查是否有参数描述
    if '"description":' in content:
        print("  OK: 有参数描述")
    else:
        print("  WARNING: 缺少参数描述")

    return True

def main():
    """主函数"""
    print("=" * 60)
    print("MCP规范符合性检查")
    print("=" * 60)

    checks = [
        ("导入检查", check_imports),
        ("服务器实例", check_server_instance),
        ("工具函数", check_tool_functions),
        ("list_tools函数", check_list_tools),
        ("响应格式", check_response_format),
        ("通信协议", check_communication),
        ("错误处理", check_error_handling),
        ("JSON Schema", check_json_schema),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"  ERROR: {check_name}检查异常: {e}")
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
        print("\n完全符合MCP规范！")
        print("项目可以作为MCP服务器正常运行。")
    elif passed >= total - 2:  # 允许最多2个警告
        print(f"\n基本符合MCP规范 ({passed}/{total})")
        print("项目可以作为MCP服务器运行。")
    else:
        print(f"\n不符合MCP规范 ({passed}/{total})")
        print("项目需要修复才能作为MCP服务器运行。")

    # 关键要求检查
    print("\n" + "=" * 60)
    print("MCP关键要求:")
    print("1. 使用Server类创建服务器实例 -", "OK" if results[1][1] else "ERROR")
    print("2. 有list_tools函数返回工具列表 -", "OK" if results[3][1] else "ERROR")
    print("3. 有call_tool装饰的工具函数 -", "OK" if results[2][1] else "ERROR")
    print("4. 使用stdio_server进行通信 -", "OK" if results[5][1] else "ERROR")
    print("5. 使用正确的响应类型 -", "OK" if results[4][1] else "ERROR")
    print("=" * 60)

    # 所有关键要求都必须通过
    critical_checks = [1, 2, 3, 4, 5]  # 索引对应上面的检查
    all_critical_passed = all(results[i][1] for i in critical_checks if i < len(results))

    return all_critical_passed

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