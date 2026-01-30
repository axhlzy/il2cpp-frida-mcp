"""
构建脚本：在 pip install 时自动编译 Frida Agent
"""
import subprocess
import shutil
import sys
from pathlib import Path


def build_agent():
    """编译 TypeScript Agent"""
    root = Path(__file__).parent
    agent_src = root / "agent"
    agent_out = root / "_agent.js"
    target_dir = root / "mcp_server"
    target_file = target_dir / "_agent.js"
    
    # 检查是否有 agent 源码
    if not agent_src.exists():
        print("[!] agent/ 目录不存在，跳过编译")
        # 如果已有编译好的文件，直接复制
        if agent_out.exists():
            shutil.copy(agent_out, target_file)
            print(f"[✓] 复制已有的 _agent.js 到 {target_file}")
        return
    
    # 检查 npm
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    try:
        # 安装依赖
        print("[*] 安装 npm 依赖...")
        subprocess.run([npm_cmd, "install"], cwd=root, check=True, capture_output=True)
        
        # 编译
        print("[*] 编译 Frida Agent...")
        subprocess.run([npm_cmd, "run", "build"], cwd=root, check=True, capture_output=True)
        
        # 复制到包目录
        if agent_out.exists():
            shutil.copy(agent_out, target_file)
            print(f"[✓] Agent 编译完成: {target_file}")
        else:
            print("[✗] 编译后未找到 _agent.js")
            
    except FileNotFoundError:
        print("[!] npm 未安装，跳过 Agent 编译")
        if agent_out.exists():
            shutil.copy(agent_out, target_file)
            print(f"[✓] 使用已有的 _agent.js")
    except subprocess.CalledProcessError as e:
        print(f"[!] 编译失败: {e}")
        if agent_out.exists():
            shutil.copy(agent_out, target_file)
            print(f"[✓] 使用已有的 _agent.js")


if __name__ == "__main__":
    build_agent()
