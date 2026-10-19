import platform
import socket
from datetime import datetime


def collect_system():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "timestamp": datetime.now().isoformat()
    }