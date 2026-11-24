def test_register_success(client):
    res = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecretPassword123"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "alice"
    assert data["user"]["credit_balance"] == 500.0

def test_register_duplicate_username(client):
    res1 = client.post("/auth/register", json={
        "username": "bob",
        "email": "bob1@example.com",
        "password": "SecretPassword123"
    })
    assert res1.status_code == 201

    res2 = client.post("/auth/register", json={
        "username": "bob",
        "email": "bob2@example.com",
        "password": "SecretPassword123"
    })
    assert res2.status_code == 409

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "carol",
        "email": "carol@example.com",
        "password": "SecretPassword123"
    })
    res = client.post("/auth/login", json={
        "username": "carol",
        "password": "SecretPassword123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password(client):
    res = client.post("/auth/login", json={
        "username": "carol",
        "password": "WrongPassword"
    })
    assert res.status_code == 401

def test_get_me(client, auth_headers):
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"
