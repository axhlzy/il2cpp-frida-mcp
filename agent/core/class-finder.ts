import "frida-il2cpp-bridge"

/**
 * 默认优先搜索的 Assembly 列表
 */
const DEFAULT_ASSEMBLIES = ["Assembly-CSharp", "MaxSdk.Scripts", "mscorlib"];

/**
 * 查找类（内部方法）
 */
export function findClass(
    searchClassName: string, 
    fromAssembly: string[] = DEFAULT_ASSEMBLIES
): NativePointer {
    const assemblies = Il2Cpp.domain.assemblies;
    
    // 优先从指定的 assembly 中查找
    for (const assembly of assemblies) {
        if (fromAssembly.includes(assembly.name)) {
            for (const klass of assembly.image.classes) {
                if (klass.name === searchClassName) {
                    return klass.handle;
                }
            }
        }
    }

    // 从其他 assembly 中查找
    for (const assembly of assemblies) {
        if (!fromAssembly.includes(assembly.name)) {
            for (const klass of assembly.image.classes) {
                if (klass.name === searchClassName) {
                    return klass.handle;
                }
            }
        }
    }

    return ptr(0);
}
