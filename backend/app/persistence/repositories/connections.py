"""Provider connection repository."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models.connections import ProviderConnection


class ConnectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_wallbit(
        self,
        user_id: UUID,
        label: str | None,
        credentials_encrypted: bytes,
        capabilities: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> ProviderConnection:
        conn = ProviderConnection(
            user_id=user_id,
            connection_type="wallbit",
            label=label,
            auth_kind="api_key",
            credentials_encrypted=credentials_encrypted,
            capabilities=capabilities,
            status="healthy",
            connection_metadata=metadata or {},
        )
        self.session.add(conn)
        await self.session.flush()
        await self.session.refresh(conn)
        return conn

    async def get_active_wallbit(self, user_id: UUID) -> ProviderConnection | None:
        stmt = (
            select(ProviderConnection)
            .where(ProviderConnection.user_id == user_id)
            .where(ProviderConnection.connection_type == "wallbit")
            .where(ProviderConnection.disconnected_at.is_(None))
            .order_by(ProviderConnection.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[ProviderConnection]:
        stmt = (
            select(ProviderConnection)
            .where(ProviderConnection.user_id == user_id)
            .where(ProviderConnection.disconnected_at.is_(None))
            .order_by(ProviderConnection.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, connection_id: UUID, user_id: UUID) -> ProviderConnection | None:
        stmt = select(ProviderConnection).where(
            ProviderConnection.id == connection_id,
            ProviderConnection.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_ethereum_custodial(
        self,
        user_id: UUID,
        label: str | None,
        credentials_encrypted: bytes,
        capabilities: list[str],
        metadata: dict[str, Any],
    ) -> ProviderConnection:
        conn = ProviderConnection(
            user_id=user_id,
            connection_type="ethereum_custodial",
            label=label,
            auth_kind="private_key",
            credentials_encrypted=credentials_encrypted,
            capabilities=capabilities,
            status="healthy",
            connection_metadata=metadata,
        )
        self.session.add(conn)
        await self.session.flush()
        await self.session.refresh(conn)
        return conn

    async def get_active_ethereum_custodial(
        self, connection_id: UUID, user_id: UUID
    ) -> ProviderConnection | None:
        stmt = (
            select(ProviderConnection)
            .where(ProviderConnection.id == connection_id)
            .where(ProviderConnection.user_id == user_id)
            .where(ProviderConnection.connection_type == "ethereum_custodial")
            .where(ProviderConnection.disconnected_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
