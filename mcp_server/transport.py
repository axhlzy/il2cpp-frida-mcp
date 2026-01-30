"""
MCP 传输层实现
"""
import sys
import asyncio
from .server import server


async def run_stdio():
    """以 stdio 模式运行"""
    from mcp.server.stdio import stdio_server
    
    print("[*] 启动 MCP 服务器 (stdio 模式)...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def run_sse(host: str, port: int):
    """以 SSE 模式运行"""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn
    
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
    
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
    
    app = Starlette(
        routes=[
            Route("/sse", handle_sse),
            Route("/messages", handle_messages, methods=["POST"]),
        ]
    )
    
    print(f"[*] 启动 MCP 服务器 (SSE 模式) @ http://{host}:{port}", file=sys.stderr)
    print(f"    SSE 端点: http://{host}:{port}/sse", file=sys.stderr)
    print(f"    消息端点: http://{host}:{port}/messages", file=sys.stderr)
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


async def run_streamable_http(host: str, port: int):
    """以 Streamable HTTP 模式运行"""
    from mcp.server.streamable_http import StreamableHTTPServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import Response
    import uvicorn
    import uuid
    
    # 存储活跃的 transport 实例
    transports: dict[str, StreamableHTTPServerTransport] = {}
    
    async def handle_mcp(request):
        # 获取或创建 session
        session_id = request.headers.get("mcp-session-id")
        
        if request.method == "GET":
            # SSE 连接请求
            if not session_id or session_id not in transports:
                return Response("Session not found", status_code=404)
            transport = transports[session_id]
            return await transport.handle_sse_request(request)
        
        elif request.method == "POST":
            # 如果没有 session，创建新的
            if not session_id:
                session_id = str(uuid.uuid4())
                transport = StreamableHTTPServerTransport(
                    mcp_session_id=session_id,
                    is_json_response_enabled=True
                )
                transports[session_id] = transport
                # 启动 server
                asyncio.create_task(_run_server_for_transport(transport))
            else:
                transport = transports.get(session_id)
                if not transport:
                    return Response("Session not found", status_code=404)
            
            return await transport.handle_post_request(request)
        
        return Response("Method not allowed", status_code=405)
    
    async def _run_server_for_transport(transport: StreamableHTTPServerTransport):
        async with transport.connect() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    app = Starlette(
        routes=[
            Route("/mcp", handle_mcp, methods=["GET", "POST"]),
        ]
    )
    
    print(f"[*] 启动 MCP 服务器 (Streamable HTTP 模式) @ http://{host}:{port}", file=sys.stderr)
    print(f"    MCP 端点: http://{host}:{port}/mcp", file=sys.stderr)
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()
