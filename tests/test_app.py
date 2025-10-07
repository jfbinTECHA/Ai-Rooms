import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_end_to_end_flow(client: TestClient) -> None:
    # create nomi
    nomi_resp = client.post("/api/v1/nomis", json={"name": "Echo"})
    assert nomi_resp.status_code == 201
    nomi = nomi_resp.json()
    assert nomi["name"] == "Echo"

    # create room
    room_resp = client.post("/api/v1/rooms", json={"name": "Lobby"})
    assert room_resp.status_code == 201
    room_id = room_resp.json()["id"]

    # send chat message associated with room
    chat_resp = client.post(
        f"/api/v1/nomis/{nomi['id']}/chat",
        json={"messageText": "hello there", "roomId": room_id},
    )
    assert chat_resp.status_code == 200
    message = chat_resp.json()["message"]
    assert message["roomId"] == room_id
    assert message["embedding"]

    # room history should include the nomi reply
    history_resp = client.get(f"/api/v1/rooms/{room_id}/messages")
    assert history_resp.status_code == 200
    history = history_resp.json()["messages"]
    assert len(history) == 1
    assert history[0]["id"] == message["id"]

    # broadcast a system message
    broadcast_resp = client.post(
        f"/api/v1/rooms/{room_id}/broadcast",
        json={"messageText": "Welcome!", "sender": "system"},
    )
    assert broadcast_resp.status_code == 200
    broadcast_body = broadcast_resp.json()
    assert broadcast_body["delivered"] == 0
    assert broadcast_body["message"]["text"] == "Welcome!"

    # embeddings endpoint returns deterministic length
    embed_resp = client.post("/api/v1/embeddings", json={"text": "ping"})
    assert embed_resp.status_code == 200
    vector = embed_resp.json()["embedding"]
    assert isinstance(vector, list)
    assert len(vector) == 8
