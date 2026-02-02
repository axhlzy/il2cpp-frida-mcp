/**
 * Unity 相关服务
 * 提供 GameObject、Transform、SendMessage 等功能
 */

import "frida-il2cpp-bridge";
import { findClass } from "../core/class-finder";

/**
 * Unity 服务 - 处理 Unity 相关操作
 */
export class UnityService {
    /**
     * 获取 Transform
     * @param instancePtr 实例指针 (GameObject 或 Component)
     */
    static getTransform(instancePtr: string): any {
        try {
            const ptr_instance = ptr(instancePtr);
            const obj = new Il2Cpp.Object(ptr_instance);
            const typeName = obj.class.name;
            
            // 通过 Il2Cpp.Object 调用非静态方法
            const getTransformMethod = obj.tryMethod("get_transform");
            if (!getTransformMethod) {
                return { error: "Cannot find get_transform method" };
            }
            
            const transform = getTransformMethod.invoke() as Il2Cpp.Object;
            
            if (!transform || transform.handle.isNull()) {
                return { error: "Transform is null" };
            }
            
            return {
                instance_handle: instancePtr,
                transform_handle: transform.handle.toString(),
                type: typeName
            };
        } catch (e) {
            return { error: `Failed to get transform: ${e}` };
        }
    }

    /**
     * 获取 GameObject
     * @param instancePtr 实例指针 (Transform 或 Component)
     */
    static getGameObject(instancePtr: string): any {
        try {
            const ptr_instance = ptr(instancePtr);
            const obj = new Il2Cpp.Object(ptr_instance);
            const typeName = obj.class.name;
            
            let gobjObj: Il2Cpp.Object;
            
            if (typeName === "GameObject") {
                gobjObj = obj;
            } else {
                // Component.get_gameObject() - 通过 Il2Cpp.Object 调用
                const getGameObjectMethod = obj.tryMethod("get_gameObject");
                if (!getGameObjectMethod) {
                    return { error: "Cannot find get_gameObject method" };
                }
                const result = getGameObjectMethod.invoke() as Il2Cpp.Object;
                if (!result || result.handle.isNull()) {
                    return { error: "GameObject is null" };
                }
                gobjObj = result;
            }
            
            // 获取 GameObject 的基本信息
            let name = "";
            let layer = 0;
            let activeSelf = false;
            
            try {
                const getNameMethod = gobjObj.tryMethod("get_name");
                if (getNameMethod) {
                    const nameResult = getNameMethod.invoke() as Il2Cpp.String;
                    if (nameResult && !nameResult.handle.isNull()) {
                        name = nameResult.content || "";
                    }
                }
            } catch {}
            
            try {
                const getLayerMethod = gobjObj.tryMethod("get_layer");
                if (getLayerMethod) {
                    layer = getLayerMethod.invoke() as number;
                }
            } catch {}
            
            try {
                const getActiveMethod = gobjObj.tryMethod("get_activeSelf");
                if (getActiveMethod) {
                    activeSelf = getActiveMethod.invoke() as boolean;
                }
            } catch {}
            
            return {
                instance_handle: instancePtr,
                gameobject_handle: gobjObj.handle.toString(),
                name: name,
                layer: layer,
                active_self: activeSelf,
                source_type: typeName
            };
        } catch (e) {
            return { error: `Failed to get gameObject: ${e}` };
        }
    }

    /**
     * 获取 Transform 的子对象
     * @param transformPtr Transform 指针
     */
    static getChildren(transformPtr: string): any {
        try {
            const ptr_transform = ptr(transformPtr);
            const transformObj = new Il2Cpp.Object(ptr_transform);
            
            // 获取子对象数量 - 通过 Il2Cpp.Object 调用
            const getChildCountMethod = transformObj.tryMethod("get_childCount");
            if (!getChildCountMethod) {
                return { error: "Cannot find get_childCount method" };
            }
            
            const childCount = getChildCountMethod.invoke() as number;
            
            // 获取 GetChild 方法
            const getChildMethod = transformObj.tryMethod("GetChild", 1);
            if (!getChildMethod) {
                return { error: "Cannot find GetChild method" };
            }
            
            const children: any[] = [];
            
            for (let i = 0; i < childCount; i++) {
                try {
                    const childTransform = getChildMethod.invoke(i) as Il2Cpp.Object;
                    if (childTransform && !childTransform.handle.isNull()) {
                        // 获取子对象的 GameObject 名称
                        let childName = "";
                        try {
                            const getGameObjectMethod = childTransform.tryMethod("get_gameObject");
                            if (getGameObjectMethod) {
                                const childGameObject = getGameObjectMethod.invoke() as Il2Cpp.Object;
                                if (childGameObject && !childGameObject.handle.isNull()) {
                                    const getNameMethod = childGameObject.tryMethod("get_name");
                                    if (getNameMethod) {
                                        const nameResult = getNameMethod.invoke() as Il2Cpp.String;
                                        if (nameResult && !nameResult.handle.isNull()) {
                                            childName = nameResult.content || "";
                                        }
                                    }
                                }
                            }
                        } catch {}
                        
                        children.push({
                            index: i,
                            transform_handle: childTransform.handle.toString(),
                            name: childName
                        });
                    }
                } catch {}
            }
            
            return {
                transform_handle: transformPtr,
                child_count: childCount,
                children: children
            };
        } catch (e) {
            return { error: `Failed to get children: ${e}` };
        }
    }

    /**
     * 获取 Transform 的父对象
     * @param transformPtr Transform 指针
     */
    static getParent(transformPtr: string): any {
        try {
            const ptr_transform = ptr(transformPtr);
            const transformObj = new Il2Cpp.Object(ptr_transform);
            
            const getParentMethod = transformObj.tryMethod("get_parent");
            if (!getParentMethod) {
                return { error: "Cannot find get_parent method" };
            }
            
            const parentTransform = getParentMethod.invoke() as Il2Cpp.Object;
            
            if (!parentTransform || parentTransform.handle.isNull()) {
                return {
                    transform_handle: transformPtr,
                    parent_handle: "null",
                    is_root: true
                };
            }
            
            // 获取父对象名称
            let parentName = "";
            try {
                const getGameObjectMethod = parentTransform.tryMethod("get_gameObject");
                if (getGameObjectMethod) {
                    const parentGameObject = getGameObjectMethod.invoke() as Il2Cpp.Object;
                    if (parentGameObject && !parentGameObject.handle.isNull()) {
                        const getNameMethod = parentGameObject.tryMethod("get_name");
                        if (getNameMethod) {
                            const nameResult = getNameMethod.invoke() as Il2Cpp.String;
                            if (nameResult && !nameResult.handle.isNull()) {
                                parentName = nameResult.content || "";
                            }
                        }
                    }
                }
            } catch {}
            
            return {
                transform_handle: transformPtr,
                parent_handle: parentTransform.handle.toString(),
                parent_name: parentName,
                is_root: false
            };
        } catch (e) {
            return { error: `Failed to get parent: ${e}` };
        }
    }

    /**
     * 获取 Transform 的层级路径
     * @param transformPtr Transform 指针
     * @param maxDepth 最大深度
     */
    static getHierarchy(transformPtr: string, maxDepth: number = 10): any {
        try {
            const ptr_transform = ptr(transformPtr);
            const hierarchy: any[] = [];
            let currentObj = new Il2Cpp.Object(ptr_transform);
            
            for (let i = 0; i < maxDepth; i++) {
                if (!currentObj || currentObj.handle.isNull()) break;
                
                // 获取 GameObject 名称
                let name = "";
                try {
                    const getGameObjectMethod = currentObj.tryMethod("get_gameObject");
                    if (getGameObjectMethod) {
                        const gameObject = getGameObjectMethod.invoke() as Il2Cpp.Object;
                        if (gameObject && !gameObject.handle.isNull()) {
                            const getNameMethod = gameObject.tryMethod("get_name");
                            if (getNameMethod) {
                                const nameResult = getNameMethod.invoke() as Il2Cpp.String;
                                if (nameResult && !nameResult.handle.isNull()) {
                                    name = nameResult.content || "";
                                }
                            }
                        }
                    }
                } catch {}
                
                hierarchy.push({
                    depth: i,
                    transform_handle: currentObj.handle.toString(),
                    name: name
                });
                
                // 获取父对象
                const getParentMethod = currentObj.tryMethod("get_parent");
                if (!getParentMethod) break;
                
                const parentResult = getParentMethod.invoke() as Il2Cpp.Object;
                if (!parentResult || parentResult.handle.isNull()) break;
                currentObj = parentResult;
            }
            
            // 构建路径字符串
            const pathStr = hierarchy.map(h => h.name).reverse().join("/");
            
            return {
                transform_handle: transformPtr,
                hierarchy: hierarchy,
                path: pathStr
            };
        } catch (e) {
            return { error: `Failed to get hierarchy: ${e}` };
        }
    }

    /**
     * 调用 UnitySendMessage
     * @param gameObjectName GameObject 名称
     * @param methodName 方法名
     * @param message 消息
     */
    static sendMessage(gameObjectName: string, methodName: string, message: string): any {
        try {
            // 尝试多种方式找到 UnitySendMessage
            let sendMsgAddr: NativePointer | null = null;
            
            // 方式1: 从 libunity.so 查找
            try {
                sendMsgAddr = Process.findModuleByName("libunity.so")?.findExportByName("UnitySendMessage")!;
            } catch {}
            
            // 方式2: 从 libil2cpp.so 查找
            if (!sendMsgAddr || sendMsgAddr.isNull()) {
                try {
                    sendMsgAddr = sendMsgAddr = Process.findModuleByName("libunity.so")?.findExportByName("UnitySendMessage")!;
                } catch {}
            }
            
            // 方式3: 遍历所有模块查找
            if (!sendMsgAddr || sendMsgAddr.isNull()) {
                try {
                    const modules = Process.enumerateModules();
                    for (const mod of modules) {
                        if (mod.name.toLowerCase().includes("unity") || mod.name.toLowerCase().includes("il2cpp")) {
                            const addr = mod.findExportByName("UnitySendMessage");
                            if (addr && !addr.isNull()) {
                                sendMsgAddr = addr;
                                break;
                            }
                        }
                    }
                } catch {}
            }
            
            if (!sendMsgAddr || sendMsgAddr.isNull()) {
                return { error: "Cannot find UnitySendMessage function in any module" };
            }
            
            const sendMsgFunc = new NativeFunction(sendMsgAddr, "void", ["pointer", "pointer", "pointer"]);
            
            const gameObjectNamePtr = Memory.allocUtf8String(gameObjectName);
            const methodNamePtr = Memory.allocUtf8String(methodName);
            const messagePtr = Memory.allocUtf8String(message);
            
            sendMsgFunc(gameObjectNamePtr, methodNamePtr, messagePtr);

            return {
                success: true,
                gameobject_name: gameObjectName,
                method_name: methodName,
                message: message
            };
        } catch (e) {
            return { error: `Failed to send message: ${e}` };
        }
    }

    /**
     * 查找 GameObject
     * @param path GameObject 路径
     */
    static findGameObject(path: string): any {
        try {
            // 查找 GameObject.Find 方法
            const gameObjectClass = findClass("UnityEngine.GameObject");
            if (gameObjectClass.isNull()) {
                return { error: "Cannot find GameObject class" };
            }
            
            const klass = new Il2Cpp.Class(gameObjectClass);
            const findMethod = klass.tryMethod("Find", 1);
            
            if (!findMethod) {
                return { error: "Cannot find GameObject.Find method" };
            }
            
            // 创建 IL2CPP 字符串
            const pathStr = Il2Cpp.string(path);
            const result = findMethod.invoke(pathStr) as Il2Cpp.Object;
            
            if (!result || result.handle.isNull()) {
                return { error: `GameObject not found: ${path}` };
            }
            
            // 获取 GameObject 信息
            let name = "";
            let layer = 0;
            
            try {
                const getNameMethod = result.tryMethod("get_name");
                if (getNameMethod) {
                    const nameResult = getNameMethod.invoke() as Il2Cpp.String;
                    if (nameResult && !nameResult.handle.isNull()) {
                        name = nameResult.content || "";
                    }
                }
            } catch {}
            
            try {
                const getLayerMethod = result.tryMethod("get_layer");
                if (getLayerMethod) {
                    layer = getLayerMethod.invoke() as number;
                }
            } catch {}
            
            return {
                path: path,
                gameobject_handle: result.handle.toString(),
                name: name,
                layer: layer
            };
        } catch (e) {
            return { error: `Failed to find gameObject: ${e}` };
        }
    }
}
