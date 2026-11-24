import psutil
import platform
from typing import Dict, Any

class ResourceMonitor:
    def get_system_info(self) -> Dict[str, Any]:
        """Get static system information."""
        mem = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage('/')
            total_disk = round(disk.total / (1024**3), 1)
        except Exception:
            total_disk = 100.0

        return {
            "os_type": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "total_cpu_cores": psutil.cpu_count(logical=True) or 1,
            "total_ram_mb": round(mem.total / (1024**2), 1),
            "total_disk_gb": total_disk,
        }

    def get_available_resources(self) -> Dict[str, Any]:
        """Get current dynamic available resources."""
        mem = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=0.1)
        available_cpu = max(0.0, round(100.0 - cpu_usage, 1))

        try:
            disk = psutil.disk_usage('/')
            free_disk = round(disk.free / (1024**3), 1)
        except Exception:
            free_disk = 50.0

        return {
            "available_cpu_percent": available_cpu,
            "available_ram_mb": round(mem.available / (1024**2), 1),
            "available_disk_gb": free_disk,
        }

    def is_system_busy(self, threshold: float = 85.0) -> bool:
        """Check if system CPU is exceeding the safety threshold."""
        return psutil.cpu_percent(interval=0.1) > threshold

    def get_summary(self) -> Dict[str, Any]:
        info = self.get_system_info()
        info.update(self.get_available_resources())
        return info
