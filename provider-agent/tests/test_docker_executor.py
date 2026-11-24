import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from agent.docker_executor import DockerExecutor, APPROVED_IMAGES

def test_approved_images():
    assert "CPU_BENCHMARK" in APPROVED_IMAGES
    assert "MEMORY_BENCHMARK" in APPROVED_IMAGES
    assert "DATA_PROCESSING" in APPROVED_IMAGES
    assert "ML_INFERENCE" in APPROVED_IMAGES

def test_unknown_workload_rejection(tmp_path):
    executor = DockerExecutor(storage_dir=str(tmp_path))
    res = executor.execute_workload({
        "id": "test-123",
        "workload_type": "ARBITRARY_CODE_EXECUTION",
    })
    assert res["success"] is False
    assert "disallowed" in res["error"].lower()

def test_command_generation(tmp_path):
    executor = DockerExecutor(storage_dir=str(tmp_path))
    cmd = executor._get_command("CPU_BENCHMARK", {"iterations": 1000})
    assert "factorial" in cmd
