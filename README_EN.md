# IL2CPP Frida MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) based IL2CPP reverse engineering tool that enables AI assistants (like Claude, Kiro) to directly analyze and manipulate Unity IL2CPP applications.

## Features

- 🔌 **Frida Integration** - Support for USB, remote, and local device connections
- 📦 **IL2CPP Analysis** - List images, classes, methods with fuzzy search support
- 🔍 **Disassembly** - Method disassembly based on Frida Instruction API
- 🧠 **GC Heap Analysis** - Find runtime object instances
- 📤 **Import/Export** - Find module import and export functions
- 🛠️ **JS Execution** - Execute arbitrary JavaScript code to manipulate Frida API

## Project Structure

```
.
├── mcp_server.py           # Entry point
├── mcp_server/             # MCP Server module
│   ├── __init__.py
│   ├── server.py           # MCP Server core
│   ├── state.py            # Frida state management
│   ├── tools.py            # MCP tool definitions
│   ├── transport.py        # Transport layer (stdio/sse/http)
│   ├── cli.py              # Command line interface
│   ├── agent_loader.py     # Agent loader
│   └── handlers/           # Tool handlers
│       ├── __init__.py
│       ├── frida_handlers.py
│       └── il2cpp_handlers.py
├── agent/                  # Frida Agent (TypeScript)
│   ├── index.ts            # Agent entry point
│   ├── core/               # Core modules
│   │   ├── il2cpp-helper.ts
│   │   ├── method-utils.ts
│   │   └── class-finder.ts
│   └── services/           # Service modules
│       ├── image-service.ts
│       ├── class-service.ts
│       ├── method-service.ts
│       ├── disasm-service.ts
│       ├── module-service.ts
│       ├── gc-service.ts
│       └── exec-service.ts
├── _agent.js               # Compiled Agent
├── package.json
├── tsconfig.json
└── requirements.txt
```

## Installation

### Option 1: pip install (Recommended)

```bash
# Install from source
pip install .

# Or install in development mode
pip install -e .
```

### Option 2: Manual dependency installation

```bash
pip install -r requirements.txt
```

### Compile Frida Agent

```bash
npm install
npm run build
```

## Usage

### Start MCP Server

```bash
# If installed via pip
il2cpp-mcp                              # Interactive selection
il2cpp-mcp --stdio                      # stdio mode
il2cpp-mcp --sse                        # SSE mode
il2cpp-mcp --http                       # HTTP mode

# Or run script directly
python mcp_server.py --stdio

# Custom host and port
il2cpp-mcp --sse --host 0.0.0.0 --port 9000
```

### Configure MCP Client

#### Claude Desktop / Kiro

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "il2cpp-frida": {
      "command": "il2cpp-mcp",
      "args": ["--stdio"]
    }
  }
}
```

Or run using Python module:

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

## MCP Tools

### Frida Basic Tools

| Tool | Description |
|------|-------------|
| `frida_list_devices` | List all available Frida devices |
| `frida_connect` | Connect to device and target process |
| `frida_disconnect` | Disconnect Frida connection |
| `frida_resume` | Resume suspended process |
| `frida_list_processes` | List processes on device |

### IL2CPP Analysis Tools

| Tool | Description |
|------|-------------|
| `il2cpp_list_images` | List all IL2CPP images |
| `il2cpp_list_classes` | List all classes in specified image |
| `il2cpp_list_methods` | List all methods in specified class |
| `il2cpp_show_method` | Show method details |
| `il2cpp_find_classes` | Find classes (fuzzy match supported) |
| `il2cpp_find_methods` | Find methods (fuzzy match supported) |
| `il2cpp_show_asm` | Disassemble method |
| `il2cpp_find_export` | Find export functions |
| `il2cpp_find_import` | Find import functions |
| `il2cpp_exec_js` | Execute arbitrary JavaScript code |
| `il2cpp_gc_choose` | Find instances of specified class in heap |
| `il2cpp_gc_info` | Get GC heap information |

## Examples

### 1. Connect to Device

```
Use frida_connect to connect to the frontmost app on USB device
```

### 2. Analyze IL2CPP

```
List all images, then find classes containing "Player"
```

### 3. View Method Details

```
List all methods of PlayerController class, then view Update method details
```

## Development

### Compile Agent

```bash
npm run build     # Single build
npm run watch     # Watch mode
```

### Dependencies

- Python 3.10+
- Node.js 16+
- Frida 17+
- frida-il2cpp-bridge

## Acknowledgements

- [frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge) - IL2CPP runtime bridge
- [Il2CppHookScripts](https://github.com/AeonLucid/Il2CppHookScripts) - Reference implementation

## License

MIT
