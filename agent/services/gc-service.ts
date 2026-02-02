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
            
            // 检查类是否可以被 gc.choose 使用
            if (klass.isValueType) {
                return [{error: `Cannot use gc.choose on value type: ${className}`}];
            }
            
            try {
                Il2Cpp.gc.choose(klass).forEach((instance: Il2Cpp.Object) => {
                    if (result.length < maxCount) {
                        try {
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
                        } catch (e) {
                            // 忽略无法处理的实例
                        }
                    }
                });
            } catch (e) {
                return [{error: `gc.choose failed for ${className}: ${e}`}];
            }
        } catch (e) {
            return [{error: String(e)}];
        }
        
        return result;
    }

    /**
     * 获取 GC 堆信息
     */
    static gcInfo(): any {
        try {
            const heapSize = Il2Cpp.gc.heapSize;
            const usedHeapSize = Il2Cpp.gc.usedHeapSize;
            
            return {
                heap_size: typeof heapSize === 'number' ? heapSize : parseInt(String(heapSize)) || 0,
                used_heap_size: typeof usedHeapSize === 'number' ? usedHeapSize : parseInt(String(usedHeapSize)) || 0,
                is_enabled: Il2Cpp.gc.isEnabled,
                is_incremental: Il2Cpp.gc.isIncremental,
                max_time_slice: Il2Cpp.gc.maxTimeSlice
            };
        } catch (e) {
            return {
                error: `Failed to get GC info: ${e}`,
                heap_size: 0,
                used_heap_size: 0,
                is_enabled: false,
                is_incremental: false,
                max_time_slice: 0
            };
        }
    }
}
