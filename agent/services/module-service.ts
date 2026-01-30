/**
 * 模块服务 - 处理导入导出函数相关操作
 */
export class ModuleService {
    /**
     * 查找导出函数
     */
    static findExport(exportName: string, moduleName?: string): any[] {
        const result: any[] = [];

        const processModule = (md: Module) => {
            md.enumerateExports().forEach((exp: ModuleExportDetails) => {
                if (exp.name.includes(exportName)) {
                    result.push({
                        name: exp.name,
                        address: exp.address.toString(),
                        relative_address: exp.address.sub(md.base).toString(),
                        type: exp.type,
                        module_name: md.name,
                        module_base: md.base.toString()
                    });
                }
            });
        };

        if (moduleName) {
            const md = Process.findModuleByName(moduleName);
            if (md) {
                processModule(md);
            } else {
                throw new Error(`Module not found: ${moduleName}`);
            }
        } else {
            Process.enumerateModules().forEach(processModule);
        }

        return result;
    }

    /**
     * 查找导入函数
     */
    static findImport(moduleName: string, importName?: string): any[] {
        const result: any[] = [];
        const md = Process.findModuleByName(moduleName);
        
        if (!md) {
            throw new Error(`Module not found: ${moduleName}`);
        }

        md.enumerateImports().forEach((imp: ModuleImportDetails) => {
            if (!importName || imp.name.includes(importName)) {
                result.push({
                    name: imp.name,
                    address: imp.address?.toString() || "null",
                    type: imp.type,
                    module: imp.module || "unknown",
                    slot: imp.slot?.toString() || "null"
                });
            }
        });

        return result;
    }
}
