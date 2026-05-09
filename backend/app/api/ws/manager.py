"""In-process WebSocket connection manager."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import structlog
from fastapi import WebSocket

log = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._sessions: dict[UUID, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, session_id: UUID, ws: WebSocket) -> None:
        async with self._lock:
            self._sessions.setdefault(session_id, set()).add(ws)

    async def unsubscribe(self, session_id: UUID, ws: WebSocket) -> None:
        async with self._lock:
            sockets = self._sessions.get(session_id)
            if sockets is None:
                return
            sockets.discard(ws)
            if not sockets:
                self._sessions.pop(session_id, None)

    async def broadcast_to_session(self, session_id: UUID, frame: dict[str, Any]) -> None:
        async with self._lock:
            sockets = list(self._sessions.get(session_id, set()))
        if not sockets:
            return
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(frame)
            except Exception as exc:
                log.warning(
                    "ws_send_failed",
                    session_id=str(session_id),
                    error=str(exc),
                )
                dead.append(ws)
        if dead:
            async with self._lock:
                sockets_set = self._sessions.get(session_id)
                if sockets_set is not None:
                    for ws in dead:
                        sockets_set.discard(ws)
                    if not sockets_set:
                        self._sessions.pop(session_id, None)
