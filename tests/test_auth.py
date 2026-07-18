from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import ALGORITHM, SECRET_KEY


def test_register_creates_user(client):
    response = client.post("/auth/register", json={"email": "user@example.com", "password": "supersecret"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert "id" in body


def test_register_rejects_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "supersecret"})
    response = client.post("/auth/register", json={"email": "dup@example.com", "password": "othersecret"})
    assert response.status_code == 409


def test_login_with_correct_credentials_returns_token(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "supersecret"})
    response = client.post("/auth/login", json={"email": "login@example.com", "password": "supersecret"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_is_rejected(client):
    client.post("/auth/register", json={"email": "wrongpw@example.com", "password": "supersecret"})
    response = client.post("/auth/login", json={"email": "wrongpw@example.com", "password": "incorrect"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client):
    client.post("/auth/register", json={"email": "me@example.com", "password": "supersecret"})
    login_response = client.post("/auth/login", json={"email": "me@example.com", "password": "supersecret"})
    token = login_response.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_expired_token_is_rejected(client):
    client.post("/auth/register", json={"email": "expired@example.com", "password": "supersecret"})
    expired_payload = {
        "sub": "expired@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
