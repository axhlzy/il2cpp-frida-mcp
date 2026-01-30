/**
 * 方法修饰符常量
 */
const METHOD_ATTRIBUTE = {
    MEMBER_ACCESS_MASK: 0x0007,
    PRIVATE: 0x0001,
    PUBLIC: 0x0006,
    FAMILY: 0x0004,
    ASSEM: 0x0003,
    FAM_AND_ASSEM: 0x0002,
    FAM_OR_ASSEM: 0x0005,
    STATIC: 0x0010,
    FINAL: 0x0020,
    VIRTUAL: 0x0040,
    ABSTRACT: 0x0400,
    PINVOKE_IMPL: 0x2000,
    VTABLE_LAYOUT_MASK: 0x0100,
    REUSE_SLOT: 0x0000,
    NEW_SLOT: 0x0100,
};

/**
 * 获取方法修饰符字符串
 */
export function getMethodModifier(method: Il2Cpp.Method): string {
    const flags = method.flags;
    const access = flags & METHOD_ATTRIBUTE.MEMBER_ACCESS_MASK;
    let modifier = "";

    // Access modifiers
    switch (access) {
        case METHOD_ATTRIBUTE.PRIVATE:
            modifier += "private ";
            break;
        case METHOD_ATTRIBUTE.PUBLIC:
            modifier += "public ";
            break;
        case METHOD_ATTRIBUTE.FAMILY:
            modifier += "protected ";
            break;
        case METHOD_ATTRIBUTE.ASSEM:
        case METHOD_ATTRIBUTE.FAM_AND_ASSEM:
            modifier += "internal ";
            break;
        case METHOD_ATTRIBUTE.FAM_OR_ASSEM:
            modifier += "protected internal ";
            break;
    }

    // Static modifier
    if (flags & METHOD_ATTRIBUTE.STATIC) {
        modifier += "static ";
    }

    // Virtual/Abstract/Override modifiers
    if (flags & METHOD_ATTRIBUTE.ABSTRACT) {
        modifier += "abstract ";
        if ((flags & METHOD_ATTRIBUTE.VTABLE_LAYOUT_MASK) === METHOD_ATTRIBUTE.REUSE_SLOT) {
            modifier += "override ";
        }
    } else if (flags & METHOD_ATTRIBUTE.FINAL) {
        if ((flags & METHOD_ATTRIBUTE.VTABLE_LAYOUT_MASK) === METHOD_ATTRIBUTE.REUSE_SLOT) {
            modifier += "sealed override ";
        }
    } else if (flags & METHOD_ATTRIBUTE.VIRTUAL) {
        if ((flags & METHOD_ATTRIBUTE.VTABLE_LAYOUT_MASK) === METHOD_ATTRIBUTE.NEW_SLOT) {
            modifier += "virtual ";
        } else {
            modifier += "override ";
        }
    }

    // Extern modifier
    if (flags & METHOD_ATTRIBUTE.PINVOKE_IMPL) {
        modifier += "extern ";
    }

    return modifier.trim();
}
