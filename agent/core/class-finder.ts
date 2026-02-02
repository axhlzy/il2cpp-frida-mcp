import "frida-il2cpp-bridge"

/**
 * Find class (supports multiple formats)
 * - With namespace: "UnityEngine.Application" or "UnityEngine.Android.AndroidApplication"
 * - Pointer address: "0x7cd12bdf20"
 * - Simple class name: "Application" (if no conflicts)
 * 
 * Returns class handle or throws error with conflict list if multiple matches found
 */
export function findClass(searchClassName: string): NativePointer {
    // If it's a pointer address, return directly
    if (searchClassName.startsWith("0x")) {
        return ptr(searchClassName);
    }
    
    const assemblies = Il2Cpp.domain.assemblies;
    
    // If contains namespace (has dot), do exact match
    if (searchClassName.includes(".")) {
        const lastDotIndex = searchClassName.lastIndexOf(".");
        const targetNamespace = searchClassName.substring(0, lastDotIndex);
        const targetClassName = searchClassName.substring(lastDotIndex + 1);
        
        // Exact match namespace and class name
        for (const assembly of assemblies) {
            for (const klass of assembly.image.classes) {
                if (klass.name === targetClassName && klass.namespace === targetNamespace) {
                    return klass.handle;
                }
            }
        }
        
        return ptr(0);
    }
    
    // Simple class name - search all classes
    const matches: Array<{namespace: string, name: string, handle: string}> = [];
    
    for (const assembly of assemblies) {
        for (const klass of assembly.image.classes) {
            if (klass.name === searchClassName) {
                matches.push({
                    namespace: klass.namespace || "",
                    name: klass.name,
                    handle: klass.handle.toString()
                });
            }
        }
    }
    
    if (matches.length === 0) {
        return ptr(0);
    }
    
    if (matches.length === 1) {
        return ptr(matches[0].handle);
    }
    
    // Multiple matches found - throw error with list
    let errorMsg = `Multiple classes found with name '${searchClassName}'. Please use full name:\n`;
    for (const match of matches) {
        const fullName = match.namespace ? `${match.namespace}.${match.name}` : match.name;
        errorMsg += `  - ${fullName} (handle: ${match.handle})\n`;
    }
    throw new Error(errorMsg);
}

