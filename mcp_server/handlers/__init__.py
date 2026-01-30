"""
MCP 工具处理器
"""
from .frida_handlers import (
    handle_list_devices,
    handle_connect,
    handle_disconnect,
    handle_resume,
    handle_list_processes,
)
from .il2cpp_handlers import (
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

__all__ = [
    # Frida handlers
    "handle_list_devices",
    "handle_connect",
    "handle_disconnect",
    "handle_resume",
    "handle_list_processes",
    # IL2CPP handlers
    "handle_list_images",
    "handle_list_classes",
    "handle_list_methods",
    "handle_show_method",
    "handle_find_classes",
    "handle_find_methods",
    "handle_show_asm",
    "handle_find_export",
    "handle_find_import",
    "handle_exec_js",
    "handle_gc_choose",
    "handle_gc_info",
]
