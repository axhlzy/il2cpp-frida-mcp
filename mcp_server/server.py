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
    # 实例解析处理器
    handle_list_fields,
    handle_list_fields_with_parents,
    handle_fields_to_string,
    handle_get_field_type,
    handle_get_field_value,
    handle_get_field_offset,
    handle_get_instance_type,
    handle_get_type_parents,
    handle_list_instance_methods,
    handle_read_at_offset,
    handle_set_field_value,
    # Unity 处理器
    handle_unity_get_transform,
    handle_unity_get_gameobject,
    handle_unity_get_children,
    handle_unity_get_parent,
    handle_unity_get_hierarchy,
    handle_unity_send_message,
    handle_unity_find_gameobject,
    handle_unity_get_scene_info,
    # 内存处理器
    handle_memory_alloc_cstring,
    handle_memory_alloc_il2cpp_string,
    handle_memory_alloc,
    handle_memory_alloc_vector,
    handle_memory_scan,
    handle_memory_write,
    handle_memory_read,
    # 应用信息处理器
    handle_app_get_apk_info,
)


# 创建 MCP Server 实例
server = Server("il2cpp-frida-mcp")


# 无参数的工具列表
NO_ARGS_TOOLS = [
    "frida_list_devices", "frida_disconnect", "frida_resume", "il2cpp_gc_info",
    "app_get_apk_info"
]


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
    # 实例解析处理器
    "il2cpp_list_fields": handle_list_fields,
    "il2cpp_list_fields_with_parents": handle_list_fields_with_parents,
    "il2cpp_fields_to_string": handle_fields_to_string,
    "il2cpp_get_field_type": handle_get_field_type,
    "il2cpp_get_field_value": handle_get_field_value,
    "il2cpp_get_field_offset": handle_get_field_offset,
    "il2cpp_get_instance_type": handle_get_instance_type,
    "il2cpp_get_type_parents": handle_get_type_parents,
    "il2cpp_list_instance_methods": handle_list_instance_methods,
    "il2cpp_read_at_offset": handle_read_at_offset,
    "il2cpp_set_field_value": handle_set_field_value,
    # Unity 处理器
    "unity_get_transform": handle_unity_get_transform,
    "unity_get_gameobject": handle_unity_get_gameobject,
    "unity_get_children": handle_unity_get_children,
    "unity_get_parent": handle_unity_get_parent,
    "unity_get_hierarchy": handle_unity_get_hierarchy,
    "unity_send_message": handle_unity_send_message,
    "unity_find_gameobject": handle_unity_find_gameobject,
    "unity_get_scene_info": handle_unity_get_scene_info,
    # 内存处理器
    "memory_alloc_cstring": handle_memory_alloc_cstring,
    "memory_alloc_il2cpp_string": handle_memory_alloc_il2cpp_string,
    "memory_alloc": handle_memory_alloc,
    "memory_alloc_vector": handle_memory_alloc_vector,
    "memory_scan": handle_memory_scan,
    "memory_write": handle_memory_write,
    "memory_read": handle_memory_read,
    # 应用信息处理器
    "app_get_apk_info": handle_app_get_apk_info,
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
