"""
MCP 工具定义
"""
from mcp.types import Tool


def get_tools() -> list[Tool]:
    """返回所有可用的工具定义"""
    return [
        # Frida 基础工具
        Tool(
            name="frida_list_devices",
            description="列出所有可用的 Frida 设备",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_connect",
            description="连接到 Frida 设备和目标进程",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_type": {"type": "string", "enum": ["usb", "remote", "local"]},
                    "remote_host": {"type": "string"},
                    "mode": {"type": "string", "enum": ["spawn", "attach_front", "attach_name", "attach_pid"]},
                    "target": {"type": "string"}
                },
                "required": ["device_type", "mode"]
            }
        ),
        Tool(
            name="frida_disconnect",
            description="断开 Frida 连接",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_resume",
            description="恢复被暂停的进程 (spawn 模式后使用)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_list_processes",
            description="列出设备上的进程",
            inputSchema={
                "type": "object",
                "properties": {"filter": {"type": "string"}}
            }
        ),
        
        # IL2CPP 工具
        Tool(
            name="il2cpp_list_images",
            description="列出所有 IL2CPP 镜像",
            inputSchema={
                "type": "object",
                "properties": {"filter": {"type": "string"}}
            }
        ),
        Tool(
            name="il2cpp_list_classes",
            description="列出指定镜像的所有类",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_name": {"type": "string"},
                    "filter_namespace": {"type": "string"},
                    "filter_classname": {"type": "string"}
                },
                "required": ["image_name"]
            }
        ),
        Tool(
            name="il2cpp_list_methods",
            description="列出指定类的所有方法",
            inputSchema={
                "type": "object",
                "properties": {"class_name": {"type": "string"}},
                "required": ["class_name"]
            }
        ),
        Tool(
            name="il2cpp_show_method",
            description="显示方法的详细信息。注意:method_ptr 必须是 Il2CppMethod 指针(即 il2cpp_list_methods 返回结果的第一列 handle 地址),而不是 virtual_address 或 relative_virtual_address",
            inputSchema={
                "type": "object",
                "properties": {"method_ptr": {"type": "string", "description": "Il2CppMethod 指针地址(list_methods 返回的第一列 handle)"}},
                "required": ["method_ptr"]
            }
        ),
        Tool(
            name="il2cpp_find_classes",
            description="查找类(支持模糊匹配)",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string"},
                    "complete_match": {"type": "boolean"}
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="il2cpp_find_methods",
            description="查找方法(支持模糊匹配)",
            inputSchema={
                "type": "object",
                "properties": {
                    "method_name": {"type": "string"},
                    "find_all": {"type": "boolean"},
                    "accurate": {"type": "boolean"}
                },
                "required": ["method_name"]
            }
        ),
        Tool(
            name="il2cpp_show_asm",
            description="反汇编方法。method_ptr 应使用 virtual_address(list_methods 返回的第二列地址)。resolve_functions 默认为 false,如果设为 true 会解析跳转目标函数名,但需要预加载所有函数,耗时会比较长",
            inputSchema={
                "type": "object",
                "properties": {
                    "method_ptr": {"type": "string", "description": "方法的 virtual_address(list_methods 返回的第二列地址)"},
                    "instruction_count": {"type": "integer", "description": "反汇编指令数量,默认 64"},
                    "resolve_functions": {"type": "boolean", "description": "是否解析跳转目标函数名(默认 false,开启需要预加载所有函数,耗时较长)"}
                },
                "required": ["method_ptr"]
            }
        ),
        Tool(
            name="il2cpp_find_export",
            description="查找导出函数",
            inputSchema={
                "type": "object",
                "properties": {
                    "export_name": {"type": "string"},
                    "module_name": {"type": "string"}
                },
                "required": ["export_name"]
            }
        ),
        Tool(
            name="il2cpp_find_import",
            description="查找导入函数",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {"type": "string"},
                    "import_name": {"type": "string"}
                },
                "required": ["module_name"]
            }
        ),
        Tool(
            name="il2cpp_exec_js",
            description="执行任意 JavaScript 代码(高级功能,可以直接操作 Frida API 和 IL2CPP 对象)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string"}
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="il2cpp_gc_choose",
            description="在堆中查找指定类的所有实例（用于查找运行时对象）",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "要查找的类名"},
                    "max_count": {"type": "integer", "description": "最大返回数量，默认100"}
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="il2cpp_gc_info",
            description="获取 GC 堆信息（堆大小、已用大小等）",
            inputSchema={"type": "object", "properties": {}}
        )
    ]
