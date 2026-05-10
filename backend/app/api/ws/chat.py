"""WebSocket route for chat session subscriptions."""

from __future__ import annotations

import asyncio
from uuid import UUID

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.api.deps import DEV_TOKEN_PREFIX, parse_dev_user_token
from app.common.errors import APIError
from app.persistence.repositories.chat import ChatRepository
from app.persistence.session import session_factory

log = structlog.get_logger(__name__)

router = APIRouter()


def _websocket_token(websocket: WebSocket, token: str | None) -> str | None:
    if token:
        return token
    protocols = websocket.headers.get("sec-websocket-protocol", "")
    for protocol in protocols.split(","):
        value = protocol.strip()
        if value.startswith(DEV_TOKEN_PREFIX):
            return value
    return None


@router.websocket("/ws")
async def chat_ws(
    websocket: WebSocket,
    session_id: UUID = Query(...),
    token: str | None = Query(default=None),
) -> None:
    try:
        user_id = parse_dev_user_token(_websocket_token(websocket, token))
    except APIError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with session_factory() as db:
        repo = ChatRepository(db)
        if await repo.get_session(session_id, user_id) is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    manager = websocket.app.state.connection_manager
    await websocket.accept()
    await manager.subscribe(session_id, websocket)
    await websocket.send_json({"type": "subscribed", "session_id": str(session_id)})
    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=45.0)
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
