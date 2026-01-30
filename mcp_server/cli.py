"""
命令行接口
"""
import argparse


def select_transport_interactive() -> tuple[str, str, int]:
    """交互式选择传输方式"""
    print("\n" + "=" * 50)
    print("  IL2CPP Frida MCP Server")
    print("=" * 50)
    print("\n请选择 MCP 传输方式:\n")
    print("  [1] stdio  - 标准输入输出 (用于 Claude Desktop 等)")
    print("  [2] sse    - Server-Sent Events (HTTP 长连接)")
    print("  [3] http   - Streamable HTTP (新版 MCP 推荐)")
    print()
    
    while True:
        choice = input("请输入选项 (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("[!] 无效选项,请重新输入")
    
    transport_map = {"1": "stdio", "2": "sse", "3": "http"}
    transport = transport_map[choice]
    
    host = "127.0.0.1"
    port = 8000
    
    if transport in ["sse", "http"]:
        print(f"\n默认地址: {host}:{port}")
        custom = input("是否自定义地址? (y/N): ").strip().lower()
        if custom == "y":
            host_input = input(f"Host [{host}]: ").strip()
            if host_input:
                host = host_input
            port_input = input(f"Port [{port}]: ").strip()
            if port_input:
                port = int(port_input)
    
    return transport, host, port


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="IL2CPP Frida MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python mcp_server.py                    # 交互式选择
  python mcp_server.py --stdio            # stdio 模式
  python mcp_server.py --sse              # SSE 模式 (默认 127.0.0.1:8000)
  python mcp_server.py --http             # HTTP 模式 (默认 127.0.0.1:8000)
  python mcp_server.py --sse --host 0.0.0.0 --port 9000
        """
    )
    
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument("--stdio", action="store_true", help="使用 stdio 传输")
    transport_group.add_argument("--sse", action="store_true", help="使用 SSE 传输")
    transport_group.add_argument("--http", action="store_true", help="使用 Streamable HTTP 传输")
    
    parser.add_argument("--host", default="127.0.0.1", help="服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    
    return parser.parse_args()
