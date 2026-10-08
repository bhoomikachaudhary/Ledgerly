from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings
from app.core.security import ACCESS_TOKEN_TYPE

SIGNUP_PAYLOAD = {"email": "ada@example.com", "password": "correct-horse-1", "name": "Ada"}


def test_signup_creates_user(client):
    response = client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == SIGNUP_PAYLOAD["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_duplicate_email_returns_409(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert response.status_code == 409


def test_login_with_wrong_password_returns_401(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = client.post(
        "/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_returns_token_pair(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = client.post(
        "/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_me_requires_valid_token(client):
    response = client.get("/v1/me")
    assert response.status_code in (401, 403)


def test_me_works_with_valid_access_token(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    login = client.post(
        "/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    access_token = login.json()["access_token"]

    response = client.get("/v1/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == SIGNUP_PAYLOAD["email"]


def test_me_rejects_expired_token_returns_401(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    login = client.post(
        "/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    access_token = login.json()["access_token"]
    settings = get_settings()
    unverified_sub = jwt.decode(
        access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )["sub"]

    now = datetime.now(timezone.utc)
    expired_token = jwt.encode(
        {
            "sub": unverified_sub,
            "type": ACCESS_TOKEN_TYPE,
            "iat": now - timedelta(minutes=20),
            "exp": now - timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/v1/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_refresh_rotates_token_and_rejects_reuse(client):
    client.post("/v1/auth/signup", json=SIGNUP_PAYLOAD)
    login = client.post(
        "/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    old_refresh = login.json()["refresh_token"]

    refreshed = client.post("/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != old_refresh

    reuse_attempt = client.post("/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse_attempt.status_code == 401
