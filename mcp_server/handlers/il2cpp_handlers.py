"""
IL2CPP 操作处理器
"""
from mcp.types import TextContent
from ..state import state


def _check_connection() -> TextContent | None:
    """检查连接状态"""
    if not state.connected or not state.script:
        return TextContent(type="text", text="[✗] 请先连接到目标进程")
    return None


async def handle_list_images(args: dict) -> list[TextContent]:
    """列出 IL2CPP 镜像"""
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
        return [TextContent(type="text", text=f"[✗] 列出镜像失败: {e}")]


async def handle_list_classes(args: dict) -> list[TextContent]:
    """列出类"""
    try:
        if err := _check_connection():
            return [err]
        
        image_name = args.get("image_name", "")
        filter_namespace = args.get("filter_namespace", "")
        filter_classname = args.get("filter_classname", "")
        
        if not image_name:
            return [TextContent(type="text", text="[✗] 请指定镜像名称")]
        
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
        return [TextContent(type="text", text=f"[✗] 列出类失败: {e}")]


async def handle_list_methods(args: dict) -> list[TextContent]:
    """列出类的方法"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        if not class_name:
            return [TextContent(type="text", text="[✗] 请指定类名")]
        
        methods = state.script.exports_sync.list_methods(class_name)
        
        if not methods:
            return [TextContent(type="text", text=f"[✗] 未找到类: {class_name}")]
        
        result = "=" * 85 + "\n"
        result += f"Found {len(methods)} Methods in class: {methods[0]['class_name']}\n"
        result += "第一列: Il2CppMethod 指针 | 第二列: 内存地址 | 第三列: 相对地址(减去基址)\n"
        result += "=" * 85 + "\n"
        
        for m in methods:
            result += f"[*] {m['handle']} -> {m['virtual_address']} -> {m['relative_virtual_address']}\t| {m['modifier']} {m['return_type']} {m['name']}()\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 列出方法失败: {e}")]


async def handle_show_method(args: dict) -> list[TextContent]:
    """显示方法详情"""
    try:
        if err := _check_connection():
            return [err]
        
        il2cpp_method_ptr = args.get("il2cpp_method_ptr", "")
        if not il2cpp_method_ptr:
            return [TextContent(type="text", text="[✗] 请指定方法指针")]
        
        info = state.script.exports_sync.show_method(il2cpp_method_ptr)
        
        if not info:
            return [TextContent(type="text", text=f"[✗] 未找到方法: {il2cpp_method_ptr}")]
        
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
        return [TextContent(type="text", text=f"[✗] 获取方法信息失败: {e}")]


async def handle_find_classes(args: dict) -> list[TextContent]:
    """查找类"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        complete_match = args.get("complete_match", False)
        
        if not class_name:
            return [TextContent(type="text", text="[✗] 请指定类名")]
        
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
        return [TextContent(type="text", text=f"[✗] 查找类失败: {e}")]


async def handle_find_methods(args: dict) -> list[TextContent]:
    """查找方法"""
    try:
        if err := _check_connection():
            return [err]
        
        method_name = args.get("method_name", "")
        find_all = args.get("find_all", True)
        accurate = args.get("accurate", False)
        
        if not method_name:
            return [TextContent(type="text", text="[✗] 请指定方法名")]
        
        methods = state.script.exports_sync.find_methods(method_name, find_all, accurate)
        
        result = "=" * 100 + "\n"
        result += f"Found {len(methods)} Methods matching '{method_name}'\n"
        result += "=" * 100 + "\n"
        
        for m in methods[:100]:
            ns_str = f"{m['namespace']}." if m.get('namespace') and m['namespace'] != "[No Namespace]" else ""
            method_sig = f"{m['modifier']} {m['return_type']} {ns_str}{m['class_name']}.{m['name']}()"
            result += f"[*] {m['handle']} -> {m['virtual_address']} -> {m['relative_virtual_address']}\t| {method_sig}\n"
        
        if len(methods) > 100:
            result += f"\n  ... 还有 {len(methods) - 100} 个方法\n"
        
        result += "=" * 100
        result += f"\n\n提示: 调用函数时请使用第二列地址 (virtual_address)"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 查找方法失败: {e}")]


async def handle_show_asm(args: dict) -> list[TextContent]:
    """显示反汇编"""
    try:
        if err := _check_connection():
            return [err]
        
        il2cpp_method_ptr = args.get("il2cpp_method_ptr", "")
        instruction_count = args.get("instruction_count", 64)
        resolve_functions = args.get("resolve_functions", False)
        
        if not il2cpp_method_ptr:
            return [TextContent(type="text", text="[✗] 请指定方法指针")]
        
        if resolve_functions:
            result = "[!] 注意: 已开启函数解析,需要预加载所有函数,这可能需要较长时间...\n\n"
        else:
            result = ""
        
        asm_result = state.script.exports_sync.show_asm(il2cpp_method_ptr, instruction_count, resolve_functions)
        instructions = asm_result.get('instructions', [])
        
        result += "=" * 85 + "\n"
        result += f"Disassembly of {il2cpp_method_ptr} ({len(instructions)} instructions)\n"
        if resolve_functions and asm_result.get('methods_preloaded'):
            result += "[*] 函数解析已启用,跳转目标将显示函数名\n"
        result += "=" * 85 + "\n"
        
        for ins in instructions:
            result += f"{ins['address']}: {ins['toString']}\n"
            if 'target_method' in ins:
                result += f"  -> {ins['target_method']['class_name']}.{ins['target_method']['name']}()\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 反汇编失败: {e}")]


async def handle_find_export(args: dict) -> list[TextContent]:
    """查找导出函数"""
    try:
        if err := _check_connection():
            return [err]
        
        export_name = args.get("export_name", "")
        module_name = args.get("module_name")
        
        if not export_name:
            return [TextContent(type="text", text="[✗] 请指定导出函数名")]
        
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
            result += f"  ... 还有 {len(exports) - 50} 个导出\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 查找导出失败: {e}")]


async def handle_find_import(args: dict) -> list[TextContent]:
    """查找导入函数"""
    try:
        if err := _check_connection():
            return [err]
        
        module_name = args.get("module_name", "")
        import_name = args.get("import_name")
        
        if not module_name:
            return [TextContent(type="text", text="[✗] 请指定模块名称")]
        
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
            result += f"  ... 还有 {len(imports) - 50} 个导入\n"
        
        result += "=" * 85
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 查找导入失败: {e}")]


async def handle_exec_js(args: dict) -> list[TextContent]:
    """执行 JavaScript 代码"""
    try:
        if err := _check_connection():
            return [err]
        
        code = args.get("code", "")
        
        if not code:
            return [TextContent(type="text", text="[✗] 请提供要执行的代码")]
        
        result_data = state.script.exports_sync.exec_js(code)
        
        if result_data.get('success'):
            result = f"[✓] 代码执行成功\n"
            result += f"Result Type: {result_data.get('type', 'N/A')}\n"
            result += f"Result: {result_data.get('result', 'N/A')}\n"
        else:
            result = f"[✗] 代码执行失败\n"
            result += f"Error: {result_data.get('error', 'Unknown error')}\n"
            if result_data.get('stack'):
                result += f"Stack:\n{result_data.get('stack')}\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 执行代码失败: {e}")]


async def handle_gc_choose(args: dict) -> list[TextContent]:
    """在堆中查找指定类的实例"""
    try:
        if err := _check_connection():
            return [err]
        
        class_name = args.get("class_name", "")
        max_count = args.get("max_count", 100)
        
        if not class_name:
            return [TextContent(type="text", text="[✗] 请指定类名")]
        
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
        return [TextContent(type="text", text=f"[✗] 查找实例失败: {e}")]


async def handle_gc_info() -> list[TextContent]:
    """获取 GC 堆信息"""
    try:
        if err := _check_connection():
            return [err]
        
        info = state.script.exports_sync.gc_info()
        
        result = "=" * 50 + "\n"
        result += "GC Heap Information\n"
        result += "=" * 50 + "\n"
        result += f"Heap Size: {info.get('heap_size', 0) / 1024 / 1024:.2f} MB\n"
        result += f"Used Heap Size: {info.get('used_heap_size', 0) / 1024 / 1024:.2f} MB\n"
        result += f"GC Enabled: {info.get('is_enabled', False)}\n"
        result += f"Incremental GC: {info.get('is_incremental', False)}\n"
        result += f"Max Time Slice: {info.get('max_time_slice', 0)} ms\n"
        result += "=" * 50
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 获取 GC 信息失败: {e}")]
