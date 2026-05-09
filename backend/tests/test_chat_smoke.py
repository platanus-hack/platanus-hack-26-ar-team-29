"""Smoke: chat REST shape."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_and_list_sessions(sync_client: TestClient) -> None:
    r = sync_client.post("/api/v1/chat/sessions", json={"title": "ahorro 2026"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "id" in body and "created_at" in body
    sid = body["id"]

    r2 = sync_client.get("/api/v1/chat/sessions")
    assert r2.status_code == 200
    sessions = r2.json()
    assert any(s["id"] == sid for s in sessions)
    one = next(s for s in sessions if s["id"] == sid)
    assert "title" in one
    assert "last_message_preview" in one
    assert "updated_at" in one

    r3 = sync_client.get(f"/api/v1/chat/sessions/{sid}/messages")
    assert r3.status_code == 200
    assert r3.json() == []
