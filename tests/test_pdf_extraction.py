from pathlib import Path

import pytest

from app.pdf_extraction import extract_nests_from_pdf

SAMPLES_DIR = Path(__file__).parent.parent / "Archivos de Corte"


def _read_sample(filename: str) -> bytes:
    return (SAMPLES_DIR / filename).read_bytes()


def _auth_headers(client, email="pdf-user@example.com", password="supersecret"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_single_page_nest_extracts_general_data_and_pieces():
    nests = extract_nests_from_pdf(_read_sample("Ejemplo 1.pdf"))
    assert len(nests) == 1

    nest = nests[0]
    assert nest["multiplicidad"] == 1
    assert nest["largo_mm"] == 1310.0
    assert nest["ancho_mm"] == 580.0
    assert nest["espesor_mm"] == 12.7
    assert nest["material"] == "SAE_1010"
    assert nest["tiempo_ejecucion_estimado"] == "00:26:19"
    assert nest["recortes"] == []

    assert len(nest["piezas"]) == 4
    assert nest["piezas"][0] == {"pieza": "139394-00.lsr", "descripcion": "PC 1368 (CO) X3", "cantidad": 3}
    assert nest["piezas"][2]["cantidad"] == 6


def test_multi_page_pdf_produces_one_nest_per_page():
    nests = extract_nests_from_pdf(_read_sample("Ejemplo 2.pdf"))
    assert len(nests) == 3
    assert [nest["page_index"] for nest in nests] == [1, 2, 3]
    assert [len(nest["piezas"]) for nest in nests] == [6, 5, 5]
    for nest in nests:
        assert nest["largo_mm"] == 3000.0
        assert nest["ancho_mm"] == 1500.0
        assert nest["espesor_mm"] == 0.91


def test_saved_scrap_extracts_dimensions_from_pieza_field():
    nests = extract_nests_from_pdf(_read_sample("Ejemplo 3.pdf"))
    assert len(nests) == 1

    nest = nests[0]
    assert len(nest["piezas"]) == 2
    assert len(nest["recortes"]) == 2
    assert nest["recortes"][0] == {
        "pieza": "1085.00x1500.00_RECT_SCRAP",
        "largo_mm": 1085.0,
        "ancho_mm": 1500.0,
        "cantidad": 1,
    }
    assert nest["recortes"][1]["ancho_mm"] == 559.16


@pytest.mark.parametrize("filename", ["Ejemplo 1.pdf", "Ejemplo 2.pdf", "Ejemplo 3.pdf"])
def test_extract_pdf_endpoint_returns_nests(client, filename):
    headers = _auth_headers(client)
    with (SAMPLES_DIR / filename).open("rb") as f:
        response = client.post(
            "/orders/extract-pdf",
            files={"file": (filename, f, "application/pdf")},
            headers=headers,
        )
    assert response.status_code == 200
    body = response.json()
    assert len(body["nests"]) >= 1


def test_extract_pdf_endpoint_requires_authentication(client):
    content = _read_sample("Ejemplo 1.pdf")
    response = client.post(
        "/orders/extract-pdf",
        files={"file": ("Ejemplo 1.pdf", content, "application/pdf")},
    )
    assert response.status_code == 401


def test_extract_pdf_endpoint_rejects_non_pdf_extension(client):
    headers = _auth_headers(client)
    response = client.post(
        "/orders/extract-pdf",
        files={"file": ("archivo.xlsx", b"contenido cualquiera", "application/octet-stream")},
        headers=headers,
    )
    assert response.status_code == 400


def test_extract_pdf_endpoint_rejects_corrupt_pdf(client):
    headers = _auth_headers(client)
    response = client.post(
        "/orders/extract-pdf",
        files={"file": ("archivo.pdf", b"esto no es un pdf valido", "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 400
