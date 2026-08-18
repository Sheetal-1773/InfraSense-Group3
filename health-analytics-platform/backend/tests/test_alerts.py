from app.models.models import Alert, Component


def test_get_alerts(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_alerts_filter_by_severity(client):
    response = client.get("/api/alerts", params={"severity": "critical"})
    assert response.status_code == 200
    data = response.json()
    for alert in data["data"]:
        assert alert["severity"] == "critical"


def test_get_alerts_filter_by_status(client):
    response = client.get("/api/alerts", params={"status": "open"})
    assert response.status_code == 200
    data = response.json()
    for alert in data["data"]:
        assert alert["status"] == "open"


def test_get_active_alerts(client):
    response = client.get("/api/alerts/active")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_predictive_alerts(client):
    response = client.get("/api/alerts/predictive")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_alert_by_id(client, db):
    alert = db.query(Alert).first()
    assert alert is not None, "No seeded alerts available"

    response = client.get(f"/api/alerts/{alert.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert.id
    assert "title" in data
    assert "severity" in data


def test_get_alert_not_found(client):
    response = client.get("/api/alerts/alert-does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


def test_acknowledge_alert(client, db):
    alert = db.query(Alert).filter(Alert.status == "open").first()
    if not alert:
        import uuid
        from datetime import datetime
        from app.models.models import Component

        component = db.query(Component).first()
        alert = Alert(
            id=f"test-alert-{uuid.uuid4()}",
            component_id=component.id,
            alert_type="reactive",
            severity="warning",
            title="Test Alert",
            description="Test description",
            status="open",
            acknowledged=False,
            created_at=datetime.utcnow(),
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

    response = client.post(f"/api/alerts/{alert.id}/acknowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["acknowledged"] is True


def test_resolve_alert(client, db):
    import uuid
    from datetime import datetime
    from app.models.models import Component

    component = db.query(Component).first()
    alert = Alert(
        id=f"test-resolve-{uuid.uuid4()}",
        component_id=component.id,
        alert_type="reactive",
        severity="warning",
        title="Resolve Test Alert",
        description="Test description",
        status="acknowledged",
        acknowledged=True,
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    response = client.post(f"/api/alerts/{alert.id}/resolve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None


def test_generate_alerts_from_sources(client):
    response = client.get("/api/alerts/generate")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "summary" in data


def test_acknowledge_dynamic_alert_fallback(client, monkeypatch, db):
    """
    Acknowledge should persist a dynamic (non-DB) alert so the button works.
    """
    from app.routers import alerts as alerts_router
    from app.models.models import Component

    component = db.query(Component).first()
    assert component is not None

    monkeypatch.setattr(alerts_router, "_find_dynamic_alert", lambda alert_id: {
        "id": alert_id,
        "component_id": component.id,
        "severity": "warning",
        "title": "Dynamic Fallback Alert",
        "description": "Test dynamic fallback",
        "status": "active",
    })

    response = client.post("/api/alerts/test-dynamic-ack-id/acknowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["acknowledged"] is True


def test_resolve_dynamic_alert_fallback(client, monkeypatch, db):
    """
    Resolve should persist a dynamic (non-DB) alert so the button works.
    """
    from app.routers import alerts as alerts_router
    from app.models.models import Component

    component = db.query(Component).first()
    assert component is not None

    monkeypatch.setattr(alerts_router, "_find_dynamic_alert", lambda alert_id: {
        "id": alert_id,
        "component_id": component.id,
        "severity": "warning",
        "title": "Dynamic Fallback Alert",
        "description": "Test dynamic fallback",
        "status": "active",
    })

    response = client.post("/api/alerts/test-dynamic-resolve-id/resolve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None