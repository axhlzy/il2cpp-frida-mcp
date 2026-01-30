import "frida-il2cpp-bridge"
import { findClass } from "../core/class-finder"

/**
 * GC 服务 - 处理垃圾回收和堆相关操作
 */
export class GCService {
    /**
     * 在堆中查找指定类的所有实例
     */
    static gcChoose(className: string, maxCount: number = 100): any[] {
        const result: any[] = [];
        
        try {
            const classPtr = findClass(className);
            if (classPtr.isNull()) {
                return [{error: `Class not found: ${className}`}];
            }
            
            const klass = new Il2Cpp.Class(classPtr);
            
            Il2Cpp.gc.choose(klass).forEach((instance: Il2Cpp.Object) => {
                if (result.length < maxCount) {
                    const info: any = {
                        handle: instance.handle.toString(),
                        class_name: instance.class.name,
                        class_handle: instance.class.handle.toString()
                    };
                    
                    // 尝试获取一些字段值
                    try {
                        const fields: any = {};
                        for (const field of instance.class.fields) {
                            try {
                                if (!field.isStatic && !field.isLiteral) {
                                    const value = instance.field(field.name).value;
                                    if (value !== null && value !== undefined) {
                                        if (typeof value === 'object' && 'handle' in value) {
                                            fields[field.name] = (value as any).handle.toString();
                                        } else {
                                            fields[field.name] = String(value);
                                        }
                                    }
                                }
                            } catch (e) {
                                // 忽略无法读取的字段
                            }
                        }
                        if (Object.keys(fields).length > 0) {
                            info.fields = fields;
                        }
                    } catch (e) {
                        // 忽略
                    }
                    
                    result.push(info);
                }
            });
        } catch (e) {
            return [{error: String(e)}];
        }
        
        return result;
    }

    /**
     * 获取 GC 堆信息
     */
    static gcInfo(): any {
        return {
            heap_size: Il2Cpp.gc.heapSize,
            used_heap_size: Il2Cpp.gc.usedHeapSize,
            is_enabled: Il2Cpp.gc.isEnabled,
            is_incremental: Il2Cpp.gc.isIncremental,
            max_time_slice: Il2Cpp.gc.maxTimeSlice
        };
    }
}
