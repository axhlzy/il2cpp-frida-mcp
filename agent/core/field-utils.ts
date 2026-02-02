/**
 * 字段修饰符常量和工具函数
 */

const FIELD_ATTRIBUTE = {
    FIELD_ACCESS_MASK: 0x0007,
    PRIVATE: 0x0001,
    FAM_AND_ASSEM: 0x0002,
    ASSEMBLY: 0x0003,
    FAMILY: 0x0004,
    FAM_OR_ASSEM: 0x0005,
    PUBLIC: 0x0006,
    STATIC: 0x0010,
    INIT_ONLY: 0x0020,
    LITERAL: 0x0040,
    NOT_SERIALIZED: 0x0080,
    SPECIAL_NAME: 0x0200,
    PINVOKE_IMPL: 0x2000,
};

/**
 * 获取字段修饰符字符串
 */
export function getFieldModifier(flags: number): string {
    const access = flags & FIELD_ATTRIBUTE.FIELD_ACCESS_MASK;
    let modifier = "";

    // Access modifiers
    switch (access) {
        case FIELD_ATTRIBUTE.PRIVATE:
            modifier += "private ";
            break;
        case FIELD_ATTRIBUTE.PUBLIC:
            modifier += "public ";
            break;
        case FIELD_ATTRIBUTE.FAMILY:
            modifier += "protected ";
            break;
        case FIELD_ATTRIBUTE.ASSEMBLY:
        case FIELD_ATTRIBUTE.FAM_AND_ASSEM:
            modifier += "internal ";
            break;
        case FIELD_ATTRIBUTE.FAM_OR_ASSEM:
            modifier += "protected internal ";
            break;
    }

    // Static modifier
    if (flags & FIELD_ATTRIBUTE.STATIC) {
        modifier += "static ";
    }

    // Readonly modifier
    if (flags & FIELD_ATTRIBUTE.INIT_ONLY) {
        modifier += "readonly ";
    }

    // Const modifier
    if (flags & FIELD_ATTRIBUTE.LITERAL) {
        modifier += "const ";
    }

    return modifier.trim();
}
