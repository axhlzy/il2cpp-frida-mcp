# IL2CPP Frida MCP Server

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的 IL2CPP 逆向分析工具
让大模型能够直接分析和操作 Unity IL2CPP 应用

## 功能特性

- 🔌 **Frida 集成** - 支持 USB、远程、本地设备连接
- 📦 **IL2CPP 分析** - 列出镜像、类、方法，支持模糊搜索
- 🔍 **反汇编** - 基于 Frida Instruction API 的方法反汇编
- 🧠 **GC 堆分析** - 查找运行时对象实例
- 📤 **导入导出** - 查找模块的导入导出函数
- 🛠️ **JS 执行** - 执行任意 JavaScript 代码操作 Frida API

## 项目结构

```
.
├── mcp_server.py           # 入口文件
├── mcp_server/             # MCP Server 模块
│   ├── __init__.py
│   ├── server.py           # MCP Server 核心
│   ├── state.py            # Frida 状态管理
│   ├── tools.py            # MCP 工具定义
│   ├── transport.py        # 传输层 (stdio/sse/http)
│   ├── cli.py              # 命令行接口
│   ├── agent_loader.py     # Agent 加载器
│   └── handlers/           # 工具处理器
│       ├── __init__.py
│       ├── frida_handlers.py
│       └── il2cpp_handlers.py
├── agent/                  # Frida Agent (TypeScript)
│   ├── index.ts            # Agent 入口
│   ├── core/               # 核心模块
│   │   ├── il2cpp-helper.ts
│   │   ├── method-utils.ts
│   │   └── class-finder.ts
│   └── services/           # 服务模块
│       ├── image-service.ts
│       ├── class-service.ts
│       ├── method-service.ts
│       ├── disasm-service.ts
│       ├── module-service.ts
│       ├── gc-service.ts
│       └── exec-service.ts
├── _agent.js               # 编译后的 Agent
├── package.json
├── tsconfig.json
└── requirements.txt
```

## 安装

### 方式一：pip 安装（推荐）

```bash
# 从源码安装
pip install .

# 或开发模式安装
pip install -e .
```

### 方式二：手动安装依赖

```bash
pip install -r requirements.txt
```

### 编译 Frida Agent

```bash
npm install
npm run build
```

## 使用方法

### 启动 MCP Server

```bash
# 如果通过 pip 安装
il2cpp-frida-mcp                        # 交互式选择
il2cpp-frida-mcp --stdio                # stdio 模式
il2cpp-frida-mcp --sse                  # SSE 模式
il2cpp-frida-mcp --http                 # HTTP 模式

# 或直接运行脚本
python mcp_server.py --stdio

# 自定义地址和端口
il2cpp-frida-mcp --sse --host 0.0.0.0 --port 9000
```

### 配置 MCP 客户端

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "il2cpp-frida": {
      "command": "il2cpp-frida-mcp",
      "args": ["--stdio"]
    }
  }
}
```

或者使用 Python 模块运行：

```json
{
  "mcpServers": {
    "il2cpp-frida": {
      "command": "python",
      "args": ["-m", "mcp_server", "--stdio"]
    }
  }
}
```

## MCP 工具列表

### Frida 基础工具

| 工具名 | 描述 |
|--------|------|
| `frida_list_devices` | 列出所有可用的 Frida 设备 |
| `frida_connect` | 连接到设备和目标进程 |
| `frida_disconnect` | 断开 Frida 连接 |
| `frida_resume` | 恢复被暂停的进程 |
| `frida_list_processes` | 列出设备上的进程 |

### IL2CPP 分析工具

| 工具名 | 描述 |
|--------|------|
| `il2cpp_list_images` | 列出所有 IL2CPP 镜像 |
| `il2cpp_list_classes` | 列出指定镜像的所有类 |
| `il2cpp_list_methods` | 列出指定类的所有方法 |
| `il2cpp_show_method` | 显示方法的详细信息 |
| `il2cpp_find_classes` | 查找类（支持模糊匹配） |
| `il2cpp_find_methods` | 查找方法（支持模糊匹配） |
| `il2cpp_show_asm` | 反汇编方法 |
| `il2cpp_find_export` | 查找导出函数 |
| `il2cpp_find_import` | 查找导入函数 |
| `il2cpp_exec_js` | 执行任意 JavaScript 代码 |
| `il2cpp_gc_choose` | 在堆中查找指定类的实例 |
| `il2cpp_gc_info` | 获取 GC 堆信息 |

### 编译 Agent

```bash
npm run build
npm run watch
```

### 依赖

- Python 3.10+
- Node.js 16+
- Frida 16+
- frida-il2cpp-bridge

## 致谢

- [frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge) - IL2CPP 运行时桥接
- [Il2CppHookScripts](https://github.com/AeonLucid/Il2CppHookScripts) - 参考实现

## License

MIT
