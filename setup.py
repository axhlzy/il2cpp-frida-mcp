"""
Setup script - 在安装时自动编译 Agent
"""
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import shutil
import sys
from pathlib import Path


def build_agent():
    """编译 TypeScript Agent 并复制到包目录"""
    root = Path(__file__).parent
    agent_out = root / "_agent.js"
    target_dir = root / "mcp_server"
    target_file = target_dir / "_agent.js"
    
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    # 尝试编译
    try:
        if (root / "package.json").exists():
            print("[*] 安装 npm 依赖...")
            subprocess.run([npm_cmd, "install"], cwd=root, check=True)
            print("[*] 编译 Frida Agent...")
            subprocess.run([npm_cmd, "run", "build"], cwd=root, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[!] npm 编译跳过: {e}")
    
    # 复制 _agent.js 到包目录
    if agent_out.exists():
        shutil.copy(agent_out, target_file)
        print(f"[✓] _agent.js -> {target_file}")
    elif not target_file.exists():
        print("[!] 警告: _agent.js 不存在，请手动运行 npm run build")


class BuildPyCommand(build_py):
    def run(self):
        build_agent()
        super().run()


class DevelopCommand(develop):
    def run(self):
        build_agent()
        super().run()


class InstallCommand(install):
    def run(self):
        build_agent()
        super().run()


setup(
    cmdclass={
        'build_py': BuildPyCommand,
        'develop': DevelopCommand,
        'install': InstallCommand,
    }
)
