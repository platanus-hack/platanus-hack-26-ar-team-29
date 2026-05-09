"""ProviderConnection ORM model — see 02-4_database_schema.md."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base


class ProviderConnection(Base):
    __tablename__ = "provider_connections"
    __table_args__ = (
        CheckConstraint(
            "connection_type IN ('wallbit','ethereum')",
            name="provider_connections_type_check",
        ),
        CheckConstraint(
            "auth_kind IN ('api_key','wallet_signature','oauth')",
            name="provider_connections_auth_kind_check",
        ),
        CheckConstraint(
            "status IN ('healthy','degraded','error','revoked','pending')",
            name="provider_connections_status_check",
        ),
        Index(
            "ix_provider_connections_user_active",
            "user_id",
            postgresql_where=text("disconnected_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    connection_type: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    auth_kind: Mapped[str] = mapped_column(String, nullable=False)
    credentials_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    credentials_kid: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'v1'")
    )
    capabilities: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default=text("'{}'::text[]")
    )
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'healthy'"))
    connection_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
