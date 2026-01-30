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
    }
};
