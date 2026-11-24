def test_credit_estimate(client, auth_headers):
    res = client.post("/credits/estimate", json={
        "workload_type": "CPU_BENCHMARK",
        "required_ram_mb": 1024,
        "required_cpu_cores": 2,
        "estimated_duration_seconds": 120
    }, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["estimated_credits"] > 0
    assert "breakdown" in data

def test_get_balance_and_transactions(client, auth_headers):
    bal_res = client.get("/credits/balance", headers=auth_headers)
    assert bal_res.status_code == 200
    assert bal_res.json()["balance"] == 500.0

    tx_res = client.get("/credits/transactions", headers=auth_headers)
    assert tx_res.status_code == 200
    assert len(tx_res.json()["transactions"]) >= 1
    assert tx_res.json()["transactions"][0]["transaction_type"] == "SIGNUP_BONUS"
