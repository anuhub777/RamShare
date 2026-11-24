def test_register_provider(client, auth_headers):
    payload = {
        "machine_name": "worker-alpha",
        "os_type": "Linux",
        "os_version": "6.1.0",
        "architecture": "x86_64",
        "total_cpu_cores": 8,
        "total_ram_mb": 16384,
        "total_disk_gb": 512,
        "max_cpu_percent": 75.0,
        "max_ram_mb": 4096.0,
        "max_concurrent_jobs": 2
    }
    res = client.post("/providers/register", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["machine_name"] == "worker-alpha"
    assert data["is_online"] is True
    assert data["is_sharing"] is True

def test_provider_heartbeat(client, auth_headers):
    reg = client.post("/providers/register", json={
        "machine_name": "worker-beta",
        "os_type": "Darwin",
        "os_version": "14.2",
        "architecture": "arm64",
        "total_cpu_cores": 10,
        "total_ram_mb": 32768,
        "total_disk_gb": 1024
    }, headers=auth_headers)
    provider_id = reg.json()["id"]

    hb = client.post("/providers/heartbeat", json={
        "provider_id": provider_id,
        "available_cpu_percent": 68.5,
        "available_ram_mb": 12000.0,
        "available_disk_gb": 250.0,
        "current_job_count": 0
    }, headers=auth_headers)
    assert hb.status_code == 200
    assert hb.json()["status"] == "ok"
