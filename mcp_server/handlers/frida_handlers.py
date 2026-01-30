"""
Frida 基础操作处理器
"""
import frida
import asyncio
from mcp.types import TextContent
from ..state import state
from ..agent_loader import load_agent


async def handle_list_devices() -> list[TextContent]:
    """列出所有设备"""
    try:
        devices = frida.enumerate_devices()
        result = "可用设备列表:\n" + "=" * 60 + "\n"
        for dev in devices:
            type_str = {'local': '本地', 'usb': 'USB', 'remote': '远程'}.get(dev.type, dev.type)
            result += f"  [{type_str}] {dev.name} (ID: {dev.id})\n"
        result += "=" * 60
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 获取设备列表失败: {e}")]


async def handle_connect(args: dict) -> list[TextContent]:
    """连接到设备和进程"""
    try:
        device_type = args.get("device_type", "usb")
        mode = args.get("mode", "attach_front")
        target = args.get("target", "")
        remote_host = args.get("remote_host", "127.0.0.1:27042")
        
        # 获取设备
        if device_type == "usb":
            state.device = frida.get_usb_device()
        elif device_type == "remote":
            dm = frida.get_device_manager()
            state.device = dm.add_remote_device(remote_host)
        else:
            state.device = frida.get_local_device()
        
        result = f"[✓] 已连接设备: {state.device.name}\n"
        
        # 连接到进程
        if mode == "spawn":
            if not target:
                return [TextContent(type="text", text="[✗] spawn 模式需要指定包名")]
            state.pid = state.device.spawn([target])
            state.session = state.device.attach(state.pid)
            result += f"[✓] 已启动并附加: {target} (PID: {state.pid})\n"
            result += "[!] 进程已暂停,使用 frida_resume 恢复执行\n"
        elif mode == "attach_front":
            app = state.device.get_frontmost_application()
            if not app:
                return [TextContent(type="text", text="[✗] 没有前台应用")]
            state.pid = app.pid
            state.session = state.device.attach(state.pid)
            result += f"[✓] 已附加到前台应用: {app.identifier} (PID: {state.pid})\n"
        elif mode == "attach_name":
            if not target:
                return [TextContent(type="text", text="[✗] attach_name 模式需要指定进程名")]
            state.session = state.device.attach(target)
            result += f"[✓] 已附加到进程: {target}\n"
        elif mode == "attach_pid":
            if not target:
                return [TextContent(type="text", text="[✗] attach_pid 模式需要指定 PID")]
            pid = int(target)
            state.session = state.device.attach(pid)
            state.pid = pid
            result += f"[✓] 已附加到 PID: {pid}\n"
        
        # 加载 Agent
        if load_agent():
            result += "[✓] Agent 已加载\n"
            state.connected = True
            if mode != "spawn":
                result += "[*] 等待 IL2CPP 初始化...\n"
                await asyncio.sleep(2)
                result += "[✓] 就绪\n"
        else:
            result += "[✗] Agent 加载失败\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 连接失败: {e}")]


async def handle_disconnect() -> list[TextContent]:
    """断开连接"""
    try:
        if state.session:
            state.session.detach()
        state.session = None
        state.script = None
        state.device = None
        state.pid = None
        state.connected = False
        return [TextContent(type="text", text="[✓] 已断开连接")]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 断开失败: {e}")]


async def handle_resume() -> list[TextContent]:
    """恢复进程"""
    try:
        if state.device and state.pid:
            state.device.resume(state.pid)
            await asyncio.sleep(3)
            return [TextContent(type="text", text=f"[✓] 已恢复进程 PID: {state.pid}")]
        else:
            return [TextContent(type="text", text="[✗] 没有可恢复的进程")]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 恢复失败: {e}")]


async def handle_list_processes(args: dict) -> list[TextContent]:
    """列出进程"""
    try:
        if not state.device:
            return [TextContent(type="text", text="[✗] 请先连接设备")]
        
        filter_str = args.get("filter", "").lower()
        processes = state.device.enumerate_processes()
        
        if filter_str:
            processes = [p for p in processes if filter_str in p.name.lower()]
        
        result = f"进程列表 (共 {len(processes)} 个):\n" + "=" * 60 + "\n"
        for p in processes[:50]:
            result += f"  [{p.pid}] {p.name}\n"
        
        if len(processes) > 50:
            result += f"  ... 还有 {len(processes) - 50} 个进程\n"
        
        result += "=" * 60
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] 获取进程列表失败: {e}")]
