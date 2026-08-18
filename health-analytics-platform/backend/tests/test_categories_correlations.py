def test_get_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for cat in data:
        assert "name" in cat
        assert "type" in cat


def test_get_category_by_id(client, db):
    from app.models.models import Category

    category = db.query(Category).first()
    assert category is not None

    response = client.get(f"/api/categories/{category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category.id
    assert data["name"] == category.name


def test_get_correlations(client):
    response = client.get("/api/correlations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_correlations_topology(client):
    response = client.get("/api/correlations/topology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


def test_get_ranked_root_causes(client):
    response = client.get("/api/correlations/ranked/root-cause")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)