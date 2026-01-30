import "frida-il2cpp-bridge"
import { Il2CppCache } from "../core/il2cpp-helper"
import { getMethodModifier } from "../core/method-utils"
import { findClass } from "../core/class-finder"

/**
 * 方法服务 - 处理 IL2CPP Method 相关操作
 */
export class MethodService {
    /**
     * 列出指定类的所有方法
     */
    static listMethods(classNameOrPtr: string | NativePointer): any[] {
        let klass: Il2Cpp.Class;

        if (typeof classNameOrPtr === "string") {
            if (classNameOrPtr.startsWith("0x")) {
                klass = new Il2Cpp.Class(ptr(classNameOrPtr));
            } else {
                const classPtr = findClass(classNameOrPtr);
                if (classPtr.isNull()) {
                    throw new Error(`Class not found: ${classNameOrPtr}`);
                }
                klass = new Il2Cpp.Class(classPtr);
            }
        } else {
            klass = new Il2Cpp.Class(classNameOrPtr);
        }

        return klass.methods.map((method) => ({
            handle: method.handle.toString(),
            name: method.name,
            virtual_address: method.virtualAddress.toString(),
            relative_virtual_address: method.relativeVirtualAddress.toString(),
            parameter_count: method.parameterCount,
            return_type: method.returnType.name,
            class_name: klass.name,
            is_generic: method.isGeneric,
            is_static: method.isStatic,
            modifier: getMethodModifier(method)
        }));
    }

    /**
     * 查找方法（支持模糊匹配）
     */
    static findMethods(filter: string, findAll: boolean = true, accurate: boolean = false): any[] {
        const result: any[] = [];

        if (findAll) {
            const methods = Il2CppCache.methods
                .filter((item) => 
                    accurate ? item.name === filter : item.name.toLowerCase().includes(filter.toLowerCase())
                );

            for (const method of methods) {
                result.push({
                    handle: method.handle.toString(),
                    virtual_address: method.virtualAddress.toString(),
                    relative_virtual_address: method.relativeVirtualAddress.toString(),
                    name: method.name,
                    class_name: method.class.name,
                    class_handle: method.class.handle.toString(),
                    namespace: method.class.namespace || "[No Namespace]",
                    assembly_name: method.class.image.assembly.name,
                    modifier: getMethodModifier(method),
                    return_type: method.returnType.name,
                    parameter_count: method.parameterCount
                });
            }
        } else {
            // 只搜索常用类
            const commonClasses = ["Transform", "GameObject", "Application", "Input", "PlayerPrefs", "Object"];
            for (const className of commonClasses) {
                try {
                    const classPtr = findClass(className);
                    if (!classPtr.isNull()) {
                        const klass = new Il2Cpp.Class(classPtr);
                        for (const method of klass.methods) {
                            if (method.name.toLowerCase().includes(filter.toLowerCase())) {
                                result.push({
                                    handle: method.handle.toString(),
                                    virtual_address: method.virtualAddress.toString(),
                                    relative_virtual_address: method.relativeVirtualAddress.toString(),
                                    name: method.name,
                                    class_name: klass.name,
                                    class_handle: klass.handle.toString(),
                                    namespace: klass.namespace || "[No Namespace]",
                                    assembly_name: klass.image.assembly.name,
                                    modifier: getMethodModifier(method),
                                    return_type: method.returnType.name,
                                    parameter_count: method.parameterCount
                                });
                            }
                        }
                    }
                } catch (e) {
                    // 忽略找不到的类
                }
            }
        }

        return result;
    }

    /**
     * 查看方法详细信息
     */
    static showMethod(methodPtr: string | NativePointer): any {
        let mPtr: NativePointer;

        if (typeof methodPtr === "string") {
            if (methodPtr.startsWith("0x")) {
                mPtr = ptr(methodPtr);
            } else {
                throw new Error("Invalid pointer format");
            }
        } else {
            mPtr = methodPtr;
        }

        const method = new Il2Cpp.Method(mPtr);
        
        const parameters = method.parameters.map((param) => ({
            name: param.name,
            type: param.type.name,
            type_handle: param.type.handle.toString(),
            class_handle: param.type.class.handle.toString()
        }));

        return {
            handle: method.handle.toString(),
            name: method.name,
            virtual_address: method.virtualAddress.toString(),
            relative_virtual_address: method.relativeVirtualAddress.toString(),
            class: {
                name: method.class.name,
                handle: method.class.handle.toString(),
                namespace: method.class.namespace,
                method_count: method.class.methods.length,
                field_count: method.class.fields.length
            },
            image: {
                name: method.class.image.name,
                handle: method.class.image.handle.toString(),
                class_count: method.class.image.classCount
            },
            assembly: {
                name: method.class.image.assembly.name,
                handle: method.class.image.assembly.handle.toString()
            },
            parameters: parameters,
            return_type: {
                name: method.returnType.name,
                handle: method.returnType.handle.toString(),
                class_handle: method.returnType.class.handle.toString()
            },
            is_generic: method.isGeneric,
            is_static: method.isStatic,
            parameter_count: method.parameterCount,
            modifier: getMethodModifier(method)
        };
    }
}
