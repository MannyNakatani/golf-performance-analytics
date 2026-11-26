import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "golf-performance-api"
    }