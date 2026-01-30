/**
 * 执行服务 - 处理任意 JavaScript 代码执行
 */
export class ExecService {
    /**
     * 执行任意 JavaScript 代码
     */
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
