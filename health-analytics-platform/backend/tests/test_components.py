def test_get_components(client):
    response = client.get("/api/components")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert "total" in data


def test_get_components_filter_by_status(client):
    response = client.get("/api/components", params={"status": "healthy"})
    assert response.status_code == 200
    data = response.json()
    for comp in data["data"]:
        assert comp["status"] == "healthy"


def test_get_component_by_id(client, sample_component):
    response = client.get(f"/api/components/{sample_component.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_component.id
    assert "metrics" in data


def test_get_component_not_found(client):
    response = client.get("/api/components/comp-does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Component not found"


def test_create_component(client, category_id):
    payload = {
        "name": "QA Test Component",
        "category_id": category_id,
        "hostname": "qa-test.infrasense.local",
        "environment": "test",
        "criticality": "low",
        "owner": "QA Team",
    }
    response = client.post("/api/components", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "QA Test Component"
    assert data["status"] == "healthy"
    assert data["health_score"] == 100


def test_create_duplicate_component(client, category_id):
    payload = {
        "name": "Duplicate QA Component",
        "category_id": category_id,
    }
    first = client.post("/api/components", json=payload)
    assert first.status_code == 201

    second = client.post("/api/components", json=payload)
    assert second.status_code == 400
    assert "already exists" in second.json()["detail"]


def test_create_component_invalid_category(client):
    payload = {"name": "Bad Category Component", "category_id": 999999}
    response = client.post("/api/components", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid category_id"


def test_get_component_health(client):
    response = client.get("/api/components/health")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "components" in data
    assert "healthy" in data["components"]


def test_get_components_discover(client):
    response = client.get("/api/components/discover")
    assert response.status_code == 200
    data = response.json()
    assert "discovered" in data
    assert isinstance(data["discovered"], int)


def test_refresh_all_components(client):
    response = client.post("/api/components/refresh-all")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_infrastructure_summary(client):
    response = client.get("/api/components/infrastructure/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "by_type" in data
    assert "by_status" in data
    assert "by_provider" in data