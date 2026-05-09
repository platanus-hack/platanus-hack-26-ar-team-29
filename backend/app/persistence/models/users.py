"""User ORM model — see 02-4_database_schema.md."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "primary_currency IN ('USD','ARS')",
            name="users_primary_currency_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    primary_currency: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'USD'")
    )
    locale: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'es-AR'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
