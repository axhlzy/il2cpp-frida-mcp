/**
 * 类型值解析工具
 * 参考 ref/Il2cppHook/agent/base/valueResolve.ts
 */

/**
 * 读取 UTF-16 字符串
 */
export function readU16String(mPtr: NativePointer): string {
    if (mPtr.isNull()) return "";
    try {
        const length = mPtr.add(Process.pointerSize * 2).readInt();
        if (length <= 0 || length > 10000) return "";
        return mPtr.add(Process.pointerSize * 2 + 4).readUtf16String(length) || "";
    } catch {
        return "";
    }
}

/**
 * 读取整数值
 */
export function readInt(mPtr: NativePointer): number {
    if (mPtr.isNull()) return 0;
    try {
        return mPtr.toInt32();
    } catch {
        return 0;
    }
}

/**
 * 读取无符号整数
 */
export function readUInt(mPtr: NativePointer): number {
    if (mPtr.isNull()) return 0;
    try {
        return mPtr.toUInt32();
    } catch {
        return 0;
    }
}

/**
 * 读取 64 位整数
 */
export function readInt64(mPtr: NativePointer): Int64 {
    if (mPtr.isNull()) return int64(0);
    try {
        return int64(mPtr.toString());
    } catch {
        return int64(0);
    }
}

/**
 * 读取单精度浮点数
 */
export function readSingle(mPtr: NativePointer): number {
    if (mPtr.isNull()) return 0;
    try {
        return mPtr.readFloat();
    } catch {
        return 0;
    }
}

/**
 * 解析枚举值为名称
 */
export function enumToName(value: number, enumClass: Il2Cpp.Class): string {
    try {
        for (const field of enumClass.fields) {
            if (field.isLiteral && field.isStatic) {
                try {
                    // 尝试直接获取字段值
                    const fieldValue = field.value;
                    if (fieldValue === value) {
                        return field.name;
                    }
                } catch {
                    // 如果无法获取值，跳过
                }
            }
        }
    } catch {
        // ignore
    }
    return `${value}`;
}

/**
 * 解析通用类型值
 */
export function resolveTypeValue(type: Il2Cpp.Type, valuePtr: NativePointer): string {
    if (type.handle.isNull()) return "";
    
    const typeName = type.name;
    
    // 处理枚举类型
    if (type.class.isEnum) {
        const value = valuePtr.toInt32();
        return `Enum(${enumToName(value, type.class)})`;
    }
    
    switch (typeName) {
        case "System.Void":
            return "void";
            
        case "System.Boolean":
            if (valuePtr.isNull()) return "false";
            if (valuePtr.equals(ptr(1))) return "true";
            try {
                return valuePtr.readU8() !== 0 ? "true" : "false";
            } catch {
                return valuePtr.toString();
            }
            
        case "System.Byte":
            try {
                return valuePtr.toUInt32().toString();
            } catch {
                return "0";
            }
            
        case "System.SByte":
            try {
                return (valuePtr.toInt32() << 24 >> 24).toString();
            } catch {
                return "0";
            }
            
        case "System.Int16":
            try {
                return (valuePtr.toInt32() << 16 >> 16).toString();
            } catch {
                return "0";
            }
            
        case "System.UInt16":
            try {
                return (valuePtr.toUInt32() & 0xFFFF).toString();
            } catch {
                return "0";
            }
            
        case "System.Int32":
            return readInt(valuePtr).toString();
            
        case "System.UInt32":
            return readUInt(valuePtr).toString();
            
        case "System.Int64":
            return readInt64(valuePtr).toString();
            
        case "System.UInt64":
            try {
                return uint64(valuePtr.toString()).toString();
            } catch {
                return "0";
            }
            
        case "System.Single":
            return readSingle(valuePtr).toString();
            
        case "System.Double":
            try {
                return valuePtr.add(Process.pointerSize * 2).readDouble().toString();
            } catch {
                return "0";
            }
            
        case "System.String":
            return `"${readU16String(valuePtr)}"`;
            
        case "System.IntPtr":
            if (valuePtr.isNull()) return "null";
            return valuePtr.toString();
            
        case "System.Object":
            if (valuePtr.isNull()) return "null";
            try {
                return new Il2Cpp.Object(valuePtr).toString();
            } catch {
                return valuePtr.toString();
            }
            
        default:
            // 处理数组类型
            if (typeName.endsWith("[]")) {
                if (valuePtr.isNull()) return "null";
                try {
                    const arr = new Il2Cpp.Array(valuePtr);
                    return `Array[${arr.length}]`;
                } catch {
                    return valuePtr.toString();
                }
            }
            
            // 处理 List 类型
            if (typeName.includes("System.Collections.Generic.List")) {
                if (valuePtr.isNull()) return "null";
                try {
                    const obj = new Il2Cpp.Object(valuePtr);
                    const size = obj.field("_size").value;
                    return `List[${size}]`;
                } catch {
                    return valuePtr.toString();
                }
            }
            
            // 处理 Dictionary 类型
            if (typeName.includes("System.Collections.Generic.Dictionary")) {
                if (valuePtr.isNull()) return "null";
                try {
                    const obj = new Il2Cpp.Object(valuePtr);
                    const count = obj.field("_count").value;
                    return `Dictionary[${count}]`;
                } catch {
                    return valuePtr.toString();
                }
            }
            
            // 默认处理
            if (valuePtr.isNull()) return "null";
            try {
                return new Il2Cpp.Object(valuePtr).toString();
            } catch {
                return valuePtr.toString();
            }
    }
}

/**
 * 获取静态字段值
 */
export function getStaticFieldValue(field: Il2Cpp.Field): NativePointer {
    try {
        // 使用 frida-il2cpp-bridge 的方式获取静态字段值
        const value = field.value;
        if (value === null || value === undefined) {
            return ptr(0);
        }
        if (typeof value === 'object' && 'handle' in value) {
            return (value as any).handle;
        }
        // 对于基本类型，返回值本身作为指针
        return ptr(value as any);
    } catch {
        return ptr(0);
    }
}
