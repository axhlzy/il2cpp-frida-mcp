/**
 * IL2CPP Frida Agent - 入口文件
 * 提供 RPC 接口供 MCP Server 调用
 */

import "frida-java-bridge"
import "frida-il2cpp-bridge"

import { ImageService } from "./services/image-service"
import { ClassService } from "./services/class-service"
import { MethodService } from "./services/method-service"
import { DisasmService } from "./services/disasm-service"
import { ModuleService } from "./services/module-service"
import { GCService } from "./services/gc-service"
import { ExecService } from "./services/exec-service"
import { InstanceService } from "./services/instance-service"
import { UnityService } from "./services/unity-service"
import { MemoryService } from "./services/memory-service"
import { AppService } from "./services/app-service"

// 导出给 Python 调用的 RPC 函数
rpc.exports = {
    // 镜像操作
    listImages: (filter: string = "", sort: boolean = true) => {
        return ImageService.listImages(filter, sort);
    },
    
    // 类操作
    listClasses: (imageOrName: string, filterNameSpace: string = "", filterClassName: string = "") => {
        return ClassService.listClasses(imageOrName, filterNameSpace, filterClassName);
    },
    
    findClasses: (filterClassName: string, completeMatch: boolean = false) => {
        return ClassService.findClasses(filterClassName, completeMatch);
    },
    
    // 方法操作
    listMethods: (classNameOrPtr: string) => {
        return MethodService.listMethods(classNameOrPtr);
    },
    
    findMethods: (filter: string, findAll: boolean = true, accurate: boolean = false) => {
        return MethodService.findMethods(filter, findAll, accurate);
    },
    
    showMethod: (methodPtr: string) => {
        return MethodService.showMethod(methodPtr);
    },
    
    // 反汇编
    showAsm: (methodPtr: string, instructionCount: number = 64, resolveFunctions: boolean = false) => {
        return DisasmService.showAsm(methodPtr, instructionCount, resolveFunctions);
    },
    
    // 模块操作
    findExport: (exportName: string, moduleName?: string) => {
        return ModuleService.findExport(exportName, moduleName);
    },
    
    findImport: (moduleName: string, importName?: string) => {
        return ModuleService.findImport(moduleName, importName);
    },
    
    // GC 操作
    gcChoose: (className: string, maxCount: number = 100) => {
        return GCService.gcChoose(className, maxCount);
    },
    
    gcInfo: () => {
        return GCService.gcInfo();
    },
    
    // 执行任意代码
    execJs: (code: string) => {
        return ExecService.execJs(code);
    },

    // ========== 实例解析操作 (lfs/lfp/lfss 等) ==========
    
    // 解析实例的所有字段 (lfs)
    listFields: (instancePtr: string, classHandle?: string) => {
        return InstanceService.listFields(instancePtr, classHandle);
    },
    
    // 解析实例的所有字段（包含父类）(lfp)
    listFieldsWithParents: (instancePtr: string) => {
        return InstanceService.listFieldsWithParents(instancePtr);
    },
    
    // 获取实例字段的字符串表示 (lfss)
    fieldsToString: (instancePtr: string, classHandle?: string) => {
        return InstanceService.fieldsToString(instancePtr, classHandle);
    },
    
    // 获取字段类型信息 (lft)
    getFieldType: (instancePtr: string, fieldName: string, classHandle?: string) => {
        return InstanceService.getFieldType(instancePtr, fieldName, classHandle);
    },
    
    // 获取字段值 (lfv)
    getFieldValue: (instancePtr: string, fieldName: string, classHandle?: string) => {
        return InstanceService.getFieldValue(instancePtr, fieldName, classHandle);
    },
    
    // 获取字段偏移 (lfo)
    getFieldOffset: (instancePtr: string, fieldName: string, classHandle?: string) => {
        return InstanceService.getFieldOffset(instancePtr, fieldName, classHandle);
    },
    
    // 获取实例的类型信息
    getInstanceType: (instancePtr: string) => {
        return InstanceService.getInstanceType(instancePtr);
    },
    
    // 获取实例的父类链
    getTypeParents: (instancePtr: string) => {
        return InstanceService.getTypeParents(instancePtr);
    },
    
    // 列出实例的所有方法 (lms)
    listInstanceMethods: (instancePtr: string) => {
        return InstanceService.listInstanceMethods(instancePtr);
    },
    
    // 读取实例指定偏移的值
    readAtOffset: (instancePtr: string, offset: number, size: number = 8) => {
        return InstanceService.readAtOffset(instancePtr, offset, size);
    },
    
    // 设置实例字段值
    setFieldValue: (instancePtr: string, fieldName: string, value: string, classHandle?: string) => {
        return InstanceService.setFieldValue(instancePtr, fieldName, value, classHandle);
    },

    // ========== Unity 操作 ==========
    
    // 获取 Transform
    getTransform: (instancePtr: string) => {
        return UnityService.getTransform(instancePtr);
    },
    
    // 获取 GameObject
    getGameObject: (instancePtr: string) => {
        return UnityService.getGameObject(instancePtr);
    },
    
    // 获取子对象
    getChildren: (transformPtr: string) => {
        return UnityService.getChildren(transformPtr);
    },
    
    // 获取父对象
    getParent: (transformPtr: string) => {
        return UnityService.getParent(transformPtr);
    },
    
    // 获取层级路径
    getHierarchy: (transformPtr: string, maxDepth: number = 10) => {
        return UnityService.getHierarchy(transformPtr, maxDepth);
    },
    
    // 发送消息
    sendMessage: (gameObjectName: string, methodName: string, message: string) => {
        return UnityService.sendMessage(gameObjectName, methodName, message);
    },
    
    // 查找 GameObject
    findGameObject: (path: string) => {
        return UnityService.findGameObject(path);
    },

    // ========== 内存操作 ==========
    
    // 分配 C 字符串
    allocCString: (str: string) => {
        return MemoryService.allocCString(str);
    },
    
    // 分配 IL2CPP 字符串
    allocIl2cppString: (str: string) => {
        return MemoryService.allocIl2cppString(str);
    },
    
    // 分配内存
    allocMemory: (size: number) => {
        return MemoryService.allocMemory(size);
    },
    
    // 分配 Vector
    allocVector: (values: number[]) => {
        return MemoryService.allocVector(values);
    },
    
    // 内存搜索 - 统一接口
    scan: (pattern: string, options?: {
        protection?: string;
        moduleName?: string;
        coalesce?: boolean;
        limit?: number;
    }) => {
        return MemoryService.scan(pattern, options);
    },
    
    // 写入内存
    writeMemory: (address: string, value: number | string, type: string = "int") => {
        return MemoryService.writeMemory(address, value, type);
    },
    
    // 读取内存
    readMemory: (address: string, type: string = "pointer", length: number = 0) => {
        return MemoryService.readMemory(address, type, length);
    },

    // ========== 应用信息 ==========
    
    // 获取 APK 信息
    getApkInfo: () => {
        return AppService.getApkInfo();
    }
};
