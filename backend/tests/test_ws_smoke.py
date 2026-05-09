"""Smoke: WebSocket subscription + ping/pong + plan_proposed broadcast."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_ws_subscribe_and_ping_pong(sync_client: TestClient) -> None:
    sid = sync_client.post("/api/v1/chat/sessions", json={}).json()["id"]
    with sync_client.websocket_connect(f"/api/v1/ws?session_id={sid}") as ws:
        first = ws.receive_json()
        assert first["type"] == "subscribed"
        assert first["session_id"] == sid

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"


def test_ws_streams_plan_for_buy_intent(sync_client: TestClient) -> None:
    sid = sync_client.post("/api/v1/chat/sessions", json={}).json()["id"]
    with sync_client.websocket_connect(f"/api/v1/ws?session_id={sid}") as ws:
        first = ws.receive_json()
        assert first["type"] == "subscribed"

        sync_client.post(
            f"/api/v1/chat/sessions/{sid}/messages",
            json={"content": "comprá 7 usd de apple"},
        )

        types: list[str] = []
        for _ in range(80):
            try:
                frame = ws.receive_json()
            except Exception:
                break
            t = frame.get("type")
            types.append(t)
            if t == "turn_complete":
                break
        assert "plan_proposed" in types
        assert "turn_complete" in types
