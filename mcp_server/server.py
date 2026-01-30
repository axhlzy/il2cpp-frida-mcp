"""
MCP Server 核心
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from .tools import get_tools
from .handlers import (
    handle_list_devices,
    handle_connect,
    handle_disconnect,
    handle_resume,
    handle_list_processes,
    handle_list_images,
    handle_list_classes,
    handle_list_methods,
    handle_show_method,
    handle_find_classes,
    handle_find_methods,
    handle_show_asm,
    handle_find_export,
    handle_find_import,
    handle_exec_js,
    handle_gc_choose,
    handle_gc_info,
)


# 创建 MCP Server 实例
server = Server("il2cpp-frida-mcp")


# 无参数的工具列表
NO_ARGS_TOOLS = ["frida_list_devices", "frida_disconnect", "frida_resume", "il2cpp_gc_info"]


# 工具处理器映射
HANDLERS = {
    "frida_list_devices": handle_list_devices,
    "frida_connect": handle_connect,
    "frida_disconnect": handle_disconnect,
    "frida_resume": handle_resume,
    "frida_list_processes": handle_list_processes,
    "il2cpp_list_images": handle_list_images,
    "il2cpp_list_classes": handle_list_classes,
    "il2cpp_list_methods": handle_list_methods,
    "il2cpp_show_method": handle_show_method,
    "il2cpp_find_classes": handle_find_classes,
    "il2cpp_find_methods": handle_find_methods,
    "il2cpp_show_asm": handle_show_asm,
    "il2cpp_find_export": handle_find_export,
    "il2cpp_find_import": handle_find_import,
    "il2cpp_exec_js": handle_exec_js,
    "il2cpp_gc_choose": handle_gc_choose,
    "il2cpp_gc_info": handle_gc_info,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return get_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    handler = HANDLERS.get(name)
    if handler:
        if name in NO_ARGS_TOOLS:
            return await handler()
        else:
            return await handler(arguments)
    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]
