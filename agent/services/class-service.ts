import "frida-il2cpp-bridge"
import { Il2CppCache } from "../core/il2cpp-helper"

/**
 * 类服务 - 处理 IL2CPP Class 相关操作
 */
export class ClassService {
    /**
     * 列出指定 Image 的所有类
     */
    static listClasses(imageOrName: string, filterNameSpace: string = "", filterClassName: string = ""): any[] {
        let image: Il2Cpp.Image;
        
        try {
            if (imageOrName.startsWith("0x")) {
                image = new Il2Cpp.Image(ptr(imageOrName.trim()));
            } else {
                image = Il2Cpp.domain.assembly(imageOrName).image;
            }
        } catch (error) {
            throw new Error(`Image not found: ${imageOrName}`);
        }

        const result: any[] = [];
        const tMap = new Map<string, Il2Cpp.Class[]>();

        // 按 namespace 分组
        for (const klass of image.classes) {
            const key = klass.namespace || "[No Namespace]";
            if (!tMap.has(key)) {
                tMap.set(key, []);
            }
            tMap.get(key)!.push(klass);
        }

        for (const [namespace, classes] of tMap) {
            if (filterNameSpace && !namespace.toLowerCase().includes(filterNameSpace.toLowerCase())) {
                continue;
            }
            
            for (const klass of classes) {
                if (filterClassName && !klass.name.toLowerCase().includes(filterClassName.toLowerCase())) {
                    continue;
                }
                result.push({
                    handle: klass.handle.toString(),
                    name: klass.name,
                    namespace: namespace,
                    field_count: klass.fields.length,
                    method_count: klass.methods.length,
                    is_enum: klass.isEnum,
                    image_name: image.name
                });
            }
        }

        return result;
    }

    /**
     * 查找类（支持模糊匹配）
     */
    static findClasses(filterClassName: string, completeMatch: boolean = false): any[] {
        const localClasses = Il2CppCache.classes
            .filter((item) => 
                completeMatch ? item.name === filterClassName : item.name.toLowerCase().includes(filterClassName.toLowerCase())
            );

        return localClasses.map((item) => ({
            handle: item.handle.toString(),
            name: item.name,
            namespace: item.namespace || "[No Namespace]",
            assembly_name: item.image.assembly.name,
            image_name: item.image.name,
            method_count: item.methods.length,
            field_count: item.fields.length,
            is_enum: item.isEnum,
            is_abstract: item.isAbstract
        }));
    }
}
