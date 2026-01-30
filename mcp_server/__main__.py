#!/usr/bin/env python3
"""
IL2CPP Frida MCP Server - 命令行入口
"""
import asyncio
from .cli import parse_args, select_transport_interactive
from .transport import run_stdio, run_sse, run_streamable_http


def main():
    """主入口函数"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n[*] 服务器已停止")


async def async_main():
    """异步主函数"""
    args = parse_args()
    
    if not (args.stdio or args.sse or args.http):
        transport, host, port = select_transport_interactive()
    elif args.stdio:
        transport = "stdio"
        host, port = args.host, args.port
    elif args.sse:
        transport = "sse"
        host, port = args.host, args.port
    else:
        transport = "http"
        host, port = args.host, args.port
    
    print()
    
    if transport == "stdio":
        await run_stdio()
    elif transport == "sse":
        await run_sse(host, port)
    else:
        await run_streamable_http(host, port)


if __name__ == "__main__":
    main()
