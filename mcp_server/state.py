"""
Frida 全局状态管理
"""
from typing import Any, Optional


class FridaState:
    """Frida 连接状态"""
    device: Optional[Any] = None
    session: Optional[Any] = None
    script: Optional[Any] = None
    pid: Optional[int] = None
    connected: bool = False


# 全局状态实例
state = FridaState()
