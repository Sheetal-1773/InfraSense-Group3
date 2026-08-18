def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "InfraSense API"
    assert data["version"] == "2.0.0"


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "infrasense-api"


def test_dashboard_health(client):
    response = client.get("/api/dashboard/health")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "categories" in data


def test_data_sources_status(client):
    response = client.get("/api/data-sources/status")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "data_mode" in data


def test_unknown_endpoint_returns_404(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404