/**
 * 内存操作服务
 * 提供内存搜索、分配、读写等功能
 */

/**
 * 内存服务
 */
export class MemoryService {
    /**
     * 分配 C 字符串 (UTF-8)
     * @param str 字符串
     */
    static allocCString(str: string): any {
        try {
            const ptr_str = Memory.allocUtf8String(str);
            return {
                success: true,
                pointer: ptr_str.toString(),
                type: "c_string",
                content: str
            };
        } catch (e) {
            return { error: `Failed to allocate C string: ${e}` };
        }
    }

    /**
     * 分配 IL2CPP 字符串 (System.String)
     * @param str 字符串
     */
    static allocIl2cppString(str: string): any {
        try {
            const il2cppStr = Il2Cpp.string(str);
            return {
                success: true,
                pointer: il2cppStr.handle.toString(),
                type: "il2cpp_string",
                content: str
            };
        } catch (e) {
            return { error: `Failed to allocate IL2CPP string: ${e}` };
        }
    }

    /**
     * 分配内存
     * @param size 大小（字节）
     */
    static allocMemory(size: number): any {
        try {
            const ptr_mem = Memory.alloc(size);
            return {
                success: true,
                pointer: ptr_mem.toString(),
                size: size
            };
        } catch (e) {
            return { error: `Failed to allocate memory: ${e}` };
        }
    }

    /**
     * 分配 Vector (float 数组)
     * @param values 浮点数数组
     */
    static allocVector(values: number[]): any {
        try {
            const size = values.length * 4; // float = 4 bytes
            const ptr_vec = Memory.alloc(size);
            
            for (let i = 0; i < values.length; i++) {
                ptr_vec.add(i * 4).writeFloat(values[i]);
            }
            
            return {
                success: true,
                pointer: ptr_vec.toString(),
                size: size,
                values: values
            };
        } catch (e) {
            return { error: `Failed to allocate vector: ${e}` };
        }
    }

    /**
     * 内存搜索 - 统一接口
     * 使用 Memory.scanSync 和 Process.enumerateRanges
     * 
     * @param pattern 搜索模式，格式如 "13 37 ?? ff" 或 "/regex/"
     * @param options 搜索选项
     *   - protection: 内存保护属性，如 "r--", "rw-", "r-x", "rwx" 等，默认 "r--"
     *   - moduleName: 可选，指定搜索的模块名
     *   - coalesce: 是否合并相邻的内存区域，默认 false
     *   - limit: 最大结果数量，默认 100
     */
    static scan(pattern: string, options?: {
        protection?: string;
        moduleName?: string;
        coalesce?: boolean;
        limit?: number;
    }): any {
        try {
            const protection = options?.protection || "r--";
            const moduleName = options?.moduleName;
            const coalesce = options?.coalesce || false;
            const limit = options?.limit || 100;
            
            const results: Array<{ address: string; size: number }> = [];
            let matchPattern: MatchPattern;
            
            try {
                matchPattern = new MatchPattern(pattern);
            } catch (e) {
                return { error: `Invalid pattern: ${pattern}. Error: ${e}` };
            }
            
            const scanRange = (base: NativePointer, size: number) => {
                if (results.length >= limit) return;
                
                try {
                    const matches = Memory.scanSync(base, size, matchPattern);
                    for (const match of matches) {
                        if (results.length >= limit) break;
                        results.push({
                            address: match.address.toString(),
                            size: match.size
                        });
                    }
                } catch (e) {
                    // 忽略无法访问的内存区域
                }
            };
            
            if (moduleName) {
                // 搜索指定模块
                const module = Process.findModuleByName(moduleName);
                if (!module) {
                    return { error: `Module not found: ${moduleName}` };
                }
                
                // 获取模块的内存区域
                const ranges = module.enumerateRanges(protection);
                for (const range of ranges) {
                    scanRange(range.base, range.size);
                    if (results.length >= limit) break;
                }
                
                return {
                    pattern: pattern,
                    module: moduleName,
                    module_base: module.base.toString(),
                    module_size: module.size,
                    protection: protection,
                    result_count: results.length,
                    results: results
                };
            } else {
                // 搜索所有符合保护属性的内存区域
                const ranges = Process.enumerateRanges({
                    protection: protection,
                    coalesce: coalesce
                });
                
                for (const range of ranges) {
                    scanRange(range.base, range.size);
                    if (results.length >= limit) break;
                }
                
                return {
                    pattern: pattern,
                    protection: protection,
                    coalesce: coalesce,
                    ranges_scanned: ranges.length,
                    result_count: results.length,
                    results: results
                };
            }
        } catch (e) {
            return { error: `Scan failed: ${e}` };
        }
    }

    /**
     * 写入内存值
     * @param address 地址
     * @param value 值
     * @param type 类型
     */
    static writeMemory(address: string, value: number | string, type: string = "int"): any {
        try {
            const addr = ptr(address);
            
            switch (type) {
                case "int":
                case "int32":
                    addr.writeS32(value as number);
                    break;
                case "uint32":
                    addr.writeU32(value as number);
                    break;
                case "int64":
                    addr.writeS64(value as number);
                    break;
                case "uint64":
                    addr.writeU64(value as number);
                    break;
                case "float":
                    addr.writeFloat(value as number);
                    break;
                case "double":
                    addr.writeDouble(value as number);
                    break;
                case "pointer":
                    addr.writePointer(ptr(value as string));
                    break;
                case "string":
                    addr.writeUtf8String(value as string);
                    break;
                default:
                    return { error: `Unknown type: ${type}` };
            }
            
            return {
                success: true,
                address: address,
                value: value,
                type: type
            };
        } catch (e) {
            return { error: `Failed to write memory: ${e}` };
        }
    }

    /**
     * 读取内存值
     * @param address 地址
     * @param type 类型
     * @param length 长度（用于字符串和字节数组）
     */
    static readMemory(address: string, type: string = "pointer", length: number = 0): any {
        try {
            const addr = ptr(address);
            let value: any;
            
            switch (type) {
                case "int":
                case "int32":
                    value = addr.readS32();
                    break;
                case "uint32":
                    value = addr.readU32();
                    break;
                case "int64":
                    value = addr.readS64().toString();
                    break;
                case "uint64":
                    value = addr.readU64().toString();
                    break;
                case "float":
                    value = addr.readFloat();
                    break;
                case "double":
                    value = addr.readDouble();
                    break;
                case "pointer":
                    value = addr.readPointer().toString();
                    break;
                case "string":
                    value = addr.readUtf8String(length > 0 ? length : undefined);
                    break;
                case "bytes":
                    const bytes = addr.readByteArray(length > 0 ? length : 16);
                    value = bytes ? Array.from(new Uint8Array(bytes)).map(b => b.toString(16).padStart(2, "0")).join(" ") : "";
                    break;
                default:
                    return { error: `Unknown type: ${type}` };
            }
            
            return {
                address: address,
                type: type,
                value: value
            };
        } catch (e) {
            return { error: `Failed to read memory: ${e}` };
        }
    }
}
