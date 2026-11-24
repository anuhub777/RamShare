import asyncio
from app.dependencies import get_storage_instance, get_queue_instance
from app.services.matchmaking_service import MatchmakingService

def test_full_peer_to_peer_execution_cycle(client):
    """
    End-to-End Acceptance Test:
    1. Provider user registers
    2. Consumer user registers
    3. Provider registers machine and reports online status via heartbeat
    4. Consumer submits workload
    5. Matchmaking matches and assigns job to provider
    6. Provider polls and receives assignment
    7. Provider marks RUNNING, then COMPLETED with result payload
    8. Credit ledger atomically deducts consumer and rewards provider
    9. Final verification of job state and wallet balances
    """
    # 1. Provider user
    p_reg = client.post("/auth/register", json={
        "username": "provider_node",
        "email": "provider@peer.network",
        "password": "Password123",
        "roles": ["provider"]
    })
    p_token = p_reg.json()["access_token"]
    p_headers = {"Authorization": f"Bearer {p_token}"}

    # 2. Consumer user
    c_reg = client.post("/auth/register", json={
        "username": "consumer_user",
        "email": "consumer@client.network",
        "password": "Password123",
        "roles": ["consumer"]
    })
    c_token = c_reg.json()["access_token"]
    c_headers = {"Authorization": f"Bearer {c_token}"}

    # 3. Provider registers machine and heartbeats
    prov_res = client.post("/providers/register", json={
        "machine_name": "Workstation-Ryzen9",
        "os_type": "Linux",
        "os_version": "Ubuntu 22.04",
        "architecture": "x86_64",
        "total_cpu_cores": 16,
        "total_ram_mb": 32768,
        "total_disk_gb": 1024,
        "max_cpu_percent": 80.0,
        "max_ram_mb": 8192.0,
        "max_concurrent_jobs": 4
    }, headers=p_headers)
    provider_id = prov_res.json()["id"]

    client.post("/providers/heartbeat", json={
        "provider_id": provider_id,
        "available_cpu_percent": 85.0,
        "available_ram_mb": 7500.0,
        "available_disk_gb": 400.0,
        "current_job_count": 0
    }, headers=p_headers)

    # 4. Consumer submits job
    job_sub = client.post("/jobs", json={
        "job_name": "Genomics Sequence Fold",
        "workload_type": "CPU_BENCHMARK",
        "required_ram_mb": 1024,
        "required_cpu_cores": 2,
        "max_execution_time": 60,
        "input_params": {"iterations": 20000}
    }, headers=c_headers)
    assert job_sub.status_code == 201
    job_id = job_sub.json()["id"]
    estimated_credits = job_sub.json()["estimated_credits"]

    # 5. Run Matchmaker
    storage = get_storage_instance()
    queue = get_queue_instance()
    matchmaking = MatchmakingService(storage, queue)
    processed = asyncio.run(matchmaking.process_job_queue())
    assert processed >= 1

    # Verify job ASSIGNED
    job_check = client.get(f"/jobs/{job_id}", headers=c_headers)
    assert job_check.json()["status"] == "ASSIGNED"
    assert job_check.json()["provider_id"] == provider_id

    # 6. Provider polls jobs
    poll_res = client.get(f"/jobs/poll/{provider_id}", headers=p_headers)
    assert poll_res.status_code == 200
    assigned_jobs = poll_res.json()
    assert any(j["id"] == job_id for j in assigned_jobs)

    # 7. Provider updates status to RUNNING
    run_res = client.post(f"/jobs/{job_id}/status", json={"status": "RUNNING"}, headers=p_headers)
    assert run_res.status_code == 200

    # 8. Provider reports COMPLETED with result
    comp_res = client.post(f"/jobs/{job_id}/status", json={
        "status": "COMPLETED",
        "result_summary": "Processed 20000 sequence iterations in 3.142s inside isolated Docker container",
        "actual_credits": estimated_credits
    }, headers=p_headers)
    assert comp_res.status_code == 200

    # 9. Verify Final State & Credit Balances
    final_job = client.get(f"/jobs/{job_id}", headers=c_headers)
    assert final_job.json()["status"] == "COMPLETED"
    assert "Processed 20000" in final_job.json()["result_summary"]

    c_bal = client.get("/credits/balance", headers=c_headers)
    p_bal = client.get("/credits/balance", headers=p_headers)

    # Consumer spent credits
    assert c_bal.json()["balance"] < 500.0
    # Provider earned credits
    assert p_bal.json()["balance"] > 500.0
