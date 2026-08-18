from app.models.models import Component


def test_metrics_health(client):
    response = client.get("/api/v1/metrics/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_receive_metrics(client, db):
    component = db.query(Component).first()
    assert component is not None

    payload = {
        "metrics": [
            {
                "component_id": component.id,
                "metric_name": "cpu_usage",
                "value": 42.5,
                "unit": "%",
                "labels": {"env": "test"},
            }
        ]
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["received"] == 1
    assert data["stored"] == 1


def test_receive_metrics_rejects_null_component(client):
    payload = {
        "metrics": [
            {
                "component_id": "",
                "metric_name": "cpu_usage",
                "value": 42.5,
                "unit": "%",
            }
        ]
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == 1
    assert data["stored"] == 0


def test_receive_metrics_rejects_unknown_component(client):
    payload = {
        "metrics": [
            {
                "component_id": "comp-does-not-exist",
                "metric_name": "cpu_usage",
                "value": 42.5,
                "unit": "%",
            }
        ]
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()["stored"] == 0


def test_receive_metrics_rejects_missing_metric_name(client, db):
    component = db.query(Component).first()
    payload = {
        "metrics": [
            {
                "component_id": component.id,
                "metric_name": "",
                "value": 42.5,
                "unit": "%",
            }
        ]
    }
    response = client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 200
    assert response.json()["stored"] == 0


def test_remote_write_metrics(client, db):
    component = db.query(Component).first()
    payload = {
        "metrics": [
            {
                "component_id": component.id,
                "metric_name": "memory_usage",
                "value": 63.0,
                "unit": "%",
            }
        ]
    }
    response = client.post("/api/v1/write", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["stored"] == 1


def test_data_quality_endpoint(client):
    response = client.get("/api/v1/metrics/quality")
    assert response.status_code == 200
    data = response.json()
    assert "counters" in data
    assert "data_loss_rate_percent" in data


def test_collector_status(client):
    response = client.get("/api/v1/collector/status")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)