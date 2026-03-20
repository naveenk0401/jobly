import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["app"] == "Jobly"

def test_create_user(client):
    r = client.post("/user", json={
        "email":   "pytest@jobly.com",
        "name":    "Pytest User",
        "summary": "Test summary"
    })
    # 200 created or 400 already exists
    assert r.status_code in [200, 400]

def test_get_jobs(client):
    r = client.get("/jobs?limit=5")
    assert r.status_code == 200
    assert "jobs" in r.json()
    assert "total" in r.json()

def test_get_jobs_filter_source(client):
    r = client.get("/jobs?source=greenhouse&limit=3")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    for j in jobs:
        assert j.get("source") == "greenhouse"

def test_autopilot_user_not_found(client):
    r = client.post(
        "/autopilot/enable?user_id=000000000000000000000000"
    )
    assert r.status_code == 404
