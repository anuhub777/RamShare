import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import MagicMock
from agent.job_runner import JobRunner

def test_job_runner_initialization():
    mock_executor = MagicMock()
    runner = JobRunner(
        api_url="http://localhost:8000",
        token="mock-token",
        provider_id="prov-123",
        executor=mock_executor,
        max_concurrent=2,
        poll_interval=5
    )
    assert runner.max_concurrent == 2
    assert runner.get_active_count() == 0
