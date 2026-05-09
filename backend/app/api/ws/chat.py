"""WebSocket route for chat session subscriptions."""

from __future__ import annotations

import asyncio
from uuid import UUID

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

log = structlog.get_logger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def chat_ws(
    websocket: WebSocket,
    session_id: UUID = Query(...),
    token: str | None = Query(default=None),  # ignored in dev
) -> None:
    manager = websocket.app.state.connection_manager
    await websocket.accept()
    await manager.subscribe(session_id, websocket)
    await websocket.send_json({"type": "subscribed", "session_id": str(session_id)})
    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=60.0)
            except TimeoutError:
                # Keepalive ping from server side.
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                continue
            mtype = msg.get("type") if isinstance(msg, dict) else None
            if mtype == "ping":
                await websocket.send_json({"type": "pong"})
            elif mtype in ("subscribe_session", "unsubscribe_session"):
                # noop in v1
                pass
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "code": "INVALID_REQUEST",
                        "message_es": "Tipo de mensaje no soportado.",
                        "message_en": "Unsupported frame type.",
                    }
                )
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        log.warning("ws_loop_error", error=str(exc), session_id=str(session_id))
    finally:
        await manager.unsubscribe(session_id, websocket)
