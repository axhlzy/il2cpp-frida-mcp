import "frida-il2cpp-bridge"
import { Il2CppCache } from "../core/il2cpp-helper"

/**
 * 镜像服务 - 处理 IL2CPP Image 相关操作
 */
export class ImageService {
    /**
     * 列出所有 IL2CPP 镜像
     */
    static listImages(filter: string = "", sort: boolean = true): any[] {
        const images = Il2CppCache.images.filter((image) => {
            return filter !== "" ? image.name.indexOf(filter) !== -1 : true;
        });

        if (sort) {
            images.sort((first, second) => {
                return first.name.toLowerCase().charAt(0) > second.name.toLowerCase().charAt(0) ? 1 : -1;
            });
        }

        return images.map((image) => ({
            assembly_handle: image.assembly.handle.toString(),
            image_handle: image.handle.toString(),
            class_count: image.classCount,
            assembly_name: image.assembly.name,
            image_name: image.name
        }));
    }
}
