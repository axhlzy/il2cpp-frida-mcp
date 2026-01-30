"""
IL2CPP Frida MCP Server
提供 MCP 接口让 AI 助手可以分析 IL2CPP 应用
"""
from .server import server
from .state import state

__all__ = ["server", "state"]
