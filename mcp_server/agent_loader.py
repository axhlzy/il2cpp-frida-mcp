"""
Frida Agent 加载器
"""
import sys
from pathlib import Path
from .state import state


def get_agent_path() -> Path:
    """获取 _agent.js 的路径"""
    # 优先从包目录加载
    pkg_agent = Path(__file__).parent / "_agent.js"
    if pkg_agent.exists():
        return pkg_agent
    
    # 回退到当前工作目录
    cwd_agent = Path.cwd() / "_agent.js"
    if cwd_agent.exists():
        return cwd_agent
    
    raise FileNotFoundError("_agent.js 未找到，请先运行 npm run build")


def load_agent(agent_path: str | None = None) -> bool:
    """加载 Frida Agent"""
    if not state.session:
        return False
    try:
        if agent_path is None:
            agent_path = str(get_agent_path())
        
        with open(agent_path, 'r', encoding='utf-8') as f:
            agent_code = f.read()
        state.script = state.session.create_script(agent_code)
        state.script.load()
        return True
    except Exception as e:
        print(f"加载 Agent 失败: {e}", file=sys.stderr)
        return False
