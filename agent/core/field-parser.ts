/**
 * 字段解析器
 * 参考 ref/Il2cppHook/agent/bridge/fix/parseFields.ts
 * 实现 lfs, lfp, lfss 等功能
 */

import { resolveTypeValue, getStaticFieldValue, enumToName } from "./type-resolver";
import { getFieldModifier } from "./field-utils";

/**
 * 字段信息接口
 */
export interface FieldInfo {
    index: number;
    name: string;
    offset: number;
    type_name: string;
    type_handle: string;
    class_handle: string;
    modifier: string;
    is_static: boolean;
    is_literal: boolean;
    value_handle?: string;
    value?: string;
}

/**
 * 实例字段解析结果
 */
export interface InstanceFieldsResult {
    instance_handle: string;
    class_name: string;
    class_handle: string;
    namespace: string;
    field_count: number;
    fields: FieldInfo[];
}

/**
 * 父类继承链结果
 */
export interface ParentChainResult {
    instance_handle: string;
    class_chain: Array<{
        class_name: string;
        class_handle: string;
        namespace: string;
        fields: FieldInfo[];
    }>;
}

/**
 * 字段解析器类
 */
export class FieldParser {
    private instancePtr: NativePointer;
    private klass: Il2Cpp.Class | undefined;
    private isInstance: boolean | undefined;

    /**
     * 构造函数
     * @param mPtr 实例指针或类指针
     * @param classHandle 可选的类句柄（用于指定解析哪个类的字段）
     */
    constructor(mPtr: NativePointer | string | number, classHandle?: NativePointer | string | number) {
        // 解析 mPtr
        if (typeof mPtr === "number") {
            this.instancePtr = ptr(mPtr);
        } else if (typeof mPtr === "string") {
            this.instancePtr = ptr(mPtr);
        } else {
            this.instancePtr = mPtr;
        }

        // 解析 classHandle
        if (classHandle !== undefined && classHandle !== null && classHandle !== 0 && classHandle !== "" && classHandle !== "undefined") {
            let clsPtr: NativePointer;
            if (typeof classHandle === "number") {
                clsPtr = ptr(classHandle);
            } else if (typeof classHandle === "string") {
                clsPtr = ptr(classHandle);
            } else {
                clsPtr = classHandle;
            }
            
            if (!clsPtr.isNull()) {
                this.klass = new Il2Cpp.Class(clsPtr);
                this.isInstance = !this.instancePtr.isNull();
            } else {
                // classHandle 无效，尝试从实例获取
                this.initFromInstance();
            }
        } else {
            // 没有提供 classHandle，尝试从实例获取类
            this.initFromInstance();
        }
    }
    
    /**
     * 从实例指针初始化类信息
     */
    private initFromInstance(): void {
        if (this.instancePtr.isNull()) {
            throw new Error("Instance pointer is null and no class handle provided");
        }
        
        try {
            const obj = new Il2Cpp.Object(this.instancePtr);
            this.klass = obj.class;
            // 验证类是否有效
            const _ = this.klass.name;
            this.isInstance = true;
        } catch (e) {
            throw new Error(`Failed to get class from instance: ${e}`);
        }
    }

    /**
     * 获取字段实例
     */
    getFieldInstance(fieldName: string): Il2Cpp.Field | null | undefined {
        try {
            return this.klass?.field(fieldName);
        } catch {
            return null;
        }
    }

    /**
     * 获取字段值（指针）
     */
    getFieldValue(fieldName: string): NativePointer {
        if (!this.isInstance || this.instancePtr.isNull()) return ptr(0);
        try {
            const field = this.getFieldInstance(fieldName);
            if (!field) return ptr(0);
            if (field.isStatic) return getStaticFieldValue(field);
            return this.instancePtr.add(field.offset).readPointer();
        } catch {
            return ptr(0);
        }
    }

    /**
     * 获取字段偏移
     */
    getFieldOffset(fieldName: string): number {
        const field = this.getFieldInstance(fieldName);
        return field ? field.offset : -1;
    }

    /**
     * 解析单个字段
     */
    private parseField(field: Il2Cpp.Field, index: number): FieldInfo {
        const info: FieldInfo = {
            index,
            name: field.name,
            offset: field.offset,
            type_name: field.type.name,
            type_handle: field.type.handle.toString(),
            class_handle: field.type.class.handle.toString(),
            modifier: getFieldModifier(field.flags),
            is_static: field.isStatic,
            is_literal: field.isLiteral
        };

        // 解析值
        if (this.isInstance && !this.instancePtr.isNull()) {
            try {
                if (field.isStatic) {
                    const staticValue = getStaticFieldValue(field);
                    info.value_handle = staticValue.toString();
                    info.value = resolveTypeValue(field.type, staticValue);
                } else if (!field.isLiteral) {
                    const valueHandle = this.instancePtr.add(field.offset);
                    const valuePtr = valueHandle.readPointer();
                    info.value_handle = valuePtr.toString();
                    
                    // 根据类型解析值
                    if (field.type.class.isValueType && !field.type.class.isEnum) {
                        // 值类型直接使用地址
                        info.value = resolveTypeValue(field.type, valueHandle);
                    } else {
                        info.value = resolveTypeValue(field.type, valuePtr);
                    }
                }
            } catch (e) {
                info.value = `<error: ${e}>`;
            }
        } else if (field.isStatic) {
            // 非实例模式下也可以读取静态字段
            try {
                const staticValue = getStaticFieldValue(field);
                info.value_handle = staticValue.toString();
                info.value = resolveTypeValue(field.type, staticValue);
            } catch (e) {
                info.value = `<error: ${e}>`;
            }
        }

        return info;
    }

    /**
     * 解析所有字段（lfs 功能）
     */
    parseFields(): InstanceFieldsResult {
        const fields: FieldInfo[] = [];
        
        const sortedFields = [...this.klass!.fields].sort((a, b) => a.offset - b.offset);
        
        sortedFields.forEach((field, index) => {
            fields.push(this.parseField(field, index));
        });

        return {
            instance_handle: this.instancePtr.toString(),
            class_name: this.klass!.name,
            class_handle: this.klass!.handle.toString(),
            namespace: this.klass!.namespace || "[No Namespace]",
            field_count: fields.length,
            fields
        };
    }

    /**
     * 转换为字符串（lfss 功能）
     */
    toString(): string {
        if (!this.isInstance || this.instancePtr.isNull()) return "";
        
        const result: Record<string, string> = {};
        
        const sortedFields = [...this.klass!.fields].sort((a, b) => a.offset - b.offset);
        
        for (const field of sortedFields) {
            if (!field.isStatic && !field.isLiteral) {
                try {
                    const valuePtr = this.instancePtr.add(field.offset).readPointer();
                    result[field.name] = valuePtr.toString();
                } catch {
                    result[field.name] = "null";
                }
            }
        }
        
        return JSON.stringify(result);
    }
}

/**
 * 获取类的父类链
 */
export function getParentClasses(klass: Il2Cpp.Class): Il2Cpp.Class[] {
    const parents: Il2Cpp.Class[] = [];
    let current = klass;
    
    const maxDepth = 20;
    for (let i = 0; i < maxDepth; i++) {
        parents.push(current);
        try {
            const parent = current.parent;
            if (!parent || parent.handle.isNull() || parent.name === "Object") {
                break;
            }
            current = parent;
        } catch {
            break;
        }
    }
    
    return parents;
}

/**
 * 解析实例的所有父类字段（lfp 功能）
 */
export function parseFieldsWithParents(mPtr: NativePointer | string | number): ParentChainResult {
    const instancePtr = typeof mPtr === "string" ? ptr(mPtr) : 
                        typeof mPtr === "number" ? ptr(mPtr) : mPtr;
    
    let klass: Il2Cpp.Class;
    try {
        klass = new Il2Cpp.Object(instancePtr).class;
    } catch {
        throw new Error("Invalid instance pointer");
    }
    
    const parentClasses = getParentClasses(klass);
    const classChain: ParentChainResult["class_chain"] = [];
    
    for (const cls of parentClasses) {
        const parser = new FieldParser(instancePtr, cls.handle);
        const result = parser.parseFields();
        
        classChain.push({
            class_name: cls.name,
            class_handle: cls.handle.toString(),
            namespace: cls.namespace || "[No Namespace]",
            fields: result.fields
        });
    }
    
    return {
        instance_handle: instancePtr.toString(),
        class_chain: classChain
    };
}
