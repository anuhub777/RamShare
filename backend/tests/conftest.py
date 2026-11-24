import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.local import LocalStorage
from app.main import create_app
from fastapi.testclient import TestClient

@pytest.fixture
def storage():
    s = LocalStorage(db_path=":memory:")
    asyncio.run(s.initialize())
    return s

@pytest.fixture
def client(storage):
    app = create_app(storage_override=storage)
    with TestClient(app) as tc:
        yield tc

@pytest.fixture
def auth_headers(client):
    res = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123",
        "roles": ["consumer"]
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
