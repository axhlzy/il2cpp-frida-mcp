import "frida-il2cpp-bridge"
import { Il2CppCache } from "../core/il2cpp-helper"

/**
 * 反汇编服务 - 处理反汇编相关操作
 */
export class DisasmService {
    /**
     * 反汇编方法
     * @param methodPtr 方法地址（virtualAddress）
     * @param instructionCount 反汇编指令数量
     * @param resolveFunctions 是否解析跳转目标函数名
     */
    static showAsm(methodPtr: string, instructionCount: number = 64, resolveFunctions: boolean = false): any {
        const result: any[] = [];
        let currentPtr = ptr(methodPtr);
        
        // 检查是否是相对地址，如果是则加上模块基址
        const il2cppModule = Process.findModuleByName("libil2cpp.so");
        if (il2cppModule && currentPtr.compare(il2cppModule.base) < 0) {
            currentPtr = il2cppModule.base.add(currentPtr);
        }

        // 如果需要解析函数，先预加载所有方法
        let methodsPreloaded = false;
        if (resolveFunctions) {
            // 触发方法缓存加载
            Il2CppCache.methods;
            methodsPreloaded = true;
        }

        let count = 0;
        while (count < instructionCount) {
            try {
                const ins = Instruction.parse(currentPtr);
                
                const insInfo: any = {
                    address: ins.address.toString(),
                    mnemonic: ins.mnemonic,
                    opStr: ins.opStr,
                    size: ins.size,
                    toString: ins.toString()
                };

                // 检查是否是跳转指令
                const jumpMnemonics = ["bl", "blx", "b", "bx", "b.w", "blx.w", "bl.w", "bne", "beq"];
                if (jumpMnemonics.includes(ins.mnemonic)) {
                    try {
                        const target = ptr(ins.opStr.replace("#", ""));
                        insInfo.jump_target = target.toString();
                        
                        if (resolveFunctions) {
                            const targetMethod = this.addressToMethod(target);
                            if (targetMethod) {
                                insInfo.target_method = {
                                    name: targetMethod.name,
                                    class_name: targetMethod.class.name,
                                    handle: targetMethod.handle.toString()
                                };
                            }
                        }
                    } catch (e) {
                        // 忽略解析错误
                    }
                }

                result.push(insInfo);
                currentPtr = ins.next;
                count++;

                if (ins.mnemonic === "ret") {
                    break;
                }
            } catch (e) {
                break;
            }
        }

        return {
            instructions: result,
            resolve_functions_enabled: resolveFunctions,
            methods_preloaded: methodsPreloaded
        };
    }

    /**
     * 根据地址查找方法
     */
    private static addressToMethod(address: NativePointer): Il2Cpp.Method | null {
        try {
            const methods = Il2CppCache.methods;
            for (const method of methods) {
                if (method.virtualAddress.equals(address) || method.relativeVirtualAddress.equals(address)) {
                    return method;
                }
            }
        } catch (e) {
            // 忽略错误
        }
        return null;
    }
}
