"""Chat repository."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models.chat import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, user_id: UUID, title: str | None = None) -> ChatSession:
        cs = ChatSession(user_id=user_id, title=title)
        self.session.add(cs)
        await self.session.flush()
        await self.session.refresh(cs)
        return cs

    async def list_sessions(self, user_id: UUID) -> list[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.archived_at.is_(None))
            .order_by(desc(ChatSession.last_activity_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_session(self, session_id: UUID, user_id: UUID) -> ChatSession | None:
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_messages(
        self, session_id: UUID, user_id: UUID, limit: int | None = None
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_messages_recent(
        self, session_id: UUID, user_id: UUID, limit: int = 20
    ) -> list[ChatMessage]:
        """Return most recent N messages in chronological order."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        rows.reverse()
        return rows

    async def create_message(
        self,
        session_id: UUID,
        user_id: UUID,
        author: str,
        kind: str,
        content_blocks: list[Any],
        turn_id: UUID | None = None,
        plan_id: UUID | None = None,
        tool_call: dict[str, Any] | None = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            author=author,
            kind=kind,
            content_blocks=content_blocks,
            turn_id=turn_id,
            plan_id=plan_id,
            tool_call=tool_call,
        )
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def archive_session(self, session_id: UUID) -> None:
        from datetime import UTC, datetime

        from sqlalchemy import update

        await self.session.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(archived_at=datetime.now(UTC))
        )

    async def update_session_title(self, session_id: UUID, title: str) -> None:
        from sqlalchemy import update

        await self.session.execute(
            update(ChatSession).where(ChatSession.id == session_id).values(title=title)
        )

    async def touch_session(self, session_id: UUID) -> None:
        from datetime import UTC, datetime

        from sqlalchemy import update

        await self.session.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(last_activity_at=datetime.now(UTC))
        )
