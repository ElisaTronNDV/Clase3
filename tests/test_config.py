def _auth_headers(client, email="config-user@example.com", password="supersecret"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_config_requires_authentication(client):
    response = client.get("/config")
    assert response.status_code == 401


def test_config_defaults_to_one_point_zero_mm(client):
    headers = _auth_headers(client)
    response = client.get("/config", headers=headers)
    assert response.status_code == 200
    assert response.json()["tolerance_mm"] == 1.0


def test_config_update_persists_new_value(client):
    headers = _auth_headers(client)
    update_response = client.put("/config", json={"tolerance_mm": 2.5}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["tolerance_mm"] == 2.5

    read_response = client.get("/config", headers=headers)
    assert read_response.json()["tolerance_mm"] == 2.5


def test_config_rejects_non_positive_tolerance(client):
    headers = _auth_headers(client)
    response = client.put("/config", json={"tolerance_mm": 0}, headers=headers)
    assert response.status_code == 422
