"""
IL2CPP Operation Handlers
"""
from mcp.types import TextContent
from ..state import state


def _check_connection() -> TextContent | None:
    """Check connection status"""
    if not state.connected or not state.script:
        return TextContent(type="text", text="[✗] Please connect to target process first")
    return None


async def handle_list_images(args: dict) -> list[TextContent]:
    """List IL2CPP images"""
    try:
        if err := _check_connection():
            return [err]
        
        filter_str = args.get("filter", "")
        images = state.script.exports_sync.list_images(filter_str, True)
        
        result = "=" * 85 + "\n"
        result += "List Images { assembly -> image -> classCount -> imageName }\n"
        result += "=" * 85 + "\n"
        
        for img in images:
            result += f"[*] {img['assembly_handle']} -> {img['image_handle']}\t{img['class_count']}\t{img['assembly_name']}\n"
        
        result += "-" * 28 + "\n"
        result += f"  List {len(images)} Images\n"
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to list images: {e}")]


async def handle_list_classes(args: dict) -> list[TextContent]:
    """List classes"""
    try:
        if err := _check_connection():
            return [err]
        
        image_name = args.get("image_name", "")
        filter_namespace = args.get("filter_namespace", "")
        filter_classname = args.get("filter_classname", "")
        
        if not image_name:
            return [TextContent(type="text", text="[✗] Please specify image name")]
        
        classes = state.script.exports_sync.list_classes(image_name, filter_namespace, filter_classname)
        
        result = "=" * 85 + "\n"
        result += f"Found {len(classes)} Classes in image: {image_name}\n"
        result += "=" * 85 + "\n"
        
        for cls in classes:
            ns_str = f" | N:{cls['namespace']}" if cls['namespace'] != "[No Namespace]" else ""
            result += f"[*] {cls['handle']}\t{cls['name']} | M:{cls['method_count']} | F:{cls['field_count']}{ns_str}\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to list classes: {e}")]


async def handle_list_methods(args: dict) -> list[TextContent]:
    """List class methods"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        if not class_name:
            return [TextContent(type="text", text="[✗] Please specify class name")]
        
        methods = state.script.exports_sync.list_methods(class_name)
        
        if not methods:
            return [TextContent(type="text", text=f"[✗] Class not found: {class_name}")]
        
        result = "=" * 85 + "\n"
        result += f"Found {len(methods)} Methods in class: {methods[0]['class_name']}\n"
        result += "First column: Il2CppMethod pointer | Second column: Memory address | Third column: Relative address (minus base address)\n"
        result += "=" * 85 + "\n"
        
        for m in methods:
            result += f"[*] {m['handle']} -> {m['virtual_address']} -> {m['relative_virtual_address']}\t| {m['modifier']} {m['return_type']} {m['name']}()\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to list methods: {e}")]


async def handle_show_method(args: dict) -> list[TextContent]:
    """Show method details"""
    try:
        if err := _check_connection():
            return [err]
        
        il2cpp_method_ptr = args.get("il2cpp_method_ptr", "")
        if not il2cpp_method_ptr:
            return [TextContent(type="text", text="[✗] Please specify method pointer")]
        
        info = state.script.exports_sync.show_method(il2cpp_method_ptr)
        
        if not info:
            return [TextContent(type="text", text=f"[✗] Method not found: {il2cpp_method_ptr}")]
        
        result = f"\n[-]{info['assembly']['name']} @ {info['assembly']['handle']}\n"
        result += f"  [-]{info['image']['name']} @ {info['image']['handle']} | C:{info['image']['class_count']}\n"
        
        ns = info['class']['namespace']
        ns_str = f" | N:{ns}" if ns else ""
        result += f"    [-]{info['class']['name']} @ {info['class']['handle']} | M:{info['class']['method_count']} | F:{info['class']['field_count']}{ns_str}\n"
        
        rva = info['relative_virtual_address']
        rva_str = f" & RP: {rva}" if rva != "0x0" else ""
        result += f"      [-]{info['modifier']} {info['return_type']['name']} {info['name']}() @ MI: {info['handle']} & MP: {info['virtual_address']}{rva_str}\n"
        
        for param in info['parameters']:
            result += f"        [-]{param['name']:20} | type: {param['type_handle']} | @ class:{param['class_handle']} | {param['type']}\n"
        
        if info['return_type']['name'] != "System.Void":
            result += f"        [-]{'_RET_':20} | type: {info['return_type']['handle']} | @ class:{info['return_type']['class_handle']} | {info['return_type']['name']}\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get method info: {e}")]


async def handle_find_classes(args: dict) -> list[TextContent]:
    """Find classes"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        complete_match = args.get("complete_match", False)
        
        if not class_name:
            return [TextContent(type="text", text="[✗] Please specify class name")]
        
        classes = state.script.exports_sync.find_classes(class_name, complete_match)
        
        result = "=" * 85 + "\n"
        result += f"Found {len(classes)} Classes matching '{class_name}'\n"
        result += "=" * 85 + "\n"
        
        for cls in classes:
            ns_str = f" | NS:{cls['namespace']}" if cls['namespace'] != "[No Namespace]" else ""
            result += f"[*] {cls['name']}\n"
            result += f"    Handle: {cls['handle']}\n"
            result += f"    Assembly: {cls['assembly_name']}\n"
            result += f"    Image: {cls['image_name']}\n"
            result += f"    Methods: {cls['method_count']} | Fields: {cls['field_count']}{ns_str}\n"
            if cls.get('is_enum'):
                result += f"    [Enum]\n"
            if cls.get('is_abstract'):
                result += f"    [Abstract]\n"
            result += "\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find classes: {e}")]


async def handle_find_methods(args: dict) -> list[TextContent]:
    """Find methods"""
    try:
        if err := _check_connection():
            return [err]
        
        method_name = args.get("method_name", "")
        find_all = args.get("find_all", True)
        accurate = args.get("accurate", False)
        
        if not method_name:
            return [TextContent(type="text", text="[✗] Please specify method name")]
        
        methods = state.script.exports_sync.find_methods(method_name, find_all, accurate)
        
        result = "=" * 100 + "\n"
        result += f"Found {len(methods)} Methods matching '{method_name}'\n"
        result += "=" * 100 + "\n"
        
        for m in methods[:100]:
            ns_str = f"{m['namespace']}." if m.get('namespace') and m['namespace'] != "[No Namespace]" else ""
            method_sig = f"{m['modifier']} {m['return_type']} {ns_str}{m['class_name']}.{m['name']}()"
            result += f"[*] {m['handle']} -> {m['virtual_address']} -> {m['relative_virtual_address']}\t| {method_sig}\n"
        
        if len(methods) > 100:
            result += f"\n  ... {len(methods) - 100} more methods\n"
        
        result += "=" * 100
        result += f"\n\nTip: Use the second column address (virtual_address) when calling functions"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find methods: {e}")]


async def handle_show_asm(args: dict) -> list[TextContent]:
    """Show disassembly"""
    try:
        if err := _check_connection():
            return [err]
        
        il2cpp_method_ptr = args.get("il2cpp_method_ptr", "")
        instruction_count = args.get("instruction_count", 64)
        resolve_functions = args.get("resolve_functions", False)
        
        if not il2cpp_method_ptr:
            return [TextContent(type="text", text="[✗] Please specify method pointer")]
        
        if resolve_functions:
            result = "[!] Note: Function resolution enabled, requires preloading all functions, this may take a while...\n\n"
        else:
            result = ""
        
        asm_result = state.script.exports_sync.show_asm(il2cpp_method_ptr, instruction_count, resolve_functions)
        instructions = asm_result.get('instructions', [])
        
        result += "=" * 85 + "\n"
        result += f"Disassembly of {il2cpp_method_ptr} ({len(instructions)} instructions)\n"
        if resolve_functions and asm_result.get('methods_preloaded'):
            result += "[*] Function resolution enabled, jump targets will show function names\n"
        result += "=" * 85 + "\n"
        
        for ins in instructions:
            result += f"{ins['address']}: {ins['toString']}\n"
            if 'target_method' in ins:
                result += f"  -> {ins['target_method']['class_name']}.{ins['target_method']['name']}()\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to disassemble: {e}")]


async def handle_find_export(args: dict) -> list[TextContent]:
    """Find exported functions"""
    try:
        if err := _check_connection():
            return [err]
        
        export_name = args.get("export_name", "")
        module_name = args.get("module_name")
        
        if not export_name:
            return [TextContent(type="text", text="[✗] Please specify export function name")]
        
        exports = state.script.exports_sync.find_export(export_name, module_name)
        
        result = "=" * 85 + "\n"
        result += f"Found {len(exports)} Exports matching '{export_name}'\n"
        result += "=" * 85 + "\n"
        
        for exp in exports[:50]:
            result += f"[*] {exp['name']}\n"
            result += f"    Address: {exp['address']} (RVA: {exp['relative_address']})\n"
            result += f"    Module: {exp['module_name']} (Base: {exp['module_base']})\n"
            result += f"    Type: {exp['type']}\n"
        
        if len(exports) > 50:
            result += f"  ... {len(exports) - 50} more exports\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find exports: {e}")]


async def handle_find_import(args: dict) -> list[TextContent]:
    """Find imported functions"""
    try:
        if err := _check_connection():
            return [err]
        
        module_name = args.get("module_name", "")
        import_name = args.get("import_name")
        
        if not module_name:
            return [TextContent(type="text", text="[✗] Please specify module name")]
        
        imports = state.script.exports_sync.find_import(module_name, import_name)
        
        result = "=" * 85 + "\n"
        result += f"Found {len(imports)} Imports in module '{module_name}'\n"
        result += "=" * 85 + "\n"
        
        for imp in imports[:50]:
            result += f"[*] {imp['name']}\n"
            result += f"    Address: {imp['address']}\n"
            result += f"    Module: {imp['module']}\n"
            result += f"    Type: {imp['type']}\n"
        
        if len(imports) > 50:
            result += f"  ... {len(imports) - 50} more imports\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find imports: {e}")]


async def handle_exec_js(args: dict) -> list[TextContent]:
    """Execute JavaScript code"""
    try:
        if err := _check_connection():
            return [err]
        
        code = args.get("code", "")
        
        if not code:
            return [TextContent(type="text", text="[✗] Please provide code to execute")]
        
        result_data = state.script.exports_sync.exec_js(code)
        
        if result_data.get('success'):
            result = f"[✓] Code executed successfully\n"
            result += f"Result Type: {result_data.get('type', 'N/A')}\n"
            result += f"Result: {result_data.get('result', 'N/A')}\n"
        else:
            result = f"[✗] Code execution failed\n"
            result += f"Error: {result_data.get('error', 'Unknown error')}\n"
            if result_data.get('stack'):
                result += f"Stack:\n{result_data.get('stack')}\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to execute code: {e}")]


async def handle_gc_choose(args: dict) -> list[TextContent]:
    """Find instances of specified class in heap"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        max_count = args.get("max_count", 100)
        
        if not class_name:
            return [TextContent(type="text", text="[✗] Please specify class name")]
        
        instances = state.script.exports_sync.gc_choose(class_name, max_count)
        
        if instances and len(instances) > 0 and 'error' in instances[0]:
            return [TextContent(type="text", text=f"[✗] {instances[0]['error']}")]
        
        result = "=" * 85 + "\n"
        result += f"Found {len(instances)} instances of '{class_name}'\n"
        result += "=" * 85 + "\n"
        
        for i, inst in enumerate(instances):
            result += f"\n[{i}] {inst.get('class_name', 'Unknown')}\n"
            result += f"    Handle: {inst.get('handle', 'N/A')}\n"
            if 'fields' in inst:
                result += f"    Fields:\n"
                for fname, fvalue in inst['fields'].items():
                    result += f"      {fname}: {fvalue}\n"
        
        result += "\n" + "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find instances: {e}")]


async def handle_gc_info() -> list[TextContent]:
    """Get GC heap information"""
    try:
        if err := _check_connection():
            return [err]
        
        info = state.script.exports_sync.gc_info()
        
        # 安全地获取数值，处理可能的类型问题
        def safe_size(val, default=0):
            if val is None:
                return default
            try:
                if isinstance(val, (int, float)):
                    return float(val)
                return float(str(val).replace(',', ''))
            except:
                return default
        
        heap_size = safe_size(info.get('heap_size', 0))
        used_heap_size = safe_size(info.get('used_heap_size', 0))
        
        result = "=" * 50 + "\n"
        result += "GC Heap Information\n"
        result += "=" * 50 + "\n"
        result += f"Heap Size: {heap_size / 1024 / 1024:.2f} MB\n"
        result += f"Used Heap Size: {used_heap_size / 1024 / 1024:.2f} MB\n"
        result += f"GC Enabled: {info.get('is_enabled', False)}\n"
        result += f"Incremental GC: {info.get('is_incremental', False)}\n"
        result += f"Max Time Slice: {info.get('max_time_slice', 0)} ms\n"
        
        if 'error' in info:
            result += f"\nWarning: {info.get('error')}\n"
        
        result += "=" * 50
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get GC info: {e}")]


# ========== Instance parsing handlers (lfs/lfp/lfss etc) ==========

async def handle_list_fields(args: dict) -> list[TextContent]:
    """Parse all fields of instance (lfs)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        fields_result = state.script.exports_sync.list_fields(instance_ptr, class_handle)
        
        result = "=" * 100 + "\n"
        result += f"Instance Fields: {fields_result.get('class_name', 'Unknown')} ({fields_result.get('class_handle', 'N/A')})\n"
        result += f"Instance Handle: {fields_result.get('instance_handle', 'N/A')}\n"
        result += f"Namespace: {fields_result.get('namespace', '[No Namespace]')}\n"
        result += f"Field Count: {fields_result.get('field_count', 0)}\n"
        result += "=" * 100 + "\n"
        
        for field in fields_result.get('fields', []):
            idx = f"[{field.get('index', 0)}]".ljust(6)
            offset = f"0x{field.get('offset', 0):04x}"
            modifier = field.get('modifier', '').ljust(20)
            type_name = field.get('type_name', 'Unknown')
            name = field.get('name', 'Unknown')
            
            result += f"{idx} {offset} {modifier} {type_name}\t{name}\n"
            
            if 'value' in field:
                value_handle = field.get('value_handle', 'N/A')
                value = field.get('value', 'N/A')
                result += f"       ---> {value_handle} ---> {value}\n"
            result += "\n"
        
        result += "=" * 100
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to parse fields: {e}")]


async def handle_list_fields_with_parents(args: dict) -> list[TextContent]:
    """Parse all fields of instance including parents (lfp)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        parent_result = state.script.exports_sync.list_fields_with_parents(instance_ptr)
        
        result = "=" * 100 + "\n"
        result += f"Instance Fields with Parents\n"
        result += f"Instance Handle: {parent_result.get('instance_handle', 'N/A')}\n"
        result += "=" * 100 + "\n"
        
        # 显示继承链
        class_chain = parent_result.get('class_chain', [])
        chain_str = " <--- ".join([c.get('class_name', 'Unknown') for c in class_chain])
        result += f"Inheritance: {chain_str}\n"
        result += "-" * 100 + "\n"
        
        for cls_info in class_chain:
            result += f"\n[Class] {cls_info.get('class_name', 'Unknown')} ({cls_info.get('class_handle', 'N/A')})\n"
            result += f"Namespace: {cls_info.get('namespace', '[No Namespace]')}\n"
            result += "-" * 50 + "\n"
            
            for field in cls_info.get('fields', []):
                idx = f"[{field.get('index', 0)}]".ljust(6)
                offset = f"0x{field.get('offset', 0):04x}"
                modifier = field.get('modifier', '').ljust(20)
                type_name = field.get('type_name', 'Unknown')
                name = field.get('name', 'Unknown')
                
                result += f"{idx} {offset} {modifier} {type_name}\t{name}\n"
                
                if 'value' in field:
                    value_handle = field.get('value_handle', 'N/A')
                    value = field.get('value', 'N/A')
                    result += f"       ---> {value_handle} ---> {value}\n"
        
        result += "\n" + "=" * 100
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to parse fields: {e}")]


async def handle_fields_to_string(args: dict) -> list[TextContent]:
    """Get string representation of instance fields (lfss)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        fields_str = state.script.exports_sync.fields_to_string(instance_ptr, class_handle)
        
        result = f"Instance: {instance_ptr}\n"
        result += f"Fields: {fields_str}"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get field string: {e}")]


async def handle_get_field_type(args: dict) -> list[TextContent]:
    """Get field type information (lft)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        field_name = args.get("field_name", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr or not field_name:
            return [TextContent(type="text", text="[✗] Please specify instance pointer and field name")]
        
        field_info = state.script.exports_sync.get_field_type(instance_ptr, field_name, class_handle)
        
        if 'error' in field_info:
            return [TextContent(type="text", text=f"[✗] {field_info['error']}")]
        
        result = "=" * 60 + "\n"
        result += f"Field Type Information: {field_name}\n"
        result += "=" * 60 + "\n"
        result += f"Name: {field_info.get('name', 'N/A')}\n"
        result += f"Offset: 0x{field_info.get('offset', 0):04x}\n"
        result += f"Type Name: {field_info.get('type_name', 'N/A')}\n"
        result += f"Type Handle: {field_info.get('type_handle', 'N/A')}\n"
        result += f"Class Name: {field_info.get('class_name', 'N/A')}\n"
        result += f"Class Handle: {field_info.get('class_handle', 'N/A')}\n"
        result += f"Is Static: {field_info.get('is_static', False)}\n"
        result += f"Is Literal: {field_info.get('is_literal', False)}\n"
        result += f"Is Value Type: {field_info.get('is_value_type', False)}\n"
        result += f"Is Enum: {field_info.get('is_enum', False)}\n"
        result += "=" * 60
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get field type: {e}")]


async def handle_get_field_value(args: dict) -> list[TextContent]:
    """Get field value (lfv)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        field_name = args.get("field_name", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr or not field_name:
            return [TextContent(type="text", text="[✗] Please specify instance pointer and field name")]
        
        value_info = state.script.exports_sync.get_field_value(instance_ptr, field_name, class_handle)
        
        result = f"Field: {value_info.get('field_name', 'N/A')}\n"
        result += f"Value Handle: {value_info.get('value_handle', 'N/A')}\n"
        result += f"Is Null: {value_info.get('is_null', True)}"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get field value: {e}")]


async def handle_get_field_offset(args: dict) -> list[TextContent]:
    """Get field offset (lfo)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        field_name = args.get("field_name", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr or not field_name:
            return [TextContent(type="text", text="[✗] Please specify instance pointer and field name")]
        
        offset_info = state.script.exports_sync.get_field_offset(instance_ptr, field_name, class_handle)
        
        result = f"Field: {offset_info.get('field_name', 'N/A')}\n"
        result += f"Offset: {offset_info.get('offset', -1)}\n"
        result += f"Offset (Hex): {offset_info.get('offset_hex', 'not found')}"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get field offset: {e}")]


async def handle_get_instance_type(args: dict) -> list[TextContent]:
    """Get instance type information"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        type_info = state.script.exports_sync.get_instance_type(instance_ptr)
        
        if 'error' in type_info:
            return [TextContent(type="text", text=f"[✗] {type_info['error']}")]
        
        result = "=" * 60 + "\n"
        result += f"Instance Type Information\n"
        result += "=" * 60 + "\n"
        result += f"Instance Handle: {type_info.get('instance_handle', 'N/A')}\n"
        result += f"Class Name: {type_info.get('class_name', 'N/A')}\n"
        result += f"Class Handle: {type_info.get('class_handle', 'N/A')}\n"
        result += f"Namespace: {type_info.get('namespace', '[No Namespace]')}\n"
        result += f"Assembly: {type_info.get('assembly_name', 'N/A')}\n"
        result += f"Image: {type_info.get('image_name', 'N/A')}\n"
        result += f"Is Value Type: {type_info.get('is_value_type', False)}\n"
        result += f"Is Enum: {type_info.get('is_enum', False)}\n"
        result += f"Is Abstract: {type_info.get('is_abstract', False)}\n"
        result += f"Field Count: {type_info.get('field_count', 0)}\n"
        result += f"Method Count: {type_info.get('method_count', 0)}\n"
        result += "=" * 60
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get instance type: {e}")]


async def handle_get_type_parents(args: dict) -> list[TextContent]:
    """Get instance parent class chain"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        parents_info = state.script.exports_sync.get_type_parents(instance_ptr)
        
        if 'error' in parents_info:
            return [TextContent(type="text", text=f"[✗] {parents_info['error']}")]
        
        result = "=" * 80 + "\n"
        result += f"Type Parent Chain\n"
        result += f"Instance Handle: {parents_info.get('instance_handle', 'N/A')}\n"
        result += "=" * 80 + "\n"
        
        parent_chain = parents_info.get('parent_chain', [])
        chain_str = " <--- ".join([p.get('class_name', 'Unknown') for p in parent_chain])
        result += f"\n{chain_str}\n\n"
        
        for i, parent in enumerate(parent_chain):
            result += f"[{i}] {parent.get('class_name', 'Unknown')}\n"
            result += f"    Handle: {parent.get('class_handle', 'N/A')}\n"
            result += f"    Namespace: {parent.get('namespace', '[No Namespace]')}\n"
        
        result += "\n" + "=" * 80
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get parent chain: {e}")]


async def handle_list_instance_methods(args: dict) -> list[TextContent]:
    """List all methods of instance (lms)"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        methods = state.script.exports_sync.list_instance_methods(instance_ptr)
        
        if methods and len(methods) > 0 and 'error' in methods[0]:
            return [TextContent(type="text", text=f"[✗] {methods[0]['error']}")]
        
        result = "=" * 100 + "\n"
        result += f"Instance Methods (Instance: {instance_ptr})\n"
        result += f"Found {len(methods)} methods\n"
        result += "=" * 100 + "\n"
        
        for m in methods:
            static_str = "[static] " if m.get('is_static', False) else ""
            generic_str = "[generic] " if m.get('is_generic', False) else ""
            result += f"[{m.get('index', 0)}] {m.get('handle', 'N/A')} -> {m.get('virtual_address', 'N/A')}\n"
            result += f"    {static_str}{generic_str}{m.get('return_type', 'void')} {m.get('name', 'Unknown')}() | params: {m.get('parameter_count', 0)}\n"
        
        result += "=" * 100
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to list instance methods: {e}")]


async def handle_read_at_offset(args: dict) -> list[TextContent]:
    """Read value at specified offset of instance"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        offset = args.get("offset", 0)
        size = args.get("size", 8)
        
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        read_result = state.script.exports_sync.read_at_offset(instance_ptr, offset, size)
        
        if 'error' in read_result:
            return [TextContent(type="text", text=f"[✗] {read_result['error']}")]
        
        result = f"Instance: {read_result.get('instance_handle', 'N/A')}\n"
        result += f"Offset: {read_result.get('offset', 0)} ({read_result.get('offset_hex', 'N/A')})\n"
        result += f"Address: {read_result.get('address', 'N/A')}\n"
        result += f"Size: {read_result.get('size', 0)} bytes\n"
        result += f"Value: {read_result.get('value', 'N/A')}"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to read offset value: {e}")]


async def handle_set_field_value(args: dict) -> list[TextContent]:
    """Set instance field value"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        field_name = args.get("field_name", "")
        value = args.get("value", "")
        class_handle = args.get("class_handle")
        
        if not instance_ptr or not field_name or not value:
            return [TextContent(type="text", text="[✗] Please specify instance pointer, field name and new value")]
        
        set_result = state.script.exports_sync.set_field_value(instance_ptr, field_name, value, class_handle)
        
        if 'error' in set_result:
            return [TextContent(type="text", text=f"[✗] {set_result['error']}")]
        
        result = f"[✓] Field value set successfully\n"
        result += f"Field: {set_result.get('field_name', 'N/A')}\n"
        result += f"Offset: 0x{set_result.get('field_offset', 0):04x}\n"
        result += f"New Value: {set_result.get('new_value', 'N/A')}"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to set field value: {e}")]


# ========== Unity operation handlers ==========

async def handle_unity_get_transform(args: dict) -> list[TextContent]:
    """Get Transform"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        result = state.script.exports_sync.get_transform(instance_ptr)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Instance: {result.get('instance_handle', 'N/A')}\n"
        text += f"Transform: {result.get('transform_handle', 'N/A')}\n"
        text += f"Type: {result.get('type', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get Transform: {e}")]


async def handle_unity_get_gameobject(args: dict) -> list[TextContent]:
    """Get GameObject"""
    try:
        if err := _check_connection():
            return [err]
        
        instance_ptr = args.get("instance_ptr", "")
        if not instance_ptr:
            return [TextContent(type="text", text="[✗] Please specify instance pointer")]
        
        result = state.script.exports_sync.get_game_object(instance_ptr)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Instance: {result.get('instance_handle', 'N/A')}\n"
        text += f"GameObject: {result.get('gameobject_handle', 'N/A')}\n"
        text += f"Name: {result.get('name', 'N/A')}\n"
        text += f"Layer: {result.get('layer', 0)}\n"
        text += f"Active: {result.get('active_self', False)}\n"
        text += f"Source Type: {result.get('source_type', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get GameObject: {e}")]


async def handle_unity_get_children(args: dict) -> list[TextContent]:
    """Get child objects"""
    try:
        if err := _check_connection():
            return [err]
        
        transform_ptr = args.get("transform_ptr", "")
        if not transform_ptr:
            return [TextContent(type="text", text="[✗] Please specify Transform pointer")]
        
        result = state.script.exports_sync.get_children(transform_ptr)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Transform: {result.get('transform_handle', 'N/A')}\n"
        text += f"Child Count: {result.get('child_count', 0)}\n"
        text += "-" * 50 + "\n"
        
        for child in result.get('children', []):
            text += f"[{child.get('index', 0)}] {child.get('transform_handle', 'N/A')} - {child.get('name', 'N/A')}\n"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get children: {e}")]


async def handle_unity_get_parent(args: dict) -> list[TextContent]:
    """Get parent object"""
    try:
        if err := _check_connection():
            return [err]
        
        transform_ptr = args.get("transform_ptr", "")
        if not transform_ptr:
            return [TextContent(type="text", text="[✗] Please specify Transform pointer")]
        
        result = state.script.exports_sync.get_parent(transform_ptr)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Transform: {result.get('transform_handle', 'N/A')}\n"
        text += f"Parent: {result.get('parent_handle', 'N/A')}\n"
        text += f"Parent Name: {result.get('parent_name', 'N/A')}\n"
        text += f"Is Root: {result.get('is_root', False)}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get parent: {e}")]


async def handle_unity_get_hierarchy(args: dict) -> list[TextContent]:
    """Get hierarchy path"""
    try:
        if err := _check_connection():
            return [err]
        
        transform_ptr = args.get("transform_ptr", "")
        max_depth = args.get("max_depth", 10)
        
        if not transform_ptr:
            return [TextContent(type="text", text="[✗] Please specify Transform pointer")]
        
        result = state.script.exports_sync.get_hierarchy(transform_ptr, max_depth)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Transform: {result.get('transform_handle', 'N/A')}\n"
        text += f"Path: {result.get('path', 'N/A')}\n"
        text += "-" * 50 + "\n"
        
        for item in result.get('hierarchy', []):
            indent = "  " * item.get('depth', 0)
            text += f"{indent}[{item.get('depth', 0)}] {item.get('name', 'N/A')} ({item.get('transform_handle', 'N/A')})\n"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get hierarchy: {e}")]


async def handle_unity_send_message(args: dict) -> list[TextContent]:
    """Send message"""
    try:
        if err := _check_connection():
            return [err]
        
        gameobject_name = args.get("gameobject_name", "")
        method_name = args.get("method_name", "")
        message = args.get("message", "")
        
        if not gameobject_name or not method_name:
            return [TextContent(type="text", text="[✗] Please specify GameObject name and method name")]
        
        result = state.script.exports_sync.send_message(gameobject_name, method_name, message)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] Message sent successfully\n"
        text += f"GameObject: {result.get('gameobject_name', 'N/A')}\n"
        text += f"Method: {result.get('method_name', 'N/A')}\n"
        text += f"Message: {result.get('message', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to send message: {e}")]


async def handle_unity_find_gameobject(args: dict) -> list[TextContent]:
    """Find GameObject"""
    try:
        if err := _check_connection():
            return [err]
        
        path = args.get("path", "")
        if not path:
            return [TextContent(type="text", text="[✗] Please specify GameObject path")]
        
        result = state.script.exports_sync.find_game_object(path)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Path: {result.get('path', 'N/A')}\n"
        text += f"GameObject: {result.get('gameobject_handle', 'N/A')}\n"
        text += f"Name: {result.get('name', 'N/A')}\n"
        text += f"Layer: {result.get('layer', 0)}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to find GameObject: {e}")]


# ========== Memory operation handlers ==========

async def handle_memory_alloc_cstring(args: dict) -> list[TextContent]:
    """Allocate C string"""
    try:
        if err := _check_connection():
            return [err]
        
        s = args.get("str", "")
        result = state.script.exports_sync.alloc_c_string(s)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] String allocated successfully\n"
        text += f"Pointer: {result.get('pointer', 'N/A')}\n"
        text += f"Content: {result.get('content', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to allocate string: {e}")]


async def handle_memory_alloc_il2cpp_string(args: dict) -> list[TextContent]:
    """Allocate IL2CPP string"""
    try:
        if err := _check_connection():
            return [err]
        
        s = args.get("str", "")
        result = state.script.exports_sync.alloc_il2cpp_string(s)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] IL2CPP string allocated successfully\n"
        text += f"Pointer: {result.get('pointer', 'N/A')}\n"
        text += f"Content: {result.get('content', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to allocate IL2CPP string: {e}")]


async def handle_memory_alloc(args: dict) -> list[TextContent]:
    """Allocate memory"""
    try:
        if err := _check_connection():
            return [err]
        
        size = args.get("size", 0)
        result = state.script.exports_sync.alloc_memory(size)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] Memory allocated successfully\n"
        text += f"Pointer: {result.get('pointer', 'N/A')}\n"
        text += f"Size: {result.get('size', 0)} bytes"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to allocate memory: {e}")]


async def handle_memory_alloc_vector(args: dict) -> list[TextContent]:
    """Allocate Vector"""
    try:
        if err := _check_connection():
            return [err]
        
        values = args.get("values", [])
        result = state.script.exports_sync.alloc_vector(values)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] Vector allocated successfully\n"
        text += f"Pointer: {result.get('pointer', 'N/A')}\n"
        text += f"Values: {result.get('values', [])}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to allocate Vector: {e}")]


async def handle_memory_scan(args: dict) -> list[TextContent]:
    """Memory scan - unified interface"""
    try:
        if err := _check_connection():
            return [err]
        
        pattern = args.get("pattern", "")
        if not pattern:
            return [TextContent(type="text", text="[✗] Please specify search pattern")]
        
        options = {
            "protection": args.get("protection", "r--"),
            "moduleName": args.get("module_name"),
            "coalesce": args.get("coalesce", False),
            "limit": args.get("limit", 100)
        }
        
        result = state.script.exports_sync.scan(pattern, options)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = "=" * 60 + "\n"
        text += f"Memory Scan Results\n"
        text += "=" * 60 + "\n"
        text += f"Pattern: {result.get('pattern', 'N/A')}\n"
        text += f"Protection: {result.get('protection', 'N/A')}\n"
        
        if result.get('module'):
            text += f"Module: {result.get('module', 'N/A')} (Base: {result.get('module_base', 'N/A')})\n"
        else:
            text += f"Ranges Scanned: {result.get('ranges_scanned', 0)}\n"
            text += f"Coalesce: {result.get('coalesce', False)}\n"
        
        text += f"Result Count: {result.get('result_count', 0)}\n"
        text += "-" * 60 + "\n"
        
        for r in result.get('results', [])[:50]:
            text += f"  {r.get('address', 'N/A')} (size: {r.get('size', 0)})\n"
        
        if result.get('result_count', 0) > 50:
            text += f"  ... {result.get('result_count', 0) - 50} more results\n"
        
        text += "=" * 60
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Search failed: {e}")]


async def handle_memory_write(args: dict) -> list[TextContent]:
    """Write memory"""
    try:
        if err := _check_connection():
            return [err]
        
        address = args.get("address", "")
        value = args.get("value")
        type_str = args.get("type", "int")
        
        result = state.script.exports_sync.write_memory(address, value, type_str)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"[✓] Write successful\n"
        text += f"Address: {result.get('address', 'N/A')}\n"
        text += f"Value: {result.get('value', 'N/A')}\n"
        text += f"Type: {result.get('type', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Write failed: {e}")]


async def handle_memory_read(args: dict) -> list[TextContent]:
    """Read memory"""
    try:
        if err := _check_connection():
            return [err]
        
        address = args.get("address", "")
        type_str = args.get("type", "pointer")
        length = args.get("length", 0)
        
        result = state.script.exports_sync.read_memory(address, type_str, length)
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = f"Address: {result.get('address', 'N/A')}\n"
        text += f"Type: {result.get('type', 'N/A')}\n"
        text += f"Value: {result.get('value', 'N/A')}"
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Read failed: {e}")]


# ========== Application info handlers ==========

async def handle_app_get_apk_info() -> list[TextContent]:
    """Get APK information"""
    try:
        if err := _check_connection():
            return [err]
        
        result = state.script.exports_sync.get_apk_info()
        
        if 'error' in result:
            return [TextContent(type="text", text=f"[✗] {result['error']}")]
        
        text = "=" * 60 + "\n"
        text += "APK Information\n"
        text += "=" * 60 + "\n"
        text += f"App Name: {result.get('app_name', 'N/A')}\n"
        text += f"Package: {result.get('package_name', 'N/A')}\n"
        text += f"Version: {result.get('version_name', 'N/A')} ({result.get('version_code', 'N/A')})\n"
        text += f"Target SDK: {result.get('target_sdk_version', 'N/A')}\n"
        text += f"UID: {result.get('uid', 'N/A')}\n"
        text += f"Size: {result.get('app_size_mb', 'N/A')} MB\n"
        text += f"Debuggable: {result.get('is_debuggable', False)}\n"
        text += f"Backupable: {result.get('is_backupable', False)}\n"
        text += "-" * 60 + "\n"
        text += f"Source Dir: {result.get('source_dir', 'N/A')}\n"
        text += f"Data Dir: {result.get('data_dir', 'N/A')}\n"
        text += f"Native Lib Dir: {result.get('native_library_dir', 'N/A')}\n"
        text += "-" * 60 + "\n"
        text += f"Install Time: {result.get('first_install_time', 'N/A')}\n"
        text += f"Update Time: {result.get('last_update_time', 'N/A')}\n"
        
        signatures = result.get('signatures', {})
        if signatures:
            text += "-" * 60 + "\n"
            text += f"MD5: {signatures.get('md5', 'N/A')}\n"
            text += f"SHA-1: {signatures.get('sha1', 'N/A')}\n"
            text += f"SHA-256: {signatures.get('sha256', 'N/A')}\n"
        
        if result.get('unity_build_id'):
            text += f"Unity Build ID: {result.get('unity_build_id')}\n"
        
        text += "=" * 60
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get APK info: {e}")]


async def handle_unity_get_scene_info(args: dict) -> list[TextContent]:
    """Get current scene information with all GameObjects and attached scripts"""
    try:
        if err := _check_connection():
            return [err]
        
        max_depth = args.get("max_depth", 10)
        include_inactive = args.get("include_inactive", True)
        
        # Execute JavaScript to collect scene info
        js_code = f'''
(function() {{
    const maxDepth = {max_depth};
    const includeInactive = {'true' if include_inactive else 'false'};
    
    // Unity built-in component types to filter out
    const builtInTypes = new Set([
        'Transform', 'RectTransform', 'CanvasRenderer', 'Image', 'Text',
        'Button', 'Canvas', 'CanvasScaler', 'GraphicRaycaster', 'EventSystem',
        'StandaloneInputModule', 'Camera', 'AudioListener', 'Light',
        'MeshRenderer', 'MeshFilter', 'SpriteRenderer', 'Animator',
        'Animation', 'Rigidbody', 'Rigidbody2D', 'Collider', 'Collider2D',
        'BoxCollider', 'BoxCollider2D', 'SphereCollider', 'CapsuleCollider',
        'CharacterController', 'ParticleSystem', 'TrailRenderer', 'LineRenderer',
        'SkinnedMeshRenderer', 'LODGroup', 'AudioSource', 'VideoPlayer',
        'TextMesh', 'TextMeshPro', 'TextMeshProUGUI', 'TMP_Text',
        'ScrollRect', 'Scrollbar', 'Slider', 'Toggle', 'ToggleGroup',
        'InputField', 'Dropdown', 'Mask', 'RawImage', 'LayoutElement',
        'ContentSizeFitter', 'AspectRatioFitter', 'HorizontalLayoutGroup',
        'VerticalLayoutGroup', 'GridLayoutGroup', 'LayoutGroup',
        'RectMask2D', 'Shadow', 'Outline', 'PositionAsUV1'
    ]);
    
    const result = {{
        scene_name: '',
        root_count: 0,
        total_gameobjects: 0,
        total_scripts: 0,
        roots: [],
        scripts_summary: []
    }};
    
    // Collect all MonoBehaviours and their GameObjects
    const MonoBehaviour = Il2Cpp.domain.assembly("UnityEngine.CoreModule").image.class("UnityEngine.MonoBehaviour");
    const Transform = Il2Cpp.domain.assembly("UnityEngine.CoreModule").image.class("UnityEngine.Transform");
    const GameObject = Il2Cpp.domain.assembly("UnityEngine.CoreModule").image.class("UnityEngine.GameObject");
    
    // Get current scene name - find from custom scripts that contain "Scene" in name
    let foundSceneName = 'Unknown';
    const sceneScripts = [];
    
    // Map: GO pointer -> {{name, ptr, scripts: [{{name, ptr}}], children: []}}
    const goMap = new Map();
    // Map: GO pointer -> parent GO pointer
    const parentMap = new Map();
    // Script summary
    const scriptCounts = new Map();
    // Root transforms
    const rootTransforms = [];
    
    // Collect all MonoBehaviours
    Il2Cpp.gc.choose(MonoBehaviour).forEach(mb => {{
        try {{
            const className = mb.class.name;
            if (builtInTypes.has(className)) return;
            
            // Check if this is a scene script (contains "Scene" in name)
            if (className.includes('Scene') && foundSceneName === 'Unknown') {{
                foundSceneName = className;
            }}
            
            const go = mb.method("get_gameObject").invoke();
            if (go.isNull()) return;
            
            // Check active state
            if (!includeInactive) {{
                const activeSelf = go.method("get_activeSelf").invoke();
                if (!activeSelf) return;
            }}
            
            const goPtr = go.handle.toString();
            const goName = go.method("get_name").invoke().content || 'Unknown';
            
            if (!goMap.has(goPtr)) {{
                goMap.set(goPtr, {{
                    name: goName,
                    ptr: goPtr,
                    scripts: [],
                    children: [],
                    active: go.method("get_activeSelf").invoke() ? true : false
                }});
                
                // Also collect transform hierarchy for this GO
                const transform = go.method("get_transform").invoke();
                if (!transform.isNull()) {{
                    const parent = transform.method("get_parent").invoke();
                    if (parent.isNull()) {{
                        rootTransforms.push({{ transform: transform, goPtr: goPtr }});
                    }} else {{
                        const parentGo = parent.method("get_gameObject").invoke();
                        if (!parentGo.isNull()) {{
                            parentMap.set(goPtr, parentGo.handle.toString());
                        }}
                    }}
                }}
            }}
            
            goMap.get(goPtr).scripts.push({{
                name: className,
                ptr: mb.handle.toString()
            }});
            
            // Count scripts
            scriptCounts.set(className, (scriptCounts.get(className) || 0) + 1);
            result.total_scripts++;
        }} catch(e) {{}}
    }});
    
    result.scene_name = foundSceneName;
    
    // Collect all Transforms to build hierarchy (for GOs without custom scripts)
    Il2Cpp.gc.choose(Transform).forEach(t => {{
        try {{
            const go = t.method("get_gameObject").invoke();
            if (go.isNull()) return;
            
            const goPtr = go.handle.toString();
            const goName = go.method("get_name").invoke().content || 'Unknown';
            
            // Ensure GO is in map
            if (!goMap.has(goPtr)) {{
                if (!includeInactive) {{
                    const activeSelf = go.method("get_activeSelf").invoke();
                    if (!activeSelf) return;
                }}
                goMap.set(goPtr, {{
                    name: goName,
                    ptr: goPtr,
                    scripts: [],
                    children: [],
                    active: go.method("get_activeSelf").invoke() ? true : false
                }});
            }}
            
            // Check parent
            const parent = t.method("get_parent").invoke();
            if (parent.isNull()) {{
                rootTransforms.push({{ transform: t, goPtr: goPtr }});
            }} else {{
                const parentGo = parent.method("get_gameObject").invoke();
                if (!parentGo.isNull()) {{
                    parentMap.set(goPtr, parentGo.handle.toString());
                }}
            }}
        }} catch(e) {{}}
    }});
    
    // Build parent-child relationships
    for (const [childPtr, parentPtr] of parentMap) {{
        if (goMap.has(parentPtr) && goMap.has(childPtr)) {{
            goMap.get(parentPtr).children.push(childPtr);
        }}
    }}
    
    // Build tree structure from roots
    function buildTree(goPtr, depth) {{
        if (depth > maxDepth) return null;
        const goInfo = goMap.get(goPtr);
        if (!goInfo) return null;
        
        const node = {{
            name: goInfo.name,
            ptr: goInfo.ptr,
            active: goInfo.active,
            scripts: goInfo.scripts,
            children: []
        }};
        
        for (const childPtr of goInfo.children) {{
            const childNode = buildTree(childPtr, depth + 1);
            if (childNode) {{
                node.children.push(childNode);
            }}
        }}
        
        return node;
    }}
    
    // Process roots
    const processedRoots = new Set();
    for (const {{ goPtr }} of rootTransforms) {{
        if (processedRoots.has(goPtr)) continue;
        processedRoots.add(goPtr);
        
        const tree = buildTree(goPtr, 0);
        if (tree) {{
            result.roots.push(tree);
        }}
    }}
    
    result.root_count = result.roots.length;
    result.total_gameobjects = goMap.size;
    
    // Build script summary
    for (const [name, count] of scriptCounts) {{
        result.scripts_summary.push({{ name, count }});
    }}
    result.scripts_summary.sort((a, b) => b.count - a.count);
    
    return result;
}})();
'''
        
        result_data = state.script.exports_sync.exec_js(js_code)
        
        if not result_data.get('success'):
            return [TextContent(type="text", text=f"[✗] Failed to get scene info: {result_data.get('error', 'Unknown error')}")]
        
        scene_info = result_data.get('result', {})
        
        # Format output
        text = "=" * 100 + "\n"
        text += f"Scene Information: {scene_info.get('scene_name', 'Unknown')}\n"
        text += "=" * 100 + "\n"
        text += f"Root GameObjects: {scene_info.get('root_count', 0)}\n"
        text += f"Total GameObjects: {scene_info.get('total_gameobjects', 0)}\n"
        text += f"Total Custom Scripts: {scene_info.get('total_scripts', 0)}\n"
        text += "-" * 100 + "\n"
        
        # Script summary
        scripts_summary = scene_info.get('scripts_summary', [])
        if scripts_summary:
            text += "\n[Custom Scripts Summary]\n"
            for s in scripts_summary[:20]:
                text += f"  {s.get('name', 'Unknown')}: {s.get('count', 0)} instance(s)\n"
            if len(scripts_summary) > 20:
                text += f"  ... and {len(scripts_summary) - 20} more script types\n"
        
        text += "\n" + "-" * 100 + "\n"
        text += "[Scene Hierarchy]\n\n"
        
        # Build hierarchy text
        def format_node(node, indent=0):
            prefix = "  " * indent
            active_str = "" if node.get('active', True) else " [inactive]"
            result = f"{prefix}├─ {node.get('name', 'Unknown')}{active_str}\n"
            result += f"{prefix}│  GO: {node.get('ptr', 'N/A')}\n"
            
            scripts = node.get('scripts', [])
            if scripts:
                for script in scripts:
                    result += f"{prefix}│  └─ [Script] {script.get('name', 'Unknown')}: {script.get('ptr', 'N/A')}\n"
            
            children = node.get('children', [])
            for child in children:
                result += format_node(child, indent + 1)
            
            return result
        
        roots = scene_info.get('roots', [])
        for root in roots:
            text += format_node(root)
            text += "\n"
        
        text += "=" * 100
        
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get scene info: {e}")]
