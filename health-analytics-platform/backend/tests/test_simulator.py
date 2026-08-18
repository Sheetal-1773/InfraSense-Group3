def test_get_simulator_status(client):
    response = client.get("/api/simulator/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data


def test_get_available_scenarios(client):
    response = client.get("/api/simulator/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) > 0


def test_set_valid_scenario(client):
    response = client.post("/api/simulator/scenario", json={"scenario": "cpu_spike"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["scenario"] == "cpu_spike"


def test_set_normal_scenario(client):
    response = client.post("/api/simulator/scenario", json={"scenario": "normal"})
    assert response.status_code == 200
    assert response.json()["scenario"] == "normal"


def test_set_invalid_scenario(client):
    response = client.post("/api/simulator/scenario", json={"scenario": "not-a-real-scenario"})
    assert response.status_code == 400
    assert "Invalid scenario" in response.json()["detail"]


def test_reset_simulator(client):
    response = client.post("/api/simulator/reset")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_simulator_components(client):
    response = client.get("/api/simulator/components")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "components" in data
        assert "count" in data