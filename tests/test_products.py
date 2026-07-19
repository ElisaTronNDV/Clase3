def _auth_headers(client, email="products-user@example.com", password="supersecret"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _sample_product(**overrides):
    product = {
        "material": "SAE_1010",
        "thickness_mm": 2.1,
        "length_mm": 3000,
        "width_mm": 1500,
        "stock": 10,
        "reorder_point": 5,
    }
    product.update(overrides)
    return product


def test_list_products_requires_authentication(client):
    response = client.get("/products")
    assert response.status_code == 401


def test_create_product_succeeds(client):
    headers = _auth_headers(client)
    response = client.post("/products", json=_sample_product(), headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["material"] == "SAE_1010"
    assert body["committed_stock"] == 0
    assert "id" in body


def test_create_product_rejects_exact_duplicate(client):
    headers = _auth_headers(client)
    client.post("/products", json=_sample_product(), headers=headers)
    response = client.post("/products", json=_sample_product(), headers=headers)
    assert response.status_code == 409


def test_create_product_allows_different_dimensions(client):
    headers = _auth_headers(client)
    client.post("/products", json=_sample_product(), headers=headers)
    response = client.post("/products", json=_sample_product(length_mm=2500), headers=headers)
    assert response.status_code == 201


def test_create_product_rejects_missing_required_field(client):
    headers = _auth_headers(client)
    incomplete = _sample_product()
    del incomplete["material"]
    response = client.post("/products", json=incomplete, headers=headers)
    assert response.status_code == 422


def test_created_products_get_sequential_ids(client):
    headers = _auth_headers(client)
    first = client.post("/products", json=_sample_product(), headers=headers).json()
    second = client.post("/products", json=_sample_product(length_mm=2500), headers=headers).json()
    assert second["id"] > first["id"]


def test_list_products_returns_all(client):
    headers = _auth_headers(client)
    client.post("/products", json=_sample_product(), headers=headers)
    client.post("/products", json=_sample_product(length_mm=2500), headers=headers)
    response = client.get("/products", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_product_persists_allowed_fields(client):
    headers = _auth_headers(client)
    created = client.post("/products", json=_sample_product(), headers=headers).json()

    update_response = client.put(
        f"/products/{created['id']}",
        json=_sample_product(reorder_point=20),
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["reorder_point"] == 20

    read_response = client.get(f"/products/{created['id']}", headers=headers)
    assert read_response.json()["reorder_point"] == 20


def test_update_product_ignores_committed_stock_in_payload(client):
    headers = _auth_headers(client)
    created = client.post("/products", json=_sample_product(), headers=headers).json()
    assert created["committed_stock"] == 0

    payload = _sample_product()
    payload["committed_stock"] = 99
    update_response = client.put(f"/products/{created['id']}", json=payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["committed_stock"] == 0
