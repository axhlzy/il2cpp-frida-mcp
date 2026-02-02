/**
 * 实例解析服务
 * 提供 lfs, lfp, lfss, lft, lfv, lfo 等功能的 RPC 接口
 */

import "frida-il2cpp-bridge";
import { FieldParser, parseFieldsWithParents, InstanceFieldsResult, ParentChainResult } from "../core/field-parser";
import { findClass } from "../core/class-finder";

/**
 * 实例服务 - 处理 IL2CPP 实例解析相关操作
 */
export class InstanceService {
    /**
     * 解析实例的所有字段 (lfs)
     * @param instancePtr 实例指针
     * @param classHandle 可选的类句柄
     */
    static listFields(instancePtr: string, classHandle?: string): InstanceFieldsResult {
        const parser = new FieldParser(instancePtr, classHandle);
        return parser.parseFields();
    }

    /**
     * 解析实例的所有字段（包含父类）(lfp)
     * @param instancePtr 实例指针
     */
    static listFieldsWithParents(instancePtr: string): ParentChainResult {
        return parseFieldsWithParents(instancePtr);
    }

    /**
     * 获取实例字段的字符串表示 (lfss)
     * @param instancePtr 实例指针
     * @param classHandle 可选的类句柄
     */
    static fieldsToString(instancePtr: string, classHandle?: string): string {
        const parser = new FieldParser(instancePtr, classHandle);
        return parser.toString();
    }

    /**
     * 获取字段类型信息 (lft)
     * @param instancePtr 实例指针
     * @param fieldName 字段名
     * @param classHandle 可选的类句柄
     */
    static getFieldType(instancePtr: string, fieldName: string, classHandle?: string): any {
        const parser = new FieldParser(instancePtr, classHandle);
        const field = parser.getFieldInstance(fieldName);
        
        if (!field) {
            return { error: `Field not found: ${fieldName}` };
        }

        return {
            name: field.name,
            offset: field.offset,
            type_name: field.type.name,
            type_handle: field.type.handle.toString(),
            class_name: field.type.class.name,
            class_handle: field.type.class.handle.toString(),
            is_static: field.isStatic,
            is_literal: field.isLiteral,
            is_value_type: field.type.class.isValueType,
            is_enum: field.type.class.isEnum
        };
    }

    /**
     * 获取字段值 (lfv)
     * @param instancePtr 实例指针
     * @param fieldName 字段名
     * @param classHandle 可选的类句柄
     */
    static getFieldValue(instancePtr: string, fieldName: string, classHandle?: string): any {
        const parser = new FieldParser(instancePtr, classHandle);
        const valuePtr = parser.getFieldValue(fieldName);
        
        return {
            field_name: fieldName,
            value_handle: valuePtr.toString(),
            is_null: valuePtr.isNull()
        };
    }

    /**
     * 获取字段偏移 (lfo)
     * @param instancePtr 实例指针
     * @param fieldName 字段名
     * @param classHandle 可选的类句柄
     */
    static getFieldOffset(instancePtr: string, fieldName: string, classHandle?: string): any {
        const parser = new FieldParser(instancePtr, classHandle);
        const offset = parser.getFieldOffset(fieldName);
        
        return {
            field_name: fieldName,
            offset: offset,
            offset_hex: offset >= 0 ? `0x${offset.toString(16)}` : "not found"
        };
    }

    /**
     * 获取实例的类型信息
     * @param instancePtr 实例指针
     */
    static getInstanceType(instancePtr: string): any {
        try {
            const obj = new Il2Cpp.Object(ptr(instancePtr));
            const klass = obj.class;
            
            return {
                instance_handle: instancePtr,
                class_name: klass.name,
                class_handle: klass.handle.toString(),
                namespace: klass.namespace || "[No Namespace]",
                assembly_name: klass.image.assembly.name,
                image_name: klass.image.name,
                is_value_type: klass.isValueType,
                is_enum: klass.isEnum,
                is_abstract: klass.isAbstract,
                field_count: klass.fields.length,
                method_count: klass.methods.length
            };
        } catch (e) {
            return { error: `Failed to get instance type: ${e}` };
        }
    }

    /**
     * 获取实例的父类链
     * @param instancePtr 实例指针
     */
    static getTypeParents(instancePtr: string): any {
        try {
            const obj = new Il2Cpp.Object(ptr(instancePtr));
            let klass = obj.class;
            const parents: any[] = [];
            
            const maxDepth = 20;
            for (let i = 0; i < maxDepth; i++) {
                parents.push({
                    class_name: klass.name,
                    class_handle: klass.handle.toString(),
                    namespace: klass.namespace || "[No Namespace]"
                });
                
                try {
                    const parent = klass.parent;
                    if (!parent || parent.handle.isNull()) break;
                    klass = parent;
                } catch {
                    break;
                }
            }
            
            return {
                instance_handle: instancePtr,
                parent_chain: parents
            };
        } catch (e) {
            return { error: `Failed to get type parents: ${e}` };
        }
    }

    /**
     * 列出实例的所有方法 (lms)
     * @param instancePtr 实例指针
     */
    static listInstanceMethods(instancePtr: string): any[] {
        try {
            const obj = new Il2Cpp.Object(ptr(instancePtr));
            const klass = obj.class;
            
            return klass.methods.map((method, index) => ({
                index,
                handle: method.handle.toString(),
                name: method.name,
                virtual_address: method.virtualAddress.toString(),
                relative_virtual_address: method.relativeVirtualAddress.toString(),
                return_type: method.returnType.name,
                parameter_count: method.parameterCount,
                is_static: method.isStatic,
                is_generic: method.isGeneric
            }));
        } catch (e) {
            return [{ error: `Failed to list methods: ${e}` }];
        }
    }

    /**
     * 读取实例指定偏移的值
     * @param instancePtr 实例指针
     * @param offset 偏移量
     * @param size 读取大小 (1, 2, 4, 8)
     */
    static readAtOffset(instancePtr: string, offset: number, size: number = 8): any {
        try {
            const ptr_instance = ptr(instancePtr);
            const addr = ptr_instance.add(offset);
            
            let value: any;
            switch (size) {
                case 1:
                    value = addr.readU8();
                    break;
                case 2:
                    value = addr.readU16();
                    break;
                case 4:
                    value = addr.readU32();
                    break;
                case 8:
                default:
                    value = addr.readPointer().toString();
                    break;
            }
            
            return {
                instance_handle: instancePtr,
                offset: offset,
                offset_hex: `0x${offset.toString(16)}`,
                address: addr.toString(),
                size: size,
                value: value
            };
        } catch (e) {
            return { error: `Failed to read at offset: ${e}` };
        }
    }

    /**
     * 设置实例字段值
     * @param instancePtr 实例指针
     * @param fieldName 字段名
     * @param value 新值（指针字符串）
     * @param classHandle 可选的类句柄
     */
    static setFieldValue(instancePtr: string, fieldName: string, value: string, classHandle?: string): any {
        try {
            const parser = new FieldParser(instancePtr, classHandle);
            const field = parser.getFieldInstance(fieldName);
            
            if (!field) {
                return { error: `Field not found: ${fieldName}` };
            }
            
            if (field.isStatic || field.isLiteral) {
                return { error: `Cannot set static or literal field: ${fieldName}` };
            }
            
            const instance = ptr(instancePtr);
            const newValue = ptr(value);
            const fieldAddr = instance.add(field.offset);
            
            fieldAddr.writePointer(newValue);
            
            return {
                success: true,
                field_name: fieldName,
                field_offset: field.offset,
                new_value: newValue.toString()
            };
        } catch (e) {
            return { error: `Failed to set field value: ${e}` };
        }
    }
}
