"""Smoke: WebSocket subscription + ping/pong + plan_proposed broadcast."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import DEV_WS_TOKEN


def test_ws_subscribe_and_ping_pong(sync_client: TestClient) -> None:
    sid = sync_client.post("/api/v1/chat/sessions", json={}).json()["id"]
    with sync_client.websocket_connect(f"/api/v1/ws?session_id={sid}&token={DEV_WS_TOKEN}") as ws:
        first = ws.receive_json()
        assert first["type"] == "subscribed"
        assert first["session_id"] == sid

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"


def test_ws_streams_plan_for_buy_intent(sync_client: TestClient) -> None:
    sid = sync_client.post("/api/v1/chat/sessions", json={}).json()["id"]
    with sync_client.websocket_connect(f"/api/v1/ws?session_id={sid}&token={DEV_WS_TOKEN}") as ws:
        first = ws.receive_json()
        assert first["type"] == "subscribed"

        sync_client.post(
            f"/api/v1/chat/sessions/{sid}/messages",
            json={"content": "comprá 7 usd de apple"},
        )

        types: list[str] = []
        plan_id: str | None = None
        for _ in range(300):
            try:
                frame = ws.receive_json()
            except Exception:
                break
            t = frame.get("type")
            types.append(t)
            if t == "plan_proposed":
                plan_id = frame.get("plan_id")
                # Reject the plan so the agent can finish the turn
                sync_client.post(f"/api/v1/plans/{plan_id}/reject", json={"reason": "test"})
            if t == "turn_complete":
                break
        assert "plan_proposed" in types
        assert "turn_complete" in types
