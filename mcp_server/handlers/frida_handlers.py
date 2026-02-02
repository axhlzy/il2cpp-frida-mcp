"""
Frida Basic Operation Handlers
"""
import frida
import asyncio
from mcp.types import TextContent
from ..state import state
from ..agent_loader import load_agent


async def handle_list_devices() -> list[TextContent]:
    """List all devices"""
    try:
        devices = frida.enumerate_devices()
        result = "Available Devices:\n" + "=" * 60 + "\n"
        for dev in devices:
            type_str = {'local': 'Local', 'usb': 'USB', 'remote': 'Remote'}.get(dev.type, dev.type)
            result += f"  [{type_str}] {dev.name} (ID: {dev.id})\n"
        result += "=" * 60
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get device list: {e}")]


async def handle_connect(args: dict) -> list[TextContent]:
    """Connect to device and process"""
    try:
        device_type = args.get("device_type", "usb")
        mode = args.get("mode", "attach_front")
        target = args.get("target", "")
        remote_host = args.get("remote_host", "127.0.0.1:27042")
        
        # Get device
        if device_type == "usb":
            state.device = frida.get_usb_device()
        elif device_type == "remote":
            dm = frida.get_device_manager()
            state.device = dm.add_remote_device(remote_host)
        else:
            state.device = frida.get_local_device()
        
        result = f"[✓] Connected to device: {state.device.name}\n"
        
        # Connect to process
        if mode == "spawn":
            if not target:
                return [TextContent(type="text", text="[✗] spawn mode requires package name")]
            state.pid = state.device.spawn([target])
            state.session = state.device.attach(state.pid)
            result += f"[✓] Spawned and attached: {target} (PID: {state.pid})\n"
            result += "[!] Process suspended, use frida_resume to continue\n"
        elif mode == "attach_front":
            app = state.device.get_frontmost_application()
            if not app:
                return [TextContent(type="text", text="[✗] No foreground application")]
            state.pid = app.pid
            state.session = state.device.attach(state.pid)
            result += f"[✓] Attached to foreground app: {app.identifier} (PID: {state.pid})\n"
        elif mode == "attach_name":
            if not target:
                return [TextContent(type="text", text="[✗] attach_name mode requires process name")]
            state.session = state.device.attach(target)
            result += f"[✓] Attached to process: {target}\n"
        elif mode == "attach_pid":
            if not target:
                return [TextContent(type="text", text="[✗] attach_pid mode requires PID")]
            pid = int(target)
            state.session = state.device.attach(pid)
            state.pid = pid
            result += f"[✓] Attached to PID: {pid}\n"
        
        # Load Agent
        if load_agent():
            result += "[✓] Agent loaded\n"
            state.connected = True
            if mode != "spawn":
                result += "[*] Waiting for IL2CPP initialization...\n"
                await asyncio.sleep(2)
                result += "[✓] Ready\n"
        else:
            result += "[✗] Failed to load agent\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Connection failed: {e}")]


async def handle_disconnect() -> list[TextContent]:
    """Disconnect"""
    try:
        if state.session:
            state.session.detach()
        state.session = None
        state.script = None
        state.device = None
        state.pid = None
        state.connected = False
        return [TextContent(type="text", text="[✓] Disconnected")]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Disconnect failed: {e}")]


async def handle_resume() -> list[TextContent]:
    """Resume process"""
    try:
        if state.device and state.pid:
            state.device.resume(state.pid)
            await asyncio.sleep(3)
            return [TextContent(type="text", text=f"[✓] Resumed process PID: {state.pid}")]
        else:
            return [TextContent(type="text", text="[✗] No process to resume")]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Resume failed: {e}")]


async def handle_list_processes(args: dict) -> list[TextContent]:
    """List processes"""
    try:
        if not state.device:
            return [TextContent(type="text", text="[✗] Please connect to device first")]
        
        filter_str = args.get("filter", "").lower()
        processes = state.device.enumerate_processes()
        
        if filter_str:
            processes = [p for p in processes if filter_str in p.name.lower()]
        
        result = f"Process List ({len(processes)} total):\n" + "=" * 60 + "\n"
        for p in processes[:50]:
            result += f"  [{p.pid}] {p.name}\n"
        
        if len(processes) > 50:
            result += f"  ... and {len(processes) - 50} more processes\n"
        
        result += "=" * 60
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"[✗] Failed to get process list: {e}")]
