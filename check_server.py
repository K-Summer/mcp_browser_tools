#!/usr/bin/env python3
"""
检查服务器状态的简单脚本
"""

import socket
import sys

def check_server(host='127.0.0.1', port=8000):
    """检查服务器是否在运行"""
    print(f"检查服务器 {host}:{port}...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((host, port))
            if result == 0:
                print(f"[SUCCESS] 服务器正在运行在 {host}:{port}")
                return True
            else:
                print(f"[ERROR] 服务器未运行在 {host}:{port} (错误码: {result})")
                return False
    except socket.timeout:
        print(f"[ERROR] 连接超时")
        return False
    except Exception as e:
        print(f"[ERROR] 检查时出错: {e}")
        return False

def main():
    print("=" * 50)
    print("MCP Browser Tools 服务器状态检查")
    print("=" * 50)

    # 检查常用端口
    ports = [8000, 8080, 3000, 5000]

    for port in ports:
        if check_server('127.0.0.1', port):
            print(f"\n建议: 使用以下命令连接:")
            print(f"  python -m mcp_browser_tools --transport sse --host 127.0.0.1 --port {port}")
            return True

    print("\n" + "=" * 50)
    print("未找到运行中的服务器")
    print("\n要启动服务器，请运行以下命令之一:")
    print("  python -m mcp_browser_tools --transport sse --host 127.0.0.1 --port 8000")
    print("  python -m mcp_browser_tools --transport sse --host 0.0.0.0 --port 8080")
    print("\n要使用 stdio 模式（无需网络连接）:")
    print("  python -m mcp_browser_tools --transport stdio")
    print("=" * 50)

    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)