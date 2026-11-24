import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from agent.monitor import ResourceMonitor

def test_system_info():
    monitor = ResourceMonitor()
    info = monitor.get_system_info()
    assert "os_type" in info
    assert "architecture" in info
    assert info["total_cpu_cores"] >= 1
    assert info["total_ram_mb"] > 0

def test_available_resources():
    monitor = ResourceMonitor()
    res = monitor.get_available_resources()
    assert "available_cpu_percent" in res
    assert "available_ram_mb" in res
    assert res["available_cpu_percent"] >= 0.0
    assert res["available_ram_mb"] > 0.0
