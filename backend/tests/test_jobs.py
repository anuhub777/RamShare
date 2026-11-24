def test_submit_job(client, auth_headers):
    payload = {
        "job_name": "Matrix Multiplier",
        "workload_type": "CPU_BENCHMARK",
        "required_ram_mb": 512,
        "required_cpu_cores": 1,
        "max_execution_time": 60,
        "input_params": {"iterations": 5000}
    }
    res = client.post("/jobs", json=payload, headers=auth_headers)
    assert res.status_code == 201
    job = res.json()
    assert job["job_name"] == "Matrix Multiplier"
    assert job["status"] == "PENDING"
    assert job["estimated_credits"] > 0

def test_cancel_job(client, auth_headers):
    res = client.post("/jobs", json={
        "job_name": "Cancel Me",
        "workload_type": "DATA_PROCESSING",
        "required_ram_mb": 256,
        "required_cpu_cores": 1,
        "max_execution_time": 60
    }, headers=auth_headers)
    job_id = res.json()["id"]

    cancel_res = client.post(f"/jobs/{job_id}/cancel", headers=auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
