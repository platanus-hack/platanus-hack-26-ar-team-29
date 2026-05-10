"""Smoke: plan reject path via REST."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_plan_reject_path(sync_client: TestClient) -> None:
    sid = sync_client.post("/api/v1/chat/sessions", json={}).json()["id"]
    r = sync_client.post(
        f"/api/v1/chat/sessions/{sid}/messages",
        json={"content": "vendé 5 usd de SPY"},
    )
    assert r.status_code == 202

    plan_id: str | None = None
    for _ in range(300):
        time.sleep(0.1)
        r_get = sync_client.get(f"/api/v1/chat/sessions/{sid}/messages")
        if r_get.status_code != 200:
            print("Failed to get messages:", r_get.text)
            continue
        msgs = r_get.json()
        for m in msgs:
            if m.get("kind") == "plan_proposal" and m.get("plan_id"):
                plan_id = m["plan_id"]
                break
        if plan_id:
            break
    assert plan_id is not None, "plan was not proposed"

    rj = sync_client.post(f"/api/v1/plans/{plan_id}/reject", json={"reason": "test"})
    assert rj.status_code == 200, rj.text
    body = rj.json()
    assert body["ok"] is True
    assert body["plan_state"] == "rejected"

    again = sync_client.post(f"/api/v1/plans/{plan_id}/approve")
    assert again.status_code == 412
    assert again.json()["error"]["code"] == "PLAN_STALE"
