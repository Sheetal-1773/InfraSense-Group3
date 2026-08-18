from app.models.models import Prediction


def test_get_predictions(client):
    response = client.get("/api/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_predictions_filter_by_severity(client):
    response = client.get("/api/predictions", params={"severity": "high"})
    assert response.status_code == 200
    data = response.json()
    for pred in data["data"]:
        assert pred["severity"] == "high"


def test_get_active_predictions(client):
    response = client.get("/api/predictions/active")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_prediction_by_id(client, db):
    prediction = db.query(Prediction).first()
    if not prediction:
        import uuid
        from datetime import datetime
        from app.models.models import Component

        component = db.query(Component).first()
        prediction = Prediction(
            id=f"test-pred-{uuid.uuid4()}",
            component_id=component.id,
            prediction_type="Disk Usage",
            current_value=75.0,
            predicted_value=92.0,
            predicted_threshold=90.0,
            time_to_breach_minutes=120,
            confidence=85,
            severity="high",
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

    response = client.get(f"/api/predictions/{prediction.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == prediction.id
    assert "predicted_value" in data


def test_get_prediction_not_found(client):
    response = client.get("/api/predictions/pred-does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Prediction not found"


def test_run_predictions(client):
    response = client.post("/api/predictions/run")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "predictions_created" in data


def test_cleanup_predictions(client):
    response = client.post("/api/predictions/cleanup")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_generate_predictions_from_sources(client):
    response = client.get("/api/predictions/generate")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "summary" in data