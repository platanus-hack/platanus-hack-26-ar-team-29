"""ChatService — owns chat session + message lifecycle.

Persists user messages and spawns the agent task with a strong reference to
prevent GC. The agent then drives WS broadcasts and persists agent replies.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.errors import NOT_FOUND, APIError
from app.persistence.models.chat import ChatMessage
from app.persistence.repositories.chat import ChatRepository
from app.persistence.session import session_factory

if TYPE_CHECKING:
    from app.agents.chat_agent import ChatAgent
    from app.api.ws.manager import ConnectionManager

log = structlog.get_logger(__name__)


def _author_to_role(author: str) -> str:
    return {"agent": "assistant"}.get(author, author)


def _content_to_text(blocks: list[Any]) -> str:
    parts: list[str] = []
    for b in blocks or []:
        if isinstance(b, str):
            parts.append(b)
        elif isinstance(b, dict):
            t = b.get("text")
            if t:
                parts.append(str(t))
    return "".join(parts)


def _message_to_api(msg: ChatMessage) -> dict[str, Any]:
    return {
        "id": str(msg.id),
        "role": _author_to_role(msg.author),
        "content": _content_to_text(msg.content_blocks),
        "kind": msg.kind,
        "plan_id": str(msg.plan_id) if msg.plan_id else None,
        "created_at": msg.created_at.isoformat().replace("+00:00", "Z"),
    }


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        manager: ConnectionManager,
        agent: ChatAgent,
        sessionmaker: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.session = session
        self.manager = manager
        self.agent = agent
        self.sessionmaker = sessionmaker or session_factory
        self.repo = ChatRepository(session)

    async def create_session(self, user_id: UUID, title: str | None) -> dict[str, Any]:
        cs = await self.repo.create_session(user_id=user_id, title=title)
        await self.session.commit()
        return {
            "id": str(cs.id),
            "title": cs.title,
            "created_at": cs.created_at.isoformat().replace("+00:00", "Z"),
        }

    async def list_sessions(self, user_id: UUID) -> list[dict[str, Any]]:
        sessions = await self.repo.list_sessions(user_id)
        out: list[dict[str, Any]] = []
        for s in sessions:
            # Last user/assistant text message preview.
            messages = await self.repo.list_messages(session_id=s.id, user_id=user_id)
            preview: str | None = None
            for m in reversed(messages):
                if m.author in ("user", "agent") and m.kind == "text":
                    preview = _content_to_text(m.content_blocks)[:140]
                    break
            out.append(
                {
                    "id": str(s.id),
                    "title": s.title,
                    "last_message_preview": preview,
                    "updated_at": s.updated_at.isoformat().replace("+00:00", "Z"),
                }
            )
        return out

    async def list_messages(self, user_id: UUID, session_id: UUID) -> list[dict[str, Any]]:
        cs = await self.repo.get_session(session_id, user_id)
        if cs is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="Esta conversación no existe.",
                message_en="Chat session not found.",
            )
        messages = await self.repo.list_messages(session_id=session_id, user_id=user_id)
        return [
            _message_to_api(m)
            for m in messages
            if m.author in ("user", "agent", "system") and m.kind in ("text", "plan_proposal")
        ]

    async def send_user_message(
        self,
        user_id: UUID,
        session_id: UUID,
        content: str,
        agent_tasks: set[asyncio.Task] | None = None,
    ) -> dict[str, Any]:
        cs = await self.repo.get_session(session_id, user_id)
        if cs is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="Esta conversación no existe.",
                message_en="Chat session not found.",
            )
        turn_id = uuid4()
        msg = await self.repo.create_message(
            session_id=session_id,
            user_id=user_id,
            author="user",
            kind="text",
            content_blocks=[{"type": "text", "text": content}],
            turn_id=turn_id,
        )
        await self.repo.touch_session(session_id)
        await self.session.commit()

        # Spawn the agent task with a strong reference held in the module-level set.
        task = asyncio.create_task(
            self.agent.run_turn(
                session_id=session_id,
                user_id=user_id,
                turn_id=turn_id,
                user_content=content,
                sessionmaker=self.sessionmaker,
            )
        )
        if agent_tasks is not None:
            agent_tasks.add(task)
            task.add_done_callback(agent_tasks.discard)
        return {
            "message_id": str(msg.id),
            "accepted": True,
            "turn_id": str(turn_id),
        }
