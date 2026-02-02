"""
MCP Tool Definitions
"""
from mcp.types import Tool


def get_tools() -> list[Tool]:
    """Return all available tool definitions"""
    return [
        # Frida Basic Tools
        Tool(
            name="frida_list_devices",
            description="List all available Frida devices (usually not needed unless user explicitly requests device list)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_connect",
            description="Connect to Frida device and target process. Default: device_type='usb' and mode='attach_front' to attach foreground app",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_type": {"type": "string", "enum": ["usb", "remote", "local"], "default": "usb"},
                    "remote_host": {"type": "string"},
                    "mode": {"type": "string", "enum": ["spawn", "attach_front", "attach_name", "attach_pid"], "default": "attach_front"},
                    "target": {"type": "string"}
                },
                "required": ["device_type", "mode"]
            }
        ),
        Tool(
            name="frida_disconnect",
            description="Disconnect from Frida",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_resume",
            description="Resume suspended process (use after spawn mode)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="frida_list_processes",
            description="List processes on device",
            inputSchema={
                "type": "object",
                "properties": {"filter": {"type": "string"}}
            }
        ),
        
        # IL2CPP Tools
        Tool(
            name="il2cpp_list_images",
            description="List all IL2CPP images",
            inputSchema={
                "type": "object",
                "properties": {"filter": {"type": "string"}}
            }
        ),
        Tool(
            name="il2cpp_list_classes",
            description="List all classes in specified image",
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
            description="List all methods of specified class",
            inputSchema={
                "type": "object",
                "properties": {"class_name": {"type": "string"}},
                "required": ["class_name"]
            }
        ),
        Tool(
            name="il2cpp_show_method",
            description="Show method details. Note: parameter must be Il2CppMethod pointer (first column handle from il2cpp_list_methods result)",
            inputSchema={
                "type": "object",
                "properties": {"il2cpp_method_ptr": {"type": "string", "description": "Il2CppMethod pointer address (first column handle from il2cpp_list_methods)"}},
                "required": ["il2cpp_method_ptr"]
            }
        ),
        Tool(
            name="il2cpp_find_classes",
            description="Find classes (supports fuzzy matching)",
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
            description="Find methods (supports fuzzy matching)",
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
            description="Disassemble method. method_ptr should use virtual_address (second column from list_methods). resolve_functions defaults to false; if true, resolves jump target function names but requires preloading all functions (takes longer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "il2cpp_method_ptr": {"type": "string", "description": "Method virtual_address (second column from list_methods)"},
                    "instruction_count": {"type": "integer", "description": "Number of instructions to disassemble, default 64"},
                    "resolve_functions": {"type": "boolean", "description": "Whether to resolve jump target function names (default false, enabling requires preloading all functions)"}
                },
                "required": ["il2cpp_method_ptr"]
            }
        ),
        Tool(
            name="il2cpp_find_export",
            description="Find exported functions",
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
            description="Find imported functions",
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
            description="Execute arbitrary JavaScript code (advanced feature, can directly manipulate Frida API and IL2CPP objects)",
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
            description="Find all instances of specified class in heap (for finding runtime objects)",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Class name to find"},
                    "max_count": {"type": "integer", "description": "Maximum number of results, default 100"}
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="il2cpp_gc_info",
            description="Get GC heap information (heap size, used size, etc.)",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Instance Parsing Tools (lfs/lfp/lfss etc.)
        Tool(
            name="il2cpp_list_fields",
            description="Parse all fields of instance (lfs). Returns all field info including name, type, offset, value",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "class_handle": {"type": "string", "description": "Optional class handle to specify which class fields to parse"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_list_fields_with_parents",
            description="Parse all fields of instance including parent classes (lfp). Returns field info for instance and all parent classes",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_fields_to_string",
            description="Get string representation of instance fields (lfss). Returns JSON format field name-value mapping",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "class_handle": {"type": "string", "description": "Optional class handle"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_get_field_type",
            description="Get field type information (lft). Returns detailed type info for specified field",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "field_name": {"type": "string", "description": "Field name"},
                    "class_handle": {"type": "string", "description": "Optional class handle"}
                },
                "required": ["instance_ptr", "field_name"]
            }
        ),
        Tool(
            name="il2cpp_get_field_value",
            description="Get field value (lfv). Returns value pointer for specified field",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "field_name": {"type": "string", "description": "Field name"},
                    "class_handle": {"type": "string", "description": "Optional class handle"}
                },
                "required": ["instance_ptr", "field_name"]
            }
        ),
        Tool(
            name="il2cpp_get_field_offset",
            description="Get field offset (lfo). Returns offset of specified field in instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "field_name": {"type": "string", "description": "Field name"},
                    "class_handle": {"type": "string", "description": "Optional class handle"}
                },
                "required": ["instance_ptr", "field_name"]
            }
        ),
        Tool(
            name="il2cpp_get_instance_type",
            description="Get instance type information. Returns detailed info about the class the instance belongs to",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_get_type_parents",
            description="Get instance parent class chain. Returns inheritance chain from current class to root class",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_list_instance_methods",
            description="List all methods of instance (lms). Returns all methods of the class the instance belongs to",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="il2cpp_read_at_offset",
            description="Read value at specified offset of instance. Can read memory value at any offset position",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "offset": {"type": "integer", "description": "Offset"},
                    "size": {"type": "integer", "description": "Read size (1, 2, 4, 8), default 8"}
                },
                "required": ["instance_ptr", "offset"]
            }
        ),
        Tool(
            name="il2cpp_set_field_value",
            description="Set instance field value. Modify specified field value of instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Instance pointer address"},
                    "field_name": {"type": "string", "description": "Field name"},
                    "value": {"type": "string", "description": "New value (pointer string)"},
                    "class_handle": {"type": "string", "description": "Optional class handle"}
                },
                "required": ["instance_ptr", "field_name", "value"]
            }
        ),
        
        # Unity Tools
        Tool(
            name="unity_get_transform",
            description="Get Transform from GameObject or Component",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "GameObject or Component pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="unity_get_gameobject",
            description="Get GameObject from Transform or Component",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ptr": {"type": "string", "description": "Transform or Component pointer address"}
                },
                "required": ["instance_ptr"]
            }
        ),
        Tool(
            name="unity_get_children",
            description="Get all children of Transform",
            inputSchema={
                "type": "object",
                "properties": {
                    "transform_ptr": {"type": "string", "description": "Transform pointer address"}
                },
                "required": ["transform_ptr"]
            }
        ),
        Tool(
            name="unity_get_parent",
            description="Get parent of Transform",
            inputSchema={
                "type": "object",
                "properties": {
                    "transform_ptr": {"type": "string", "description": "Transform pointer address"}
                },
                "required": ["transform_ptr"]
            }
        ),
        Tool(
            name="unity_get_hierarchy",
            description="Get hierarchy path of Transform (from current object to root)",
            inputSchema={
                "type": "object",
                "properties": {
                    "transform_ptr": {"type": "string", "description": "Transform pointer address"},
                    "max_depth": {"type": "integer", "description": "Maximum depth, default 10"}
                },
                "required": ["transform_ptr"]
            }
        ),
        Tool(
            name="unity_send_message",
            description="Call UnitySendMessage to send message to GameObject",
            inputSchema={
                "type": "object",
                "properties": {
                    "gameobject_name": {"type": "string", "description": "GameObject name"},
                    "method_name": {"type": "string", "description": "Method name"},
                    "message": {"type": "string", "description": "Message content"}
                },
                "required": ["gameobject_name", "method_name", "message"]
            }
        ),
        Tool(
            name="unity_find_gameobject",
            description="Find GameObject by path (using GameObject.Find)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "GameObject path"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="unity_get_scene_info",
            description="Get current scene information including all GameObjects hierarchy and attached scripts with their pointers",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_depth": {"type": "integer", "description": "Maximum hierarchy depth to traverse, default 10"},
                    "include_inactive": {"type": "boolean", "description": "Whether to include inactive GameObjects, default true"}
                }
            }
        ),
        
        # Memory Tools
        Tool(
            name="memory_alloc_cstring",
            description="Allocate C string (UTF-8)",
            inputSchema={
                "type": "object",
                "properties": {
                    "str": {"type": "string", "description": "String to allocate"}
                },
                "required": ["str"]
            }
        ),
        Tool(
            name="memory_alloc_il2cpp_string",
            description="Allocate IL2CPP string (System.String)",
            inputSchema={
                "type": "object",
                "properties": {
                    "str": {"type": "string", "description": "String to allocate"}
                },
                "required": ["str"]
            }
        ),
        Tool(
            name="memory_alloc",
            description="Allocate memory of specified size",
            inputSchema={
                "type": "object",
                "properties": {
                    "size": {"type": "integer", "description": "Memory size in bytes"}
                },
                "required": ["size"]
            }
        ),
        Tool(
            name="memory_alloc_vector",
            description="Allocate Vector (float array)",
            inputSchema={
                "type": "object",
                "properties": {
                    "values": {"type": "array", "items": {"type": "number"}, "description": "Float array"}
                },
                "required": ["values"]
            }
        ),
        Tool(
            name="memory_scan",
            description="Memory scan - unified interface. Uses Memory.scanSync and Process.enumerateRanges for memory scanning",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Search pattern, format like '13 37 ?? ff' or '/regex/'"},
                    "protection": {"type": "string", "description": "Memory protection attribute, e.g. 'r--', 'rw-', 'r-x', 'rwx', default 'r--'"},
                    "module_name": {"type": "string", "description": "Optional, specify module name to search"},
                    "coalesce": {"type": "boolean", "description": "Whether to coalesce adjacent memory regions, default false"},
                    "limit": {"type": "integer", "description": "Maximum number of results, default 100"}
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="memory_write",
            description="Write memory value",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Memory address"},
                    "value": {"description": "Value to write"},
                    "type": {"type": "string", "enum": ["int", "int32", "uint32", "int64", "uint64", "float", "double", "pointer", "string"], "description": "Value type, default int"}
                },
                "required": ["address", "value"]
            }
        ),
        Tool(
            name="memory_read",
            description="Read memory value",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Memory address"},
                    "type": {"type": "string", "enum": ["int", "int32", "uint32", "int64", "uint64", "float", "double", "pointer", "string", "bytes"], "description": "Value type, default pointer"},
                    "length": {"type": "integer", "description": "Length (for string and bytes types)"}
                },
                "required": ["address"]
            }
        ),
        
        # App Info Tools
        Tool(
            name="app_get_apk_info",
            description="Get APK basic information (package name, version, signature, etc.)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]
