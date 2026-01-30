import "frida-il2cpp-bridge"

/**
 * 查找类（支持两种格式）
 * - 带命名空间: "UnityEngine.Application" 或 "UnityEngine.Android.AndroidApplication"
 * - 指针地址: "0x7cd12bdf20"
 * 
 * 注意：不支持单独类名（如 "Application"），因为可能导致重名冲突
 */
export function findClass(searchClassName: string): NativePointer {
    // 如果是指针地址，直接返回
    if (searchClassName.startsWith("0x")) {
        return ptr(searchClassName);
    }
    
    // 必须包含命名空间（包含点号）
    if (!searchClassName.includes(".")) {
        throw new Error(`请使用完整的类名格式: Namespace.ClassName 或类的 handle 地址。例如: UnityEngine.Application 或 0x7cd12bdf20`);
    }
    
    const assemblies = Il2Cpp.domain.assemblies;
    
    // 解析命名空间和类名
    const lastDotIndex = searchClassName.lastIndexOf(".");
    const targetNamespace = searchClassName.substring(0, lastDotIndex);
    const targetClassName = searchClassName.substring(lastDotIndex + 1);
    
    // 精确匹配命名空间和类名
    for (const assembly of assemblies) {
        for (const klass of assembly.image.classes) {
            if (klass.name === targetClassName && klass.namespace === targetNamespace) {
                return klass.handle;
            }
        }
    }

    return ptr(0);
}
