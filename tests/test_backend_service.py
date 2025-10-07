import pytest
from fastapi.testclient import TestClient

from backend.backend_service import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app(database_url="sqlite:///:memory:")
    with TestClient(app) as test_client:
        yield test_client


def authenticated_client(client: TestClient) -> tuple[TestClient, str]:
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "user@example.com", "password": "secret", "display_name": "User"},
    )
    assert signup_resp.status_code == 201
    signup_token = signup_resp.json()["access_token"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "secret"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token != ""
    return client, token


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_full_backend_flow(client: TestClient) -> None:
    client, token = authenticated_client(client)

    nomi_resp = client.post(
        "/api/v1/nomis",
        json={"name": "Eve", "persona": {"mood": "cheerful"}},
        headers=auth_headers(token),
    )
    assert nomi_resp.status_code == 201
    nomi_id = nomi_resp.json()["id"]

    room_resp = client.post(
        "/api/v1/rooms",
        json={"name": "General", "is_group": True},
        headers=auth_headers(token),
    )
    assert room_resp.status_code == 201
    room_id = room_resp.json()["id"]

    message_resp = client.post(
        f"/api/v1/rooms/{room_id}/messages",
        json={"text": "Hello team"},
        headers=auth_headers(token),
    )
    assert message_resp.status_code == 201
    message_id = message_resp.json()["id"]

    history_resp = client.get(
        f"/api/v1/rooms/{room_id}/messages",
        headers=auth_headers(token),
    )
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert isinstance(history, list)
    assert history[0]["id"] == message_id

    chat_resp = client.post(
        f"/api/v1/nomis/{nomi_id}/chat",
        json={"message": "How are you?"},
        headers=auth_headers(token),
    )
    assert chat_resp.status_code == 200
    assert "reply" in chat_resp.json()

    embed_resp = client.post(
        "/api/v1/embeddings",
        json={"text": "hello world"},
        headers=auth_headers(token),
    )
    assert embed_resp.status_code == 201
    embedding_id = embed_resp.json()["id"]

    search_resp = client.get(
        "/api/v1/search",
        params={"query": "hello", "k": 5},
        headers=auth_headers(token),
    )
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert any(result["id"] == embedding_id for result in results)

    usage_resp = client.get("/api/v1/usage", headers=auth_headers(token))
    assert usage_resp.status_code == 200
    usage = usage_resp.json()["usage"]
    assert usage


def test_requires_auth(client: TestClient) -> None:
    # Ensure a protected endpoint rejects missing credentials
    resp = client.get("/api/v1/rooms")
    assert resp.status_code == 401

    _, token = authenticated_client(client)
    authed_resp = client.get("/api/v1/rooms", headers=auth_headers(token))
    assert authed_resp.status_code == 200
