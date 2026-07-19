from io import BytesIO

from PIL import Image
from pyzbar.pyzbar import decode as zbar_decode


def _auth_headers(client, email="orders-user@example.com", password="supersecret"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _sample_order(**overrides):
    order = {
        "nombre_nest": "BOUNOUS_SAE_12,7_06-07-26.lnt",
        "material": "SAE_1010",
        "thickness_mm": 2.1,
        "length_mm": 3000,
        "width_mm": 1500,
        "multiplicidad": 2,
        "tiempo_ejecucion_estimado": "00:26:19",
        "piezas": [{"pieza": "139394-00.lsr", "descripcion": "PC 1368 (CO) X3", "cantidad": 3}],
        "recortes": [],
    }
    order.update(overrides)
    return order


def test_confirm_order_requires_authentication(client):
    response = client.post("/orders", json=_sample_order())
    assert response.status_code == 401


def test_confirm_order_warns_when_product_does_not_exist(client):
    headers = _auth_headers(client)
    response = client.post("/orders", json=_sample_order(), headers=headers)
    assert response.status_code == 409
    body = response.json()["detail"]
    assert body["code"] == "product_not_found"
    assert body["material"] == "SAE_1010"


def test_confirm_order_with_create_missing_product_creates_it_with_zero_stock(client):
    headers = _auth_headers(client)
    response = client.post(
        "/orders", json=_sample_order(create_missing_product=True), headers=headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "vigente"
    assert body["nest_code"].startswith("NEST-")

    products = client.get("/products", headers=headers).json()
    assert len(products) == 1
    assert products[0]["stock"] == 0
    assert products[0]["committed_stock"] == 2  # multiplicidad


def test_confirm_order_matches_existing_product_within_tolerance_and_commits_stock(client):
    headers = _auth_headers(client)
    client.post(
        "/products",
        json={
            "material": "SAE_1010",
            "thickness_mm": 2.1,
            "length_mm": 3000.4,
            "width_mm": 1500.4,
            "stock": 10,
            "reorder_point": 3,
        },
        headers=headers,
    )

    response = client.post("/orders", json=_sample_order(multiplicidad=4), headers=headers)
    assert response.status_code == 201
    assert response.json()["low_stock_warning"] is False

    products = client.get("/products", headers=headers).json()
    assert products[0]["committed_stock"] == 4


def test_confirm_order_outside_tolerance_does_not_match(client):
    headers = _auth_headers(client)
    client.post(
        "/products",
        json={
            "material": "SAE_1010",
            "thickness_mm": 2.1,
            "length_mm": 3010,
            "width_mm": 1500,
            "stock": 10,
            "reorder_point": 3,
        },
        headers=headers,
    )

    response = client.post("/orders", json=_sample_order(), headers=headers)
    assert response.status_code == 409


def test_confirm_order_raises_low_stock_warning_at_reorder_point(client):
    headers = _auth_headers(client)
    client.post(
        "/products",
        json={
            "material": "SAE_1010",
            "thickness_mm": 2.1,
            "length_mm": 3000,
            "width_mm": 1500,
            "stock": 10,
            "reorder_point": 8,
        },
        headers=headers,
    )

    response = client.post("/orders", json=_sample_order(multiplicidad=5), headers=headers)
    assert response.status_code == 201
    assert response.json()["low_stock_warning"] is True


def test_confirmed_orders_get_sequential_nest_codes(client):
    headers = _auth_headers(client)
    first = client.post("/orders", json=_sample_order(create_missing_product=True), headers=headers).json()
    second = client.post(
        "/orders", json=_sample_order(width_mm=1000, create_missing_product=True), headers=headers
    ).json()
    assert first["nest_code"] != second["nest_code"]
    assert int(second["nest_code"].split("-")[1]) > int(first["nest_code"].split("-")[1])


def test_confirm_order_persists_pieces_and_scraps(client):
    headers = _auth_headers(client)
    order_payload = _sample_order(
        create_missing_product=True,
        recortes=[{"pieza": "800.00x400.00_RECT_SCRAP", "largo_mm": 800, "ancho_mm": 400, "cantidad": 1}],
    )
    response = client.post("/orders", json=order_payload, headers=headers)
    body = response.json()
    assert len(body["piezas"]) == 1
    assert body["piezas"][0]["pieza"] == "139394-00.lsr"
    assert len(body["recortes"]) == 1
    assert body["recortes"][0]["largo_mm"] == 800


def test_get_order_not_found_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/orders/999", headers=headers)
    assert response.status_code == 404


def test_order_barcode_is_decodable_and_matches_nest_code(client):
    headers = _auth_headers(client)
    order = client.post(
        "/orders", json=_sample_order(create_missing_product=True), headers=headers
    ).json()

    response = client.get(f"/orders/{order['id']}/barcode", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    image = Image.open(BytesIO(response.content))
    decoded_values = [result.data.decode("utf-8") for result in zbar_decode(image)]
    assert order["nest_code"] in decoded_values


def test_order_barcode_requires_authentication(client):
    response = client.get("/orders/1/barcode")
    assert response.status_code == 401


def test_read_order_by_nest_code_returns_order(client):
    headers = _auth_headers(client)
    order = client.post(
        "/orders", json=_sample_order(create_missing_product=True), headers=headers
    ).json()

    response = client.get(f"/orders/by-nest-code/{order['nest_code']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_read_order_by_nest_code_not_found_returns_404(client):
    headers = _auth_headers(client)
    response = client.get("/orders/by-nest-code/NEST-999999", headers=headers)
    assert response.status_code == 404


def test_close_order_discounts_stock_and_committed_stock(client):
    headers = _auth_headers(client)
    client.post(
        "/products",
        json={
            "material": "SAE_1010",
            "thickness_mm": 2.1,
            "length_mm": 3000,
            "width_mm": 1500,
            "stock": 10,
            "reorder_point": 3,
        },
        headers=headers,
    )
    order = client.post("/orders", json=_sample_order(multiplicidad=4), headers=headers).json()

    response = client.post(f"/orders/{order['id']}/close", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cerrada"

    products = client.get("/products", headers=headers).json()
    assert products[0]["stock"] == 6
    assert products[0]["committed_stock"] == 0


def test_close_order_twice_returns_409(client):
    headers = _auth_headers(client)
    order = client.post(
        "/orders", json=_sample_order(create_missing_product=True), headers=headers
    ).json()

    first = client.post(f"/orders/{order['id']}/close", headers=headers)
    assert first.status_code == 200

    second = client.post(f"/orders/{order['id']}/close", headers=headers)
    assert second.status_code == 409


def test_close_order_not_found_returns_404(client):
    headers = _auth_headers(client)
    response = client.post("/orders/999/close", headers=headers)
    assert response.status_code == 404


def test_close_order_creates_new_product_for_unmatched_scrap(client):
    headers = _auth_headers(client)
    order_payload = _sample_order(
        create_missing_product=True,
        recortes=[{"pieza": "800.00x400.00_RECT_SCRAP", "largo_mm": 800, "ancho_mm": 400, "cantidad": 3}],
    )
    order = client.post("/orders", json=order_payload, headers=headers).json()

    response = client.post(f"/orders/{order['id']}/close", headers=headers)
    assert response.status_code == 200

    products = client.get("/products", headers=headers).json()
    scrap_product = next(p for p in products if p["length_mm"] == 800)
    assert scrap_product["stock"] == 3
    assert scrap_product["committed_stock"] == 0


def test_close_order_increments_existing_matching_scrap_product(client):
    headers = _auth_headers(client)
    client.post(
        "/products",
        json={
            "material": "SAE_1010",
            "thickness_mm": 2.1,
            "length_mm": 800.3,
            "width_mm": 400.3,
            "stock": 5,
            "reorder_point": 0,
        },
        headers=headers,
    )
    order_payload = _sample_order(
        create_missing_product=True,
        recortes=[{"pieza": "800.00x400.00_RECT_SCRAP", "largo_mm": 800, "ancho_mm": 400, "cantidad": 3}],
    )
    order = client.post("/orders", json=order_payload, headers=headers).json()

    response = client.post(f"/orders/{order['id']}/close", headers=headers)
    assert response.status_code == 200

    products = client.get("/products", headers=headers).json()
    scrap_product = next(p for p in products if p["length_mm"] == 800.3)
    assert scrap_product["stock"] == 8
