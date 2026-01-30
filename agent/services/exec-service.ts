import Java from "frida-java-bridge";

(globalThis as any).Java = Java;

export class ExecService {
    static execJs(code: string): any {
        try {
            const result = eval(code);
            return {
                success: true,
                result: result,
                type: typeof result
            };
        } catch (e) {
            return {
                success: false,
                error: String(e),
                stack: (e as Error).stack
            };
        }
    }
}
