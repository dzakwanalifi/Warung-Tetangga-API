from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    """Tes untuk endpoint root /."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Warung Warga API v1.0.0"}

def test_health_check(client: TestClient):
    """Tes untuk endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 